from __future__ import annotations

import altair as alt
import streamlit as st


PARTY_NAME_MODES = ["Native", "English", "Both"]

METRIC_SHORT_LABELS = {
    "Population": "Population",
    "Education": "Higher edu. %",
    "Income": "Income",
    "Commute distance": "Commute km",
    "Employment": "Employed / 1k",
    "Welfare": "Welfare / 1k",
    "Crime": "Crime / 1k",
    "Cars": "Cars / 1k",
    "Age 65+": "Age 65+ %",
    "Turnout": "Turnout %",
    "Immigration share": "Immigration %",
    "Population density": "Population / km²",
    "Unemployment": "Unemployment %",
    "Owner-occupied housing": "Owner-occ. %",
    "Detached houses": "Detached %",
    "One-person households": "1-person %",
}

METRIC_PHRASES = {
    "Population": "population size",
    "Education": "higher education share",
    "Income": "disposable income",
    "Commute distance": "average commute distance",
    "Employment": "full-time employment",
    "Welfare": "social assistance use",
    "Crime": "reported crime",
    "Cars": "car ownership",
    "Age 65+": "share aged 65+",
    "Turnout": "voter turnout",
    "Immigration share": "immigration share",
    "Population density": "population density",
    "Unemployment": "unemployment rate",
    "Owner-occupied housing": "owner-occupied housing share",
    "Detached houses": "detached-house dwelling share",
    "One-person households": "one-person household share",
}


def party_parts(raw_party: str, metadata: dict[str, dict[str, str]]):
    if raw_party in metadata and raw_party == "Independent candidates":
        meta = metadata[raw_party].copy()
        return None, meta
    if ". " in raw_party:
        code, english_source = raw_party.split(". ", 1)
        meta = metadata.get(code, {}).copy()
        if not meta:
            meta = {
                "native": english_source,
                "english": english_source,
                "short_native": english_source,
                "short_english": english_source,
            }
        return code, meta
    meta = metadata.get(
        raw_party,
        {
            "native": raw_party,
            "english": raw_party,
            "short_native": raw_party,
            "short_english": raw_party,
        },
    )
    return None, meta


def format_party_name(
    raw_party: str,
    *,
    metadata: dict[str, dict[str, str]],
    mode: str = "English",
    compact: bool = False,
    include_code: bool = False,
    prose: bool = False,
) -> str:
    code, meta = party_parts(raw_party, metadata)
    native = meta["short_native"] if compact else meta["native"]
    english = meta["short_english"] if compact else meta["english"]

    if mode in {"Native", "Danish"}:
        label = native
    elif mode == "Both":
        label = f"{native} ({english})" if prose else f"{native} / {english}"
    else:
        label = english

    if include_code and code:
        return f"{code}. {label}"
    return label


def format_party_code(
    code: str,
    *,
    metadata: dict[str, dict[str, str]],
    known_parties: list[str],
    mode: str = "English",
    compact: bool = False,
) -> str:
    for raw_party in known_parties:
        party_code, _ = party_parts(raw_party, metadata)
        if party_code == code:
            return format_party_name(
                raw_party,
                metadata=metadata,
                mode=mode,
                compact=compact,
                include_code=True,
            )
    return code


def render_bar_chart(df, label_col, value_col, tooltip_label=None, full_label_col=None):
    chart_df = df.copy()
    order = chart_df[label_col].tolist()
    tooltip_fields = [alt.Tooltip(label_col, title=tooltip_label or label_col)]
    if full_label_col and full_label_col in chart_df.columns:
        tooltip_fields = [alt.Tooltip(full_label_col, title=tooltip_label or full_label_col)]
    tooltip_fields.append(alt.Tooltip(value_col, format=".2f", title=value_col))
    chart = alt.Chart(chart_df).mark_bar().encode(
        y=alt.Y(f"{label_col}:N", sort=order, title=None),
        x=alt.X(f"{value_col}:Q", title=value_col),
        color=alt.condition(alt.datum[value_col] >= 0, alt.value("#22d966"), alt.value("#3d8ef0")),
        tooltip=tooltip_fields,
    ).properties(height=max(220, len(chart_df) * 34))
    st.altair_chart(chart, use_container_width=True)


def render_national_trend_chart(df, year_col, party_col, share_col):
    chart_df = df.copy()
    chart_df["year_label"] = chart_df[year_col].astype(str)
    chart = (
        alt.Chart(chart_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("year_label:O", title="Election year", sort=chart_df["year_label"].drop_duplicates().tolist()),
            y=alt.Y(f"{share_col}:Q", title="Vote share (%)"),
            color=alt.Color(f"{party_col}:N", title="Party"),
            tooltip=[
                alt.Tooltip("year_label:O", title="Election year"),
                alt.Tooltip(f"{party_col}:N", title="Party"),
                alt.Tooltip(f"{share_col}:Q", title="Vote share", format=".2f"),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)


def render_compact_dataframe(df, rename_map=None):
    table = df.copy()
    if rename_map:
        table = table.rename(columns=rename_map)
    st.dataframe(table, use_container_width=True, hide_index=True)


def render_profile_cards(rows, label_a, label_b):
    cards = []
    for row in rows:
        cards.append(
            "<div class='data-card'>"
            f"<div class='metric'>{row['Metric']}</div>"
            f"<div class='value-line'><strong>{label_a}:</strong> {row[label_a]}</div>"
            f"<div class='value-line'><strong>{label_b}:</strong> {row[label_b]}</div>"
            f"<div class='year'>Year: {row['Year']}</div>"
            "</div>"
        )
    st.markdown(f"<div class='data-card-grid'>{''.join(cards)}</div>", unsafe_allow_html=True)


def render_status_badge(status):
    colors = {
        "country_local": ("#f6f3d0", "#746514"),
        "family_mapped": ("#d9eefc", "#0b5c88"),
        "cross_country_ready": ("#d7f6e4", "#12723d"),
        "not_public_ready": ("#f8e0df", "#7b2d2a"),
    }
    bg, fg = colors.get(status, ("#f0f0f5", "#666678"))
    label = status.replace("_", "-").title()
    st.markdown(
        f"<span style='display:inline-block;padding:0.22rem 0.5rem;border-radius:999px;background:{bg};color:{fg};font-size:0.64rem;'>"
        f"{label}</span>",
        unsafe_allow_html=True,
    )


def get_factor_status(frame, default="not_public_ready"):
    if frame.empty or "comparability_status" not in frame.columns:
        return default
    first = frame["comparability_status"].dropna()
    if first.empty:
        return default
    return first.iloc[0]


def format_status_label(status):
    return status.replace("_", "-").title()


def render_country_sidebar_footer(country_config):
    lines = [f"Data: {country_config.source_note}"]
    if country_config.secondary_source_note:
        lines.append(country_config.secondary_source_note)
    lines.append("")
    lines.append("Built by <strong>Hedegreen Research</strong>")
    html = "<br>".join(lines)
    st.markdown(
        f"<div class='sidebar-footer'><p style='font-size:0.65rem;color:#aaaabc;line-height:1.6;'>{html}</p></div>",
        unsafe_allow_html=True,
    )


def build_country_finding(
    corr,
    factor_name,
    metric_label,
    party,
    year,
    merged,
    party_name_mode,
    country_config,
):
    from core.correlation import is_valid_correlation

    if not is_valid_correlation(corr):
        return (
            "weak",
            "RESULT UNAVAILABLE",
            "Result unavailable",
            "The correlation value for this selection could not be computed reliably. No pattern claim should be made for this result.",
            None,
            f"Correlation unavailable · {len(merged)} {country_config.public_geography_label_plural} · {country_config.source_note}",
        )

    abs_r = abs(corr)
    ranked = merged.sort_values("metric")
    low10 = ranked.head(10)["share"].mean()
    high10 = ranked.tail(10)["share"].mean()
    p_short = format_party_name(
        party,
        metadata=country_config.party_metadata,
        mode=party_name_mode,
        prose=True,
    )
    m_short = METRIC_PHRASES.get(factor_name, metric_label.lower())
    note = f"Pearson r = {corr:.2f} · {len(merged)} {country_config.public_geography_label_plural} · {country_config.source_note}"

    if abs_r < 0.30:
        return (
            "weak",
            "NO PATTERN",
            "No consistent pattern found.",
            f"The data shows no consistent relationship between {m_short} and votes for {p_short} across {len(merged)} {country_config.public_geography_label_plural}.",
            None,
            note,
        )

    if corr < 0:
        direction = "lower"
        more_avg, less_avg = low10, high10
        low_label, high_label = "lowest", "highest"
    else:
        direction = "higher"
        more_avg, less_avg = high10, low10
        low_label, high_label = "highest", "lowest"

    gap = round(abs(more_avg - less_avg), 1)
    concrete = (
        f"{country_config.display_name} {country_config.public_geography_label_plural.title()} with {direction} {m_short} "
        f"tend to vote more for {p_short}. The gap is {gap:.1f} percentage points: "
        f"the 10 {country_config.public_geography_label_plural} with the {low_label} {m_short} gave {more_avg:.1f}% "
        f"to {p_short}, compared to {less_avg:.1f}% in the 10 with the {high_label}."
    )
    copy_sentence = (
        f"Write: In the {year} {country_config.election_label.lower()}, {country_config.public_geography_label_plural} "
        f"with {direction} {m_short} tended to give more support to {p_short}. "
        f"Based on data from {len(merged)} {country_config.adjective.lower()} {country_config.public_geography_label_plural}. "
        f"(Source: {country_config.source_note})"
    )
    if abs_r >= 0.70:
        band = "strong"
        tag = f"STRONG PATTERN · r = {corr:.2f}"
    elif abs_r >= 0.50:
        band = "moderate"
        tag = f"MODERATE PATTERN · r = {corr:.2f}"
    else:
        band = "weak"
        tag = f"WEAK PATTERN · r = {corr:.2f}"
    return band, tag, f"{country_config.public_geography_label_plural.title()} with {direction} {m_short} tend to vote more for {p_short}.", concrete, copy_sentence, note
