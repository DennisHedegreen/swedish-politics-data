from __future__ import annotations

import pandas as pd
import streamlit as st

from core.correlation import compute_correlation_result, corr_strength_label
from core.data_variants import resolve_sweden_public_path
from core.failure_states import describe_public_data_state, summarize_public_data_state
from core.presentation import (
    PARTY_NAME_MODES,
    build_country_finding,
    format_display_table,
    format_party_name,
    format_status_label,
    get_factor_status,
    render_bar_chart,
    render_compact_dataframe,
    render_country_sidebar_footer,
    render_national_trend_chart,
    render_profile_cards,
)
from country_registry import BASE_FACTOR_CATALOG


SWEDEN_INTERNAL_FACTOR_CATALOG: dict[str, dict[str, str]] = {}


def sweden_public_path(relative_path, variant=None):
    active_variant = "" if variant is None else variant
    return resolve_sweden_public_path(relative_path, active_variant)


@st.cache_data
def load_sweden_municipal(variant=""):
    path = sweden_public_path("riksdag/riksdag_party_share_by_municipality.csv", variant)
    if not path.exists():
        return pd.DataFrame(columns=["party", "municipality", "public_geography_id", "year", "share"])
    df = pd.read_csv(path)
    df["year"] = df["election_year"].astype(int)
    df["share"] = df["share"].astype(float)
    excluded_rows = {
        "Valdeltagande",
        "Summa giltiga röster",
        "blanka röster",
        "övriga ogiltiga",
        "övriga anmälda partier",
        "ej anmält deltagande",
        "totalsumma",
        "Totalsumma",
    }
    df = df[~df["party"].isin(excluded_rows)].copy()
    return df[["party", "municipality", "public_geography_id", "year", "share"]]


@st.cache_data
def load_sweden_national(variant=""):
    path = sweden_public_path("riksdag/riksdag_national_vote_share.csv", variant)
    if not path.exists():
        return pd.DataFrame(columns=["party", "election_year", "share", "mandates"])
    df = pd.read_csv(path)
    df["election_year"] = df["election_year"].astype(int)
    df["share"] = df["share"].astype(float)
    if "mandates" in df.columns:
        df["mandates"] = df["mandates"].astype(int)
    return df


@st.cache_data
def load_sweden_factor_file(filename, variant="", data_dir="factors"):
    path = sweden_public_path(f"{data_dir}/{filename}", variant)
    if not path.exists():
        return pd.DataFrame(columns=["municipality", "public_geography_id", "year", "value", "comparability_status"])
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    if "comparability_status" not in df.columns and "harvest_status" in df.columns:
        df["comparability_status"] = df["harvest_status"]
    return df


def get_sweden_factor_catalog(country_config, runtime_context):
    catalog = {key: BASE_FACTOR_CATALOG[key] for key in country_config.supported_factors}
    if runtime_context.profile.allow_internal:
        for key, spec in SWEDEN_INTERNAL_FACTOR_CATALOG.items():
            source_path = sweden_public_path(f"{spec.get('data_dir', 'factors')}/{spec['filename']}", runtime_context.data_variant)
            if source_path.exists():
                catalog[key] = spec
    return catalog


def load_bundle(country_config, runtime_context):
    factor_catalog = get_sweden_factor_catalog(country_config, runtime_context)
    factor_frames = {
        spec["filename"]: load_sweden_factor_file(
            spec["filename"],
            runtime_context.data_variant,
            spec.get("data_dir", "factors"),
        )
        for spec in factor_catalog.values()
    }
    return {
        "municipal": load_sweden_municipal(runtime_context.data_variant),
        "national": load_sweden_national(runtime_context.data_variant),
        "factor_frames": factor_frames,
        "factor_catalog": factor_catalog,
    }


def get_sweden_metric_series(metric_key, year, factor_frames, factor_catalog):
    filename = factor_catalog[metric_key]["filename"]
    df = factor_frames[filename]
    if df.empty:
        return pd.DataFrame(columns=["municipality", "metric"])
    frame = df[df["year"] == year][["municipality", "value"]].copy()
    frame["metric"] = frame["value"]
    return frame[["municipality", "metric"]]


def get_sweden_party_profiles(municipal_df):
    if municipal_df.empty:
        return pd.DataFrame(columns=["party", "municipality_count", "mean_share", "default_public"])
    stats = (
        municipal_df[municipal_df["share"] > 0]
        .groupby("party", as_index=False)
        .agg(
            municipality_count=("municipality", "nunique"),
            mean_share=("share", "mean"),
        )
    )
    stats["default_public"] = (
        (stats["municipality_count"] >= 25) &
        (stats["mean_share"] >= 0.5)
    )
    return stats.sort_values(["default_public", "mean_share", "municipality_count"], ascending=[False, False, False]).reset_index(drop=True)


def sweden_variant_is_ready(runtime_context):
    if not runtime_context.data_variant:
        return True
    municipal_path = sweden_public_path("riksdag/riksdag_party_share_by_municipality.csv", runtime_context.data_variant)
    if not municipal_path.exists():
        return False
    try:
        municipal_df = pd.read_csv(municipal_path)
    except Exception:
        return False
    if municipal_df.empty:
        return False

    factor_dir = sweden_public_path("factors", runtime_context.data_variant)
    if not factor_dir.exists():
        return False
    factor_files = list(factor_dir.glob("*.csv"))
    if not factor_files:
        return False
    factor_frames = []
    for factor_file in factor_files:
        try:
            factor_frames.append(pd.read_csv(factor_file))
        except Exception:
            factor_frames.append(pd.DataFrame())
    return any(not frame.empty for frame in factor_frames)


def is_available(country_config, runtime_context):
    return sweden_variant_is_ready(runtime_context)


def top_national_parties(national_df, top_n=5):
    if national_df.empty:
        return []
    year_col = "election_year" if "election_year" in national_df.columns else "year"
    latest_year = int(national_df[year_col].max())
    latest = national_df[national_df[year_col] == latest_year].copy()
    latest["share"] = pd.to_numeric(latest["share"], errors="coerce")
    latest = latest.dropna(subset=["share"]).sort_values("share", ascending=False)
    return latest["party"].head(top_n).tolist()


def ordered_national_parties(national_df):
    if national_df.empty:
        return []
    year_col = "election_year" if "election_year" in national_df.columns else "year"
    latest_year = int(national_df[year_col].max())
    latest = national_df[national_df[year_col] == latest_year].copy()
    latest["share"] = pd.to_numeric(latest["share"], errors="coerce")
    latest = latest.dropna(subset=["share"]).sort_values("share", ascending=False)
    ordered = latest["party"].tolist()
    remainder = sorted([party for party in national_df["party"].dropna().unique().tolist() if party not in ordered])
    return ordered + remainder


def ordered_sweden_parties_for_year(municipal_df, year):
    year_frame = municipal_df[municipal_df["year"] == year].copy()
    if year_frame.empty:
        return []
    profiles = get_sweden_party_profiles(year_frame)
    ordered = profiles["party"].tolist()
    remainder = sorted([party for party in year_frame["party"].dropna().unique().tolist() if party not in ordered])
    return ordered + remainder


def render(country_config, selected_country_label, runtime_context):
    bundle = load_bundle(country_config, runtime_context)
    factor_frames = bundle["factor_frames"]
    factor_catalog = bundle["factor_catalog"]
    mun = bundle["municipal"]
    nat = bundle["national"]
    data_state = summarize_public_data_state(municipal_df=mun, national_df=nat, factor_frames=factor_frames)
    sweden_years = sorted(mun["year"].unique().tolist())
    available_municipalities = sorted(mun["municipality"].unique())
    metric_options = [factor_catalog[key] | {"key": key} for key in factor_catalog]
    latest_sweden_year = sweden_years[-1] if sweden_years else None
    latest_year_votes = mun[mun["year"] == latest_sweden_year].copy() if latest_sweden_year is not None else mun.iloc[0:0].copy()
    latest_party_profiles = get_sweden_party_profiles(latest_year_votes)
    latest_default_public_parties = latest_party_profiles.loc[
        latest_party_profiles["default_public"], "party"
    ].tolist()

    with st.sidebar:
        st.markdown('<div class="hr-wordmark">HEDEGREEN RESEARCH<span class="dot"> ●</span></div>', unsafe_allow_html=True)
        st.markdown(f"**{country_config.adjective} Politics Data**")
        st.markdown(
            "<p style='font-size:0.75rem;color:#6a6a7a;line-height:1.6;margin-top:0.3rem;'>"
            "National vote trends 2002–2022. Municipality-level public reading for Riksdag 2014, 2018, and 2022.</p>",
            unsafe_allow_html=True,
        )
        st.divider()
        party_name_mode = st.selectbox("Party names", PARTY_NAME_MODES, index=1, key="sweden_party_name_mode")
        st.divider()
        page_options = ["Explore", "Compare municipalities", "By Municipality"]
        if not nat.empty:
            page_options.append("National trends")
        page_options.append("About & sources")
        page = st.radio(
            "nav",
            page_options,
            label_visibility="collapsed",
            key="sweden_page",
        )
        st.divider()
        render_country_sidebar_footer(country_config)

    if mun.empty:
        st.error(describe_public_data_state(country_config.display_name, data_state))
        return
    if data_state["status"] != "ready":
        st.warning(describe_public_data_state(country_config.display_name, data_state))

    def result_divider():
        st.markdown(
            "<div style='margin:2rem 0 0.5rem;border-top:2px solid #0d0d14;'>"
            "<span style='font-size:0.58rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;"
            "color:#0d0d14;background:#f5f5f7;padding:0 0.6rem;position:relative;top:-0.7rem;'>RESULT</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    def finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note, context_label=None):
        ctx = f'<div class="copy-label" style="margin-bottom:0.3rem;">{context_label}</div>' if context_label else ""
        copy_block = ""
        if copy_sentence:
            copy_label = "Use with caution:" if strength_tag.startswith("WEAK PATTERN") else "Write this as:"
            copy_block = (
                f'<div class="copy-label">{copy_label}</div>'
                f'<div class="copy-box">{copy_sentence}</div>'
            )
        return (
            f'<div class="finding {strength_cls}">'
            f'<div class="strength-tag">{strength_tag}</div>'
            f'{ctx}'
            f'<div class="headline">{headline}</div>'
            f'<div class="body">{concrete}</div>'
            f'{copy_block}'
            f'<div class="footnote">{note}</div>'
            f'</div>'
        )

    def how_to_read():
        with st.expander("How to read this result"):
            st.markdown(
                """
**STRONG PATTERN (abs(r) >= 0.70)** - The municipality-level relationship is clear and stable enough to describe directly.
**MODERATE PATTERN (abs(r) 0.50-0.70)** - There is a consistent tendency, but it is still not an explanation.
**WEAK PATTERN (abs(r) 0.30-0.50)** - Use with caution. It is a weak municipality-level association.
**NO PATTERN (abs(r) below 0.30)** - Do not write a pattern claim. The data does not support it.

Positive r = both rise together. Negative r = they move in opposite directions.

*Correlation is not cause. The point is to describe the visible municipality-level pattern honestly.*
                """
            )

    if page == "Explore":
        if "sweden_explore_show" not in st.session_state:
            st.session_state["sweden_explore_show"] = False
        if "sweden_cx_factors" not in st.session_state:
            st.session_state["sweden_cx_factors"] = ["Income"]
        if "sweden_cx_all_parties" not in st.session_state:
            st.session_state["sweden_cx_all_parties"] = True
        if "sweden_cx_parties" not in st.session_state:
            st.session_state["sweden_cx_parties"] = latest_default_public_parties

        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>"
            f"{country_config.adjective} Politics Data</p>",
            unsafe_allow_html=True,
        )
        st.title("Is there a pattern?")
        st.markdown(
            "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:2rem;'>"
            "Pick one or more factors, one or more parties, and an election year. Then find out."
            "</p>",
            unsafe_allow_html=True,
        )

        factor_name_to_item = {item["label"]: item for item in metric_options}
        metric_labels = [item["label"] for item in metric_options]

        st.markdown('<div class="step-label">Step 1 — Which election year?</div>', unsafe_allow_html=True)
        sw_year_options = sweden_years
        if len(sw_year_options) == 1:
            sw_year = sw_year_options[0]
            st.selectbox(
                "year",
                options=sw_year_options,
                index=0,
                key="sweden_cx_year_single",
                label_visibility="collapsed",
                disabled=True,
            )
        else:
            sw_year = st.select_slider(
                "year",
                options=sw_year_options,
                value=sw_year_options[-1],
                key="sweden_cx_year",
                label_visibility="collapsed",
            )
        current_year_votes = mun[mun["year"] == sw_year].copy()
        party_profiles = get_sweden_party_profiles(current_year_votes)
        all_parties = party_profiles["party"].tolist()
        default_public_parties = party_profiles.loc[party_profiles["default_public"], "party"].tolist()

        st.markdown('<div class="step-label" style="margin-top:1rem;">Step 2 — What factors are available for that year?</div>', unsafe_allow_html=True)
        sw_metric_labels = st.pills(
            "sweden-factors",
            metric_labels,
            key="sweden_cx_factors",
            selection_mode="multi",
            label_visibility="collapsed",
        )
        if not sw_metric_labels:
            st.markdown(
                "<p style='font-size:0.74rem;color:#8888a0;margin-bottom:0;'>"
                "No factor is currently selected. Municipality-level pattern analysis requires at least one factor."
                "</p>",
                unsafe_allow_html=True,
            )

        st.markdown('<div class="step-label" style="margin-top:1rem;">Step 3 — Pick a party</div>', unsafe_allow_html=True)
        include_low_coverage = st.checkbox(
            "Show smaller parties too",
            key="sweden_include_low_coverage",
            help="Default public view keeps only parties with at least 25 municipalities and at least 0.5% mean municipality vote share. This toggle restores the smaller or thinner-coverage parties.",
        )
        selectable_parties = all_parties if include_low_coverage else default_public_parties
        current_selected = [p for p in st.session_state.get("sweden_cx_parties", []) if p in selectable_parties]
        if not current_selected:
            current_selected = selectable_parties[:] if st.session_state.get("sweden_cx_all_parties") else selectable_parties[:1]
        st.session_state["sweden_cx_parties"] = current_selected
        sw_all_toggle = st.checkbox("All parties", key="sweden_cx_all_parties")
        if sw_all_toggle:
            sw_parties = selectable_parties
            st.session_state["sweden_cx_parties"] = selectable_parties
        else:
            sw_parties = st.pills(
                "sweden-parties",
                selectable_parties,
                key="sweden_cx_parties",
                selection_mode="multi",
                format_func=lambda p: format_party_name(p, metadata=country_config.party_metadata, mode=party_name_mode, compact=True),
                label_visibility="collapsed",
            )
            if not sw_parties:
                st.markdown(
                    "<p style='font-size:0.74rem;color:#8888a0;margin-top:0.45rem;margin-bottom:0;'>"
                    "No party is currently selected. Municipality-level pattern analysis requires at least one party selection."
                    "</p>",
                    unsafe_allow_html=True,
                )
        st.markdown(
            "<p style='font-size:0.72rem;color:#8888a0;margin-top:0.35rem;margin-bottom:0;'>"
            "Default party view keeps only parties with at least 25 municipalities and at least 0.5% mean municipality vote share.</p>",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="step-label" style="margin-top:1rem;">Step 4 — Highlight a specific municipality? (optional)</div>', unsafe_allow_html=True)
        highlight_choice = st.selectbox(
            "Highlight municipality",
            ["— none —"] + available_municipalities,
            key="sweden_highlight",
            label_visibility="collapsed",
        )
        highlight_municipality = None if highlight_choice == "— none —" else highlight_choice

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        def precompute_sweden_correlations():
            rows = []
            for party in default_public_parties:
                votes = mun[(mun["year"] == sw_year) & (mun["party"] == party)][["municipality", "share"]]
                for metric_label_name in metric_labels:
                    item = factor_name_to_item[metric_label_name]
                    ms = get_sweden_metric_series(item["key"], sw_year, factor_frames, factor_catalog)
                    if ms.empty or "municipality" not in ms.columns:
                        continue
                    merged = votes.merge(ms, on="municipality", how="inner")
                    computed = compute_correlation_result(merged, factor=metric_label_name, party=party, year=sw_year, mode="precompute-sweden")
                    if not computed["valid"]:
                        continue
                    rows.append({"year": sw_year, "party": party, "factor": metric_label_name, "label": item["metric_label"], "r": computed["r"]})
            return pd.DataFrame(rows)

        col_main, col_surprise = st.columns([3, 1])
        with col_main:
            if st.button("Show me what the data reveals →", type="primary", width="stretch", key="sweden_show"):
                st.session_state["sweden_explore_show"] = True
        with col_surprise:
            if st.button("Surprise me →", width="stretch", key="sweden_surprise"):
                interesting = precompute_sweden_correlations()
                interesting = interesting[interesting["r"].abs() >= 0.40]
                if not interesting.empty:
                    anchor = interesting.sample(1).iloc[0]
                    st.session_state["sweden_cx_factors"] = [anchor["factor"]]
                    st.session_state["sweden_cx_parties"] = [anchor["party"]]
                    st.session_state["sweden_cx_all_parties"] = False
                    st.session_state["sweden_explore_show"] = True
                    st.rerun()

        if not st.session_state.get("sweden_explore_show"):
            return

        if not sw_metric_labels or not sw_parties:
            st.markdown(
                '<div class="finding weak">'
                '<div class="strength-tag">SELECTION INCOMPLETE</div>'
                '<div class="headline">This analysis cannot run yet.</div>'
                '<div class="body">A municipality-level correlation requires at least one factor and at least one party selection. No result should be inferred from an empty selection state.</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            return

        results = []
        for party in sw_parties:
            votes = mun[(mun["year"] == sw_year) & (mun["party"] == party)][["municipality", "share"]]
            for metric_label_name in sw_metric_labels:
                item = factor_name_to_item[metric_label_name]
                ms = get_sweden_metric_series(item["key"], sw_year, factor_frames, factor_catalog)
                if ms.empty or "municipality" not in ms.columns:
                    continue
                merged = votes.merge(ms, on="municipality", how="inner")
                computed = compute_correlation_result(merged, factor=metric_label_name, party=party, year=sw_year, mode="explore-sweden")
                results.append(
                    {
                        "party": party,
                        "factor": metric_label_name,
                        "factor_key": item["key"],
                        "label": item["metric_label"],
                        "r": computed["r"],
                        "merged": computed["merged"],
                        "valid": computed["valid"],
                        "n": computed["n"],
                        "reason": computed["reason"],
                        "strength": corr_strength_label(computed["r"]),
                    }
                )

        if not results:
            st.markdown(
                '<div class="finding weak">'
                '<div class="strength-tag">NO DATA</div>'
                '<div class="headline">This combination has no data.</div>'
                '<div class="body">The selected factor is not available for the Sweden municipality layer yet. Try a different factor.</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            return

        result_divider()

        if len(sw_parties) == 1 and len(sw_metric_labels) == 1:
            row = results[0]
            if not row["valid"]:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">RESULT UNAVAILABLE</div>'
                    '<div class="headline">Result unavailable</div>'
                    '<div class="body">The selected factor-party combination did not produce a reliable municipality-level correlation value.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                return
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_country_finding(
                row["r"], row["factor"], row["label"], row["party"], sw_year, row["merged"], party_name_mode, country_config
            )
            st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note), unsafe_allow_html=True)
            how_to_read()

            scatter_df = row["merged"].copy()
            scatter_df["highlight"] = scatter_df["municipality"].eq(highlight_municipality)
            chart = st.altair_chart  # noqa: F841
            import altair as alt

            scatter = alt.Chart(scatter_df).mark_circle(size=62).encode(
                x=alt.X("metric:Q", title=row["label"]),
                y=alt.Y("share:Q", title=f"Vote share · {format_party_name(row['party'], metadata=country_config.party_metadata, mode=party_name_mode, prose=True)}"),
                color=alt.condition(alt.datum.highlight, alt.value("#ef4444"), alt.value("#22d966")),
                tooltip=[
                    alt.Tooltip("municipality:N", title="Municipality"),
                    alt.Tooltip("metric:Q", title=row["label"], format=".2f"),
                    alt.Tooltip("share:Q", title="Vote share", format=".2f"),
                ],
            )
            st.altair_chart(scatter, width="stretch")

            metric_short = METRIC_SHORT_LABELS.get(row["factor"], row["label"])
            ranked = row["merged"].sort_values("metric").rename(
                columns={"municipality": "Municipality", "metric": metric_short, "share": "Vote share"}
            )
            tab_lo, tab_hi = st.tabs([f"Lowest {metric_short}", f"Highest {metric_short}"])
            with tab_lo:
                st.markdown(
                    f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.3rem;'>Lowest {metric_short} -></p>",
                    unsafe_allow_html=True,
                )
                render_compact_dataframe(ranked.head(10))
            with tab_hi:
                st.markdown(
                    f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.3rem;'>Highest {metric_short} -></p>",
                    unsafe_allow_html=True,
                )
                render_compact_dataframe(ranked.tail(10).sort_values(metric_short, ascending=False))

        elif len(sw_parties) == 1 and len(sw_metric_labels) > 1:
            valid_results = [r for r in results if r["valid"]]
            if not valid_results:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">NO VALID RESULT</div>'
                    '<div class="headline">No valid correlation result available</div>'
                    '<div class="body">None of the selected factor-party combinations produced a valid municipality-level correlation value.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                return
            ranked = sorted(valid_results, key=lambda x: abs(float(x["r"])), reverse=True)
            summary = pd.DataFrame(
                [{"Factor": r["factor"], "Label": r["factor"], "r": r["r"], "Strength": r["strength"]} for r in ranked]
            )
            st.markdown(
                "<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>",
                unsafe_allow_html=True,
            )
            render_bar_chart(summary, "Label", "r", tooltip_label="Factor", full_label_col="Factor")
            meaningful = [r for r in ranked if abs(float(r["r"])) >= 0.30] or ranked[:1]
            no_pattern = [r for r in ranked if abs(float(r["r"])) < 0.30]
            for row in meaningful:
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_country_finding(
                    row["r"], row["factor"], row["label"], row["party"], sw_year, row["merged"], party_name_mode, country_config
                )
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note), unsafe_allow_html=True)
            if no_pattern:
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>No pattern found for: {', '.join(r['factor'] for r in no_pattern)} (abs(r) below 0.30).</p>",
                    unsafe_allow_html=True,
                )
            how_to_read()
            with st.expander("See full ranking table"):
                render_compact_dataframe(summary[["Factor", "r", "Strength"]])

        elif len(sw_parties) > 1 and len(sw_metric_labels) == 1:
            valid_results = [r for r in results if r["valid"]]
            if not valid_results:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">NO VALID RESULT</div>'
                    '<div class="headline">No valid correlation result available</div>'
                    '<div class="body">None of the selected factor-party combinations produced a valid municipality-level correlation value.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                return
            ranked = sorted(valid_results, key=lambda x: abs(float(x["r"])), reverse=True)
            summary = pd.DataFrame(
                [{"Party": format_party_name(r["party"], metadata=country_config.party_metadata, mode=party_name_mode, compact=True), "Party_full": format_party_name(r["party"], metadata=country_config.party_metadata, mode=party_name_mode), "r": r["r"], "Strength": r["strength"]} for r in ranked]
            )
            st.markdown(
                "<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>",
                unsafe_allow_html=True,
            )
            render_bar_chart(summary, "Party", "r", tooltip_label="Party", full_label_col="Party_full")
            meaningful = [r for r in ranked if abs(float(r["r"])) >= 0.30] or ranked[:1]
            no_pattern = [r for r in ranked if abs(float(r["r"])) < 0.30]
            for row in meaningful:
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_country_finding(
                    row["r"], row["factor"], row["label"], row["party"], sw_year, row["merged"], party_name_mode, country_config
                )
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note), unsafe_allow_html=True)
            if no_pattern:
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>No pattern found for: {', '.join(format_party_name(r['party'], metadata=country_config.party_metadata, mode=party_name_mode, compact=True) for r in no_pattern)} (abs(r) below 0.30).</p>",
                    unsafe_allow_html=True,
                )
            how_to_read()
            with st.expander("See full ranking table"):
                render_compact_dataframe(summary[["Party_full", "r", "Strength"]], rename_map={"Party_full": "Party"})

        else:
            valid_results = [r for r in results if r["valid"]]
            if not valid_results:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">NO VALID RESULT</div>'
                    '<div class="headline">No valid correlation result available</div>'
                    '<div class="body">None of the selected factor-party combinations produced a valid municipality-level correlation value.</div>'
                    '</div>',
                    unsafe_allow_html=True,
                )
                return
            top = max(valid_results, key=lambda x: abs(float(x["r"])))
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_country_finding(
                top["r"], top["factor"], top["label"], top["party"], sw_year, top["merged"], party_name_mode, country_config
            )
            st.markdown(
                "<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.5rem;'>Showing highest correlation across selected factors and parties. Use the full correlation table to inspect all results.</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                finding_html(
                    strength_cls,
                    strength_tag,
                    headline,
                    concrete,
                    copy_sentence,
                    note,
                    context_label=f"Strongest signal: {format_party_name(top['party'], metadata=country_config.party_metadata, mode=party_name_mode, compact=True)} × {top['factor']}",
                ),
                unsafe_allow_html=True,
            )
            other_count = len(valid_results) - 1
            if other_count > 0:
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.3rem;'>{other_count} other signal{'s' if other_count > 1 else ''} exist — see full correlation table.</p>",
                    unsafe_allow_html=True,
                )
            how_to_read()
            with st.expander("See full correlation table"):
                flat_df = pd.DataFrame(
                    [{"Party": format_party_name(r["party"], metadata=country_config.party_metadata, mode=party_name_mode), "Factor": r["factor"], "r": r["r"]} for r in valid_results]
                ).assign(abs_r=lambda d: d["r"].abs()).sort_values("abs_r", ascending=False).drop(columns="abs_r").reset_index(drop=True)
                render_compact_dataframe(flat_df)

    elif page == "Compare municipalities":
        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>"
            f"{country_config.adjective} Politics Data</p>",
            unsafe_allow_html=True,
        )
        st.title("Compare two municipalities")
        st.markdown(
            "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:1.5rem;'>"
            "Pick two municipalities and compare their party profile and public factor layer for the selected election year."
            "</p>",
            unsafe_allow_html=True,
        )
        compare_year = st.selectbox("Election year", sweden_years, index=len(sweden_years) - 1, key="sweden_compare_year")
        compare_votes = mun[mun["year"] == compare_year].copy()
        col1, col2 = st.columns(2)
        with col1:
            mun_a = st.selectbox("Municipality A", available_municipalities, key="sweden_compare_a")
        with col2:
            mun_b = st.selectbox("Municipality B", available_municipalities, index=1, key="sweden_compare_b")
        if mun_a == mun_b:
            st.warning("Select two different municipalities.")
            return

        st.markdown("## Voting patterns")

        votes_a = compare_votes[compare_votes["municipality"] == mun_a].set_index("party")["share"]
        votes_b = compare_votes[compare_votes["municipality"] == mun_b].set_index("party")["share"]
        common = votes_a.index.intersection(votes_b.index)
        if len(common):
            gap_series = (votes_a[common] - votes_b[common]).sort_values(key=lambda s: s.abs(), ascending=False)
            top_parties = gap_series.head(8).index.tolist()
            gap_chart_df = pd.DataFrame(
                {
                    "Party": [format_party_name(party, metadata=country_config.party_metadata, mode=party_name_mode, compact=True) for party in top_parties],
                    "Party_full": [format_party_name(party, metadata=country_config.party_metadata, mode=party_name_mode) for party in top_parties],
                    "Gap": [float(gap_series[party]) for party in top_parties],
                }
            )
            st.markdown(
                f"<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.5rem;'>"
                f"Percentage point gap in vote share: <strong>{mun_a}</strong> minus <strong>{mun_b}</strong>. "
                f"Positive bar = {mun_a} votes more for that party. Negative = {mun_b} does.</p>",
                unsafe_allow_html=True,
            )
            render_bar_chart(gap_chart_df, "Party", "Gap", tooltip_label="Party", full_label_col="Party_full")
            biggest_party = gap_series.index[0]
            biggest_gap = float(gap_series.iloc[0])
            direction = mun_a if biggest_gap > 0 else mun_b
            st.markdown(
                f'<div class="finding moderate">'
                f'<div class="headline">Biggest difference: {format_party_name(biggest_party, metadata=country_config.party_metadata, mode=party_name_mode, prose=True)}</div>'
                f'<div class="body"><strong>{direction}</strong> is currently <strong>{abs(biggest_gap):.1f} percentage points</strong> higher on this party in the Sweden {compare_year} municipality layer.</div>'
                f'<div class="footnote">Riksdag {compare_year} · municipality-safe public layer · {country_config.source_note}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            with st.expander("See full vote snapshot for both municipalities"):
                display_parties = gap_series.index.tolist()
                tab_a, tab_b = st.tabs([mun_a, mun_b])
                with tab_a:
                    votes_a_display = votes_a[display_parties].round(1).reset_index()
                    votes_a_display["party"] = votes_a_display["party"].apply(lambda value: format_party_name(value, metadata=country_config.party_metadata, mode=party_name_mode))
                    render_compact_dataframe(votes_a_display.rename(columns={"party": "Party", "share": "Vote %"}))
                with tab_b:
                    votes_b_display = votes_b[display_parties].round(1).reset_index()
                    votes_b_display["party"] = votes_b_display["party"].apply(lambda value: format_party_name(value, metadata=country_config.party_metadata, mode=party_name_mode))
                    render_compact_dataframe(votes_b_display.rename(columns={"party": "Party", "share": "Vote %"}))

        st.markdown("## Current factor profile")
        st.markdown(
            "<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.8rem;'>"
            "Current municipality profile using the selected election year for the Sweden public factor layer."
            "</p>",
            unsafe_allow_html=True,
        )
        cards = []
        for item in metric_options:
            metric_key = item["key"]
            metric_series = get_sweden_metric_series(metric_key, compare_year, factor_frames, factor_catalog)
            left_value = metric_series.loc[metric_series["municipality"] == mun_a, "metric"]
            right_value = metric_series.loc[metric_series["municipality"] == mun_b, "metric"]
            cards.append(
                {
                    "Metric": item["label"],
                    mun_a: f"{left_value.iloc[0]:.2f}" if not left_value.empty else "—",
                    mun_b: f"{right_value.iloc[0]:.2f}" if not right_value.empty else "—",
                    "Year": str(compare_year),
                }
            )
        st.subheader("Current factor profile")
        render_profile_cards(cards, mun_a, mun_b)

    elif page == "By Municipality":
        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>"
            f"{country_config.adjective} Politics Data</p>",
            unsafe_allow_html=True,
        )
        st.title("By Municipality")
        st.markdown(
            "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:1.5rem;'>"
            "Pick a party and a year. See all Swedish municipalities ranked by vote share."
            "</p>",
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            municipality_year = st.selectbox("Election year", sweden_years, index=len(sweden_years) - 1, key="sweden_single_year")
        with col2:
            parties_for_year = ordered_sweden_parties_for_year(mun, municipality_year)
            party = st.selectbox(
                "Party",
                parties_for_year,
                format_func=lambda value: format_party_name(value, metadata=country_config.party_metadata, mode=party_name_mode),
                key="sweden_single_party",
            )

        filtered = mun[(mun["year"] == municipality_year) & (mun["party"] == party)].sort_values("share", ascending=False)
        top = filtered.iloc[0]
        bottom = filtered.iloc[-1]
        avg = filtered["share"].mean()

        st.markdown(
            f"<p style='font-size:0.82rem;color:#3a3a4a;margin-bottom:0.8rem;'>"
            f"<strong>Highest:</strong> {top['municipality']} ({top['share']:.1f}%) &nbsp;·&nbsp; "
            f"<strong>Lowest:</strong> {bottom['municipality']} ({bottom['share']:.1f}%) &nbsp;·&nbsp; "
            f"<strong>Avg:</strong> {avg:.1f}%</p>",
            unsafe_allow_html=True,
        )
        render_compact_dataframe(
            filtered[["municipality", "share"]].rename(columns={"municipality": "Municipality", "share": "Vote %"})
        )
        with st.expander("Show full municipality bar chart"):
            render_bar_chart(
                filtered.assign(
                    municipality_label=filtered["municipality"],
                ),
                "municipality_label",
                "share",
                tooltip_label="Municipality",
                full_label_col="municipality",
            )

    elif page == "National trends":
        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>"
            f"{country_config.adjective} Politics Data</p>",
            unsafe_allow_html=True,
        )
        st.title("National trends")
        st.markdown(
            "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:1.5rem;'>"
            "Six Riksdag elections from 2002 to 2022. Select which parties to compare."
            "</p>",
            unsafe_allow_html=True,
        )
        parties_nat = ordered_national_parties(nat)
        default_nat = [party for party in top_national_parties(nat, top_n=5) if party in parties_nat]
        selected = st.multiselect(
            "Parties",
            parties_nat,
            default=default_nat,
            format_func=lambda party: format_party_name(party, metadata=country_config.party_metadata, mode=party_name_mode, compact=True),
            key="sweden_national_parties",
        )
        if selected:
            chart_df = nat[nat["party"].isin(selected)].copy()
            chart_df["party_label"] = chart_df["party"].apply(lambda party: format_party_name(party, metadata=country_config.party_metadata, mode=party_name_mode, compact=True))
            pivot = chart_df.pivot_table(index="election_year", columns="party_label", values="share")
            pivot = pivot.rename(columns=lambda party: format_party_name(party, metadata=country_config.party_metadata, mode=party_name_mode, compact=True))
            render_national_trend_chart(chart_df, "election_year", "party_label", "share")
            table = format_display_table(pivot, decimals=2)
            st.dataframe(table, width="stretch")

    else:
        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>"
            f"{country_config.adjective} Politics Data</p>",
            unsafe_allow_html=True,
        )
        st.title("About & Sources")
        st.markdown(
            f"""
This Sweden surface currently covers a municipality-safe public reading of three Riksdag election years.

Built for journalists and researchers. No login required. This public layer is deliberately narrow and municipality-safe by design.

- Country: `{country_config.display_name}`
- Election scope: `Riksdag municipality layer 2014, 2018, 2022` + `national vote trends 2002–2022`
- Public geography: `{country_config.public_geography_label}`
- Public geography count: `{country_config.public_geography_count}`
- Statistics source: `{country_config.statistics_source_name}`
- Election source: `Valmyndigheten`

Current Sweden public factors are either `Country-local` or `Family-mapped`.
Internal harvested candidates remain outside the public selector until they survive year-coverage and semantic review.
"""
        )
        st.markdown(
            """
**Method note**
- Correlation is not causation.
- Sweden public factors are municipality-safe and year-aware for `2014`, `2018`, and `2022`.
- Sweden `National trends` is a separate official Valmyndigheten national summary layer for `2002`, `2006`, `2010`, `2014`, `2018`, and `2022`.
- The public factor layer currently favors factors with clean municipality coverage and readable public semantics over breadth.
- Smaller or thinner-coverage parties can be restored in Explore, but the default party view keeps the first reading more robust.
- Party name mode changes only labels in the interface. Data values and party IDs stay the same.
"""
        )
        factor_state = []
        for item in metric_options:
            filename = item["filename"]
            state = get_factor_status(factor_frames[filename])
            factor_state.append({"Factor": item["label"], "Status": format_status_label(state)})
        render_compact_dataframe(pd.DataFrame(factor_state))
        st.subheader("Data sources")
        st.markdown(
            """
<div class="source-item"><strong>Valmyndigheten</strong> — Municipality election exports for `2014`, `2018`, and `2022` in the Sweden public vote layer.</div>
<div class="source-item"><strong>Valmyndigheten national summaries</strong> — Official national Riksdag vote-share summaries for `2002`, `2006`, `2010`, `2014`, `2018`, and `2022`.</div>
<div class="source-item"><strong>Statistics Sweden TAB1267</strong> — Population and age structure.</div>
<div class="source-item"><strong>Statistics Sweden TAB3981</strong> — Higher education share.</div>
<div class="source-item"><strong>Statistics Sweden TAB1792</strong> — Average disposable income.</div>
<div class="source-item"><strong>Statistics Sweden TAB628</strong> — Population density.</div>
<div class="source-item"><strong>Statistics Sweden TAB1278 bulk export</strong> — Passenger cars in use, normalized to cars per 1,000 residents.</div>
<div class="source-item"><strong>Statistics Sweden AA0003D / IntGr6Kom bulk export</strong> — Share in rented accommodation.</div>
<div class="source-item"><strong>Statistics Sweden BO0104T01 / TAB821 bulk export</strong> — Share in one-/two-dwelling buildings.</div>
            """,
            unsafe_allow_html=True,
        )
