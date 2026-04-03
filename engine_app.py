import streamlit as st
import pandas as pd
import altair as alt
import random
import os
from pathlib import Path

from app_data_variants import resolve_sweden_public_path
from app_failure_states import describe_public_data_state, summarize_public_data_state
from correlation_utils import correlation_band, corr_strength_label, compute_correlation_result, is_valid_correlation
from country_registry import BASE_FACTOR_CATALOG, get_country_config, list_exposed_public_countries


def parse_env_country_ids(raw_value):
    if not raw_value:
        return None
    parsed = [item.strip().lower() for item in raw_value.split(",") if item.strip()]
    return parsed or None


APP_TITLE = os.getenv("WPD_APP_TITLE", "World Politics Data")
EXPOSED_COUNTRY_IDS = parse_env_country_ids(os.getenv("WPD_EXPOSE_COUNTRIES", ""))
DATA_VARIANT = os.getenv("WPD_DATA_VARIANT", "").strip().lower()
embedded_mode = str(st.query_params.get("embedded", "")).lower() in {"1", "true", "yes"}
st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="collapsed" if embedded_mode else "expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&display=swap');

html, body, [class*="css"] { font-family: 'JetBrains Mono', monospace !important; }

section[data-testid="stSidebar"] {
    background: #ffffff !important; border-right: 1px solid #e0e0e8 !important;
    min-width: 240px !important; max-width: 280px !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1.4rem !important;
    min-height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
}
section[data-testid="stSidebar"] .stRadio > div {
    gap: 0.2rem !important;
}
section[data-testid="stSidebar"] .stRadio label {
    margin-bottom: 0 !important;
}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] {
    gap: 0.15rem !important;
}
section[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
    padding: 0.08rem 0 !important;
}
.main .block-container { padding-top: 2.5rem; padding-left: 3rem; padding-right: 3rem; max-width: 960px; }

h1 {
    font-family: 'Crimson Pro', Georgia, serif !important;
    font-size: 2.1rem !important; font-weight: 300 !important;
    color: #0d0d14 !important; line-height: 1.2 !important; margin-bottom: 0.3rem !important;
}
h2 {
    font-size: 0.7rem !important; font-weight: 500 !important; letter-spacing: 0.12em !important;
    text-transform: uppercase !important; color: #22d966 !important;
    border-bottom: 1px solid #e8e8f0 !important; padding-bottom: 0.4rem !important;
    margin-top: 2rem !important; margin-bottom: 0.8rem !important;
}
p { font-size: 0.88rem !important; line-height: 1.75 !important; color: #3a3a4a !important; }
.stCaption p { color: #8888a0 !important; font-size: 0.68rem !important; }
.stRadio > label { display: none !important; }
.stSelectbox label, .stMultiSelect label {
    font-size: 0.65rem !important; font-weight: 500 !important;
    letter-spacing: 0.09em !important; text-transform: uppercase !important; color: #8888a0 !important;
}
hr { border-color: #e0e0e8 !important; margin: 1.5rem 0 !important; }
.hr-wordmark {
    font-size: 0.58rem; font-weight: 500; letter-spacing: 0.18em;
    text-transform: uppercase; color: #aaaabc; margin-bottom: 1.6rem;
}
.hr-wordmark .dot { color: #22d966; }
.sidebar-footer {
    margin-top: auto;
    padding-top: 1.2rem;
}

/* Metric tiles */
.metric-tile {
    border: 1px solid #e0e0e8; padding: 1.1rem 1.2rem; margin-bottom: 0.5rem;
    background: #fff; line-height: 1.5;
}
.metric-tile.selected { border-color: #22d966; background: #f4fef8; }
.metric-tile .q { font-size: 0.92rem; font-weight: 400; color: #0d0d14; margin-bottom: 0.2rem; }
.metric-tile .hint { font-size: 0.72rem; color: #8888a0; }

/* Step labels */
.step-label {
    font-size: 0.6rem; font-weight: 500; letter-spacing: 0.14em;
    text-transform: uppercase; color: #aaaabc; margin-bottom: 0.5rem;
}

/* Finding reveal */
.finding {
    padding: 1.4rem 1.6rem; margin: 1.5rem 0;
    border-left: 3px solid #22d966; background: #f4fef8;
    animation: fadeIn 0.5s ease;
}
.finding.moderate { border-color: #3d8ef0; background: #f2f6ff; }
.finding.weak { border-color: #d0d0dc; background: #f8f8fb; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }
.finding .strength-tag {
    font-size: 0.58rem; font-weight: 700; letter-spacing: 0.18em;
    text-transform: uppercase; color: #22d966; margin-bottom: 0.5rem;
}
.finding.moderate .strength-tag { color: #3d8ef0; }
.finding.weak .strength-tag { color: #aaaabc; }
.finding .headline {
    font-family: 'Crimson Pro', Georgia, serif;
    font-size: 1.4rem; font-weight: 400; color: #0d0d14;
    line-height: 1.3; margin-bottom: 0.7rem;
}
.finding .body { font-size: 0.88rem; color: #2a2a3a; line-height: 1.75; }
.finding .copy-box {
    font-size: 0.8rem; color: #2a2a3a; line-height: 1.7;
    background: #fff; border: 1px solid #d0d0dc;
    padding: 0.8rem 1rem; margin-top: 0.9rem;
}
.finding .copy-label {
    font-size: 0.55rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #aaaabc; margin-bottom: 0.3rem;
}
.finding .footnote { font-size: 0.68rem; color: #aaaabc; margin-top: 0.8rem; }

/* Source items */
.source-item { font-size: 0.72rem; color: #6a6a7a; padding: 0.4rem 0; border-bottom: 1px solid #f0f0f5; line-height: 1.5; }
.source-item strong { color: #0d0d14; font-weight: 500; }
.data-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.75rem;
    margin: 0.8rem 0 0.4rem;
}
.data-card {
    border: 1px solid #e0e0e8;
    background: #fff;
    padding: 0.9rem 1rem;
}
.data-card .metric {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #8888a0;
    margin-bottom: 0.45rem;
}
.data-card .value-line {
    font-size: 0.84rem;
    line-height: 1.6;
    color: #1d1d28;
}
.data-card .year {
    margin-top: 0.45rem;
    font-size: 0.67rem;
    color: #8888a0;
}

@media (max-width: 900px) {
    .main .block-container { padding-top: 1.2rem; padding-left: 1rem; padding-right: 1rem; max-width: 100%; }
    section[data-testid="stSidebar"] { min-width: 100% !important; max-width: 100% !important; }
    h1 { font-size: 1.65rem !important; }
    .finding { padding: 1rem 1rem; }
    .finding .headline { font-size: 1.18rem; }
    .data-card-grid { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ── helpers ───────────────────────────────────────────────────────────────────

EXCLUDE = lambda s: (
    s.str.startswith("Province") | s.str.startswith("Region") |
    (s == "All Denmark") | (s == "Christiansø")
)
FACTOR_DIR = Path("denmark/factors")


def exclude_public_special_cases(df, column="municipality"):
    return df[~df[column].isin(["All Denmark", "Christiansø"])].copy()


def invalid_result_detail(reason):
    if reason == "zero_variance_metric":
        return "The selected factor has no usable municipality variation for this year after preprocessing."
    if reason == "zero_variance_share":
        return "The selected party has no usable municipality variation for this year."
    if reason == "insufficient_rows":
        return "There are too few overlapping municipality rows to compute a reliable correlation."
    return "The correlation value for this selection could not be computed reliably."


def sweden_public_path(relative_path, variant=None):
    active_variant = DATA_VARIANT if variant is None else variant
    return resolve_sweden_public_path(relative_path, active_variant)


def municipal_vote_source_label(year):
    if year == 2026:
        return "Official VALG 2026 municipality bridge + Danmarks Statistik indicators"
    return "Danmarks Statistik (CC 4.0 BY)"


def municipal_vote_source_inline(year):
    if year == 2026:
        return "Official VALG 2026 municipality bridge for vote share + Danmarks Statistik for the selected indicator"
    return "Danmarks Statistik, CC 4.0 BY"


PARTY_METADATA = {
    "A": {"danish": "Socialdemokratiet", "english": "The Social Democrats", "short_danish": "Soc.dem.", "short_english": "Soc. Dems"},
    "B": {"danish": "Radikale Venstre", "english": "The Danish Social-Liberal Party", "short_danish": "Radikale", "short_english": "Soc. Liberals"},
    "C": {"danish": "Det Konservative Folkeparti", "english": "The Conservative People's Party", "short_danish": "Konservative", "short_english": "Conservatives"},
    "D": {"danish": "Nye Borgerlige", "english": "The New Right", "short_danish": "Nye Borgerlige", "short_english": "New Right"},
    "E": {"danish": "Klaus Riskær Pedersen", "english": "Klaus Riskær Pedersen", "short_danish": "Riskær", "short_english": "Riskær"},
    "F": {"danish": "Socialistisk Folkeparti", "english": "The Socialist People's Party", "short_danish": "SF", "short_english": "Socialist PP"},
    "H": {"danish": "Borgernes Parti", "english": "The Citizens' Party", "short_danish": "Borgernes Parti", "short_english": "Citizens' Party"},
    "I": {"danish": "Liberal Alliance", "english": "Liberal Alliance", "short_danish": "LA", "short_english": "Liberal Alliance"},
    "K": {"danish": "Kristendemokraterne", "english": "Christian Democrats", "short_danish": "KD", "short_english": "Christian Dems"},
    "M": {"danish": "Moderaterne", "english": "The Moderates", "short_danish": "Moderaterne", "short_english": "Moderates"},
    "O": {"danish": "Dansk Folkeparti", "english": "The Danish People's Party", "short_danish": "DF", "short_english": "Danish PP"},
    "P": {"danish": "Stram Kurs", "english": "Hard Line", "short_danish": "Stram Kurs", "short_english": "Hard Line"},
    "Q": {"danish": "Frie Grønne", "english": "Independent Greens", "short_danish": "Frie Grønne", "short_english": "Ind. Greens"},
    "V": {"danish": "Venstre", "english": "Venstre (Liberal Party of Denmark)", "short_danish": "Venstre", "short_english": "Venstre"},
    "Å": {"danish": "Alternativet", "english": "The Alternative", "short_danish": "Alternativet", "short_english": "Alternative"},
    "Æ": {"danish": "Danmarksdemokraterne", "english": "The Danish Democrats", "short_danish": "Danmarksdem.", "short_english": "Danish Dems"},
    "Ø": {"danish": "Enhedslisten", "english": "The Red-Green Alliance", "short_danish": "Enhedslisten", "short_english": "Red-Green"},
    "Independent candidates": {"danish": "Løsgængere", "english": "Independent candidates", "short_danish": "Løsgængere", "short_english": "Independents"},
}

ACTIVE_PARTY_METADATA = PARTY_METADATA

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


def party_parts(raw_party):
    metadata = ACTIVE_PARTY_METADATA or PARTY_METADATA
    if raw_party in metadata and raw_party == "Independent candidates":
        meta = metadata[raw_party].copy()
        if "native" not in meta and "danish" in meta:
            meta["native"] = meta["danish"]
            meta["short_native"] = meta.get("short_danish", meta["danish"])
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
        elif "native" not in meta and "danish" in meta:
            meta["native"] = meta["danish"]
            meta["short_native"] = meta.get("short_danish", meta["danish"])
        return code, meta
    meta = metadata.get(raw_party, {
        "native": raw_party,
        "english": raw_party,
        "short_native": raw_party,
        "short_english": raw_party,
    })
    if "native" not in meta and "danish" in meta:
        meta["native"] = meta["danish"]
        meta["short_native"] = meta.get("short_danish", meta["danish"])
    return None, meta


def format_party_name(raw_party, mode="English", compact=False, include_code=False, prose=False):
    code, meta = party_parts(raw_party)
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


def format_party_code(code, mode="English", compact=False):
    for raw in ALL_PARTY_NAMES if "ALL_PARTY_NAMES" in globals() else []:
        party_code, _ = party_parts(raw)
        if party_code == code:
            return format_party_name(raw, mode=mode, compact=compact, include_code=True)
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

def build_finding(corr, factor_name, metric_label, party, year, merged, party_name_mode):
    if not is_valid_correlation(corr):
        return "weak", "RESULT UNAVAILABLE", "Result unavailable", \
            "The correlation value for this selection could not be computed reliably. No pattern claim should be made for this result.", \
            None, \
            f"Correlation unavailable · {len(merged)} municipalities · {municipal_vote_source_label(year)}"

    abs_r  = abs(corr)
    ranked = merged.sort_values("metric")
    low10  = ranked.head(10)["share"].mean()
    high10 = ranked.tail(10)["share"].mean()
    p_short = format_party_name(party, mode=party_name_mode, prose=True)
    m_short = METRIC_PHRASES.get(factor_name, metric_label.lower())

    note = f"Pearson r = {corr:.2f} · {len(merged)} municipalities · {municipal_vote_source_label(year)}"

    if abs_r < 0.30:
        return (
            "weak",
            "NO PATTERN",
            f"No consistent pattern found.",
            f"The data shows no consistent relationship between {m_short} and votes for {p_short} across {len(merged)} municipalities. "
            f"If you were looking for a story here — the data does not support it.",
            None,
            note
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
        f"Municipalities with {direction} {m_short} tend to vote more for {p_short}. "
        f"The gap is <strong>{gap:.1f} percentage points</strong>: "
        f"the 10 municipalities with the {low_label} {m_short} gave <strong>{more_avg:.1f}%</strong> to {p_short} in {year}, "
        f"compared to {less_avg:.1f}% in the 10 with the {high_label}."
    )
    if abs_r >= 0.70:
        copy_sentence = (
            f"Write: <em>\"In the {year} election, municipalities with {direction} {m_short} "
            f"gave on average {gap:.1f} percentage points more to {p_short}. "
            f"Based on data from {len(merged)} Danish municipalities. "
            f"(Source: {municipal_vote_source_inline(year)})\"</em>"
        )
    elif abs_r >= 0.50:
        copy_sentence = (
            f"Write: <em>\"In the {year} election, municipalities with {direction} {m_short} "
            f"tended to give more support to {p_short}. "
            f"Based on data from {len(merged)} Danish municipalities. "
            f"(Source: {municipal_vote_source_inline(year)})\"</em>"
        )
    else:
        copy_sentence = (
            f"Use with caution: <em>\"At municipality level, there is a weak association between {direction} {m_short} "
            f"and vote share for {p_short} in {year}. This does not explain why the pattern exists. "
            f"Based on data from {len(merged)} Danish municipalities. (Source: {municipal_vote_source_inline(year)})\"</em>"
        )

    if abs_r >= 0.70:
        return "strong",   "STRONG PATTERN · r = {:.2f}".format(corr),   "Municipalities with {direction} {m} tend to vote more for {p}.".format(direction=direction, m=m_short, p=p_short), concrete, copy_sentence, note
    elif abs_r >= 0.50:
        return "moderate", "MODERATE PATTERN · r = {:.2f}".format(corr), "Municipalities with {direction} {m} tend to vote more for {p}.".format(direction=direction, m=m_short, p=p_short), concrete, copy_sentence, note
    else:
        return "weak",     "WEAK PATTERN · r = {:.2f}".format(corr),     "Municipalities with {direction} {m} show a weak tendency toward {p}.".format(direction=direction, m=m_short, p=p_short), concrete, copy_sentence, note


def build_country_finding(corr, factor_name, metric_label, party, year, merged, party_name_mode, country_config):
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
    p_short = format_party_name(party, mode=party_name_mode, prose=True)
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


@st.cache_data
def load_sweden_municipal():
    path = sweden_public_path("riksdag/riksdag_party_share_by_municipality.csv")
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
    }
    df = df[~df["party"].isin(excluded_rows)].copy()
    return df[["party", "municipality", "public_geography_id", "year", "share"]]


@st.cache_data
def load_sweden_national():
    path = sweden_public_path("riksdag/riksdag_national_vote_share.csv")
    if not path.exists():
        return pd.DataFrame(columns=["party", "election_year", "share", "mandates"])
    df = pd.read_csv(path)
    df["election_year"] = df["election_year"].astype(int)
    df["share"] = df["share"].astype(float)
    if "mandates" in df.columns:
        df["mandates"] = df["mandates"].astype(int)
    return df


@st.cache_data
def load_sweden_factor_file(filename):
    path = sweden_public_path(f"factors/{filename}")
    if not path.exists():
        return pd.DataFrame(columns=["municipality", "public_geography_id", "year", "value", "comparability_status"])
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    return df


def get_sweden_metric_series(metric_key, year, factor_frames):
    filename = BASE_FACTOR_CATALOG[metric_key]["filename"]
    df = factor_frames[filename]
    if df.empty:
        return pd.DataFrame(columns=["municipality", "metric"])
    frame = df[df["year"] == year][["municipality", "value"]].copy()
    frame["metric"] = frame["value"]
    return frame[["municipality", "metric"]]


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


def sweden_variant_is_ready():
    if not DATA_VARIANT:
        return True
    municipal_path = sweden_public_path("riksdag/riksdag_party_share_by_municipality.csv")
    if not municipal_path.exists():
        return False
    try:
        municipal_df = pd.read_csv(municipal_path)
    except Exception:
        return False
    if municipal_df.empty:
        return False

    factor_dir = sweden_public_path("factors")
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


def render_sweden_app(country_config, selected_country_label):
    factor_frames = {
        BASE_FACTOR_CATALOG[key]["filename"]: load_sweden_factor_file(BASE_FACTOR_CATALOG[key]["filename"])
        for key in country_config.supported_factors
    }
    mun = load_sweden_municipal()
    nat = load_sweden_national()
    data_state = summarize_public_data_state(municipal_df=mun, national_df=nat, factor_frames=factor_frames)
    sweden_years = sorted(mun["year"].unique().tolist())
    available_municipalities = sorted(mun["municipality"].unique())
    metric_options = [BASE_FACTOR_CATALOG[key] | {"key": key} for key in country_config.supported_factors]
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
                format_func=lambda p: format_party_name(p, mode=party_name_mode, compact=True),
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
                    ms = get_sweden_metric_series(item["key"], sw_year, factor_frames)
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
            if st.button("Show me what the data reveals →", type="primary", use_container_width=True, key="sweden_show"):
                st.session_state["sweden_explore_show"] = True
        with col_surprise:
            if st.button("Surprise me →", use_container_width=True, key="sweden_surprise"):
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
                ms = get_sweden_metric_series(item["key"], sw_year, factor_frames)
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
            chart = alt.Chart(scatter_df).mark_circle(size=62).encode(
                x=alt.X("metric:Q", title=row["label"]),
                y=alt.Y("share:Q", title=f"Vote share · {format_party_name(row['party'], mode=party_name_mode, prose=True)}"),
                color=alt.condition(alt.datum.highlight, alt.value("#ef4444"), alt.value("#22d966")),
                tooltip=[
                    alt.Tooltip("municipality:N", title="Municipality"),
                    alt.Tooltip("metric:Q", title=row["label"], format=".2f"),
                    alt.Tooltip("share:Q", title="Vote share", format=".2f"),
                ],
            )
            st.altair_chart(chart, use_container_width=True)

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
                [{"Factor": r["factor"], "Label": METRIC_SHORT_LABELS.get(r["factor"], r["factor"]), "r": r["r"], "Strength": r["strength"]} for r in ranked]
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
                [{"Party": format_party_name(r["party"], mode=party_name_mode, compact=True), "Party_full": format_party_name(r["party"], mode=party_name_mode), "r": r["r"], "Strength": r["strength"]} for r in ranked]
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
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>No pattern found for: {', '.join(format_party_name(r['party'], mode=party_name_mode, compact=True) for r in no_pattern)} (abs(r) below 0.30).</p>",
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
                    context_label=f"Strongest signal: {format_party_name(top['party'], mode=party_name_mode, compact=True)} × {top['factor']}",
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
                    [{"Party": format_party_name(r["party"], mode=party_name_mode), "Factor": r["factor"], "r": r["r"]} for r in valid_results]
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
                    "Party": [format_party_name(party, mode=party_name_mode, compact=True) for party in top_parties],
                    "Party_full": [format_party_name(party, mode=party_name_mode) for party in top_parties],
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
                f'<div class="headline">Biggest difference: {format_party_name(biggest_party, mode=party_name_mode, prose=True)}</div>'
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
                    votes_a_display["party"] = votes_a_display["party"].apply(lambda value: format_party_name(value, mode=party_name_mode))
                    render_compact_dataframe(votes_a_display.rename(columns={"party": "Party", "share": "Vote %"}))
                with tab_b:
                    votes_b_display = votes_b[display_parties].round(1).reset_index()
                    votes_b_display["party"] = votes_b_display["party"].apply(lambda value: format_party_name(value, mode=party_name_mode))
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
            metric_series = get_sweden_metric_series(metric_key, compare_year, factor_frames)
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
                format_func=lambda value: format_party_name(value, mode=party_name_mode),
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
            format_func=lambda party: format_party_name(party, mode=party_name_mode, compact=True),
            key="sweden_national_parties",
        )
        if selected:
            chart_df = nat[nat["party"].isin(selected)].copy()
            chart_df["party_label"] = chart_df["party"].apply(lambda party: format_party_name(party, mode=party_name_mode, compact=True))
            pivot = chart_df.pivot_table(index="election_year", columns="party_label", values="share")
            pivot = pivot.rename(columns=lambda party: format_party_name(party, mode=party_name_mode, compact=True))
            render_national_trend_chart(chart_df, "election_year", "party_label", "share")
            table = pivot.round(2).astype(object).where(pivot.notna(), "—")
            st.dataframe(table, use_container_width=True)

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
            """,
            unsafe_allow_html=True,
        )


PUBLIC_COUNTRY_CONFIGS = list_exposed_public_countries(EXPOSED_COUNTRY_IDS)
if DATA_VARIANT:
    PUBLIC_COUNTRY_CONFIGS = [
        config
        for config in PUBLIC_COUNTRY_CONFIGS
        if config.country_id != "sweden" or sweden_variant_is_ready()
    ]
if not PUBLIC_COUNTRY_CONFIGS:
    st.error("No public country data packs are currently exposed for this app profile.")
    st.stop()

PUBLIC_COUNTRY_LABELS = {config.display_name: config.country_id for config in PUBLIC_COUNTRY_CONFIGS}
DEFAULT_COUNTRY_ID = PUBLIC_COUNTRY_CONFIGS[0].country_id if len(PUBLIC_COUNTRY_CONFIGS) == 1 else "denmark"
if DEFAULT_COUNTRY_ID not in PUBLIC_COUNTRY_LABELS.values():
    DEFAULT_COUNTRY_ID = PUBLIC_COUNTRY_CONFIGS[0].country_id
requested_country = str(st.query_params.get("country", DEFAULT_COUNTRY_ID))
if requested_country not in PUBLIC_COUNTRY_LABELS.values():
    requested_country = DEFAULT_COUNTRY_ID
requested_country_label = next(
    label for label, country_id in PUBLIC_COUNTRY_LABELS.items() if country_id == requested_country
)

with st.sidebar:
    if len(PUBLIC_COUNTRY_LABELS) == 1:
        selected_country_label = requested_country_label
        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.09em;text-transform:uppercase;color:#8888a0;margin-bottom:0.35rem;'>Country</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            (
                "<div style='padding:0.62rem 0.8rem;border:1px solid #e0e0e8;border-radius:0.5rem;"
                "background:#f7f7fb;color:#5a5a6a;font-size:0.88rem;line-height:1.3;'>"
                f"{selected_country_label}</div>"
            ),
            unsafe_allow_html=True,
        )
    else:
        selected_country_label = st.selectbox(
            "Country",
            options=list(PUBLIC_COUNTRY_LABELS),
            index=list(PUBLIC_COUNTRY_LABELS).index(requested_country_label),
            key="country_switcher",
        )

selected_country = PUBLIC_COUNTRY_LABELS[selected_country_label]
if selected_country != requested_country:
    st.query_params["country"] = selected_country
    st.rerun()

country_config = get_country_config(selected_country)
ACTIVE_PARTY_METADATA = country_config.party_metadata

if selected_country == "sweden":
    render_sweden_app(country_config, selected_country_label)
    st.stop()

# ── data loaders ──────────────────────────────────────────────────────────────

@st.cache_data
def load_municipal():
    frames = []
    share_files = [
        Path("denmark/folketing/fvpandel_party_share.csv"),
        Path("denmark/folketing/fv2026_party_share_by_municipality.csv"),
    ]
    for share_file in share_files:
        if not share_file.exists():
            continue
        frame = pd.read_csv(share_file, sep=";", encoding="utf-8-sig")
        frame.columns = ["party","municipality","year","share"]
        frames.append(frame)

    if not frames:
        return pd.DataFrame(columns=["party", "municipality", "year", "share"])

    df = pd.concat(frames, ignore_index=True)
    df["year"] = df["year"].astype(int)
    df = df[(df["party"] != "Total") & (df["municipality"] != "All Denmark")].copy()
    return exclude_public_special_cases(df)

@st.cache_data
def load_national():
    df = pd.read_csv("denmark/folketing/straubinger_votes_1953_2022.csv")
    cols = [c for c in df.columns if c.startswith("party_")]
    df = df.melt(id_vars=["year","date","total_valid"], value_vars=cols, var_name="party", value_name="votes")
    df["party"] = df["party"].str.replace("party_","").str.upper()
    df = df.dropna(subset=["votes"])
    df["share"] = (df["votes"] / df["total_valid"] * 100).round(1)
    return df

@st.cache_data
def load_population():
    path = FACTOR_DIR / "population.csv"
    if path.exists():
        df = pd.read_csv(path)
        df["year"] = df["year"].astype(int)
        return exclude_public_special_cases(
            df.rename(columns={"value": "population"})
        )
    df = pd.read_csv("denmark/socioeconomic/folk1a_population_annual.csv", sep=";", encoding="utf-8-sig")
    df = df[~EXCLUDE(df["OMRÅDE"])].copy()
    df["year"] = df["TID"].str[:4].astype(int)
    return df[["OMRÅDE","TID","year","INDHOLD"]].rename(columns={"OMRÅDE":"municipality","INDHOLD":"population"})

@st.cache_data
def load_factor_file(filename):
    path = FACTOR_DIR / filename
    if not path.exists():
        return pd.DataFrame(columns=["municipality", "year", "value"])
    df = pd.read_csv(path)
    df["year"] = df["year"].astype(int)
    return exclude_public_special_cases(df)

@st.cache_data
def load_income():
    return load_factor_file("income.csv")

@st.cache_data
def load_social():
    return load_factor_file("welfare_per_1000.csv")

@st.cache_data
def load_crime():
    return load_factor_file("crime_per_1000.csv")

@st.cache_data
def load_cars():
    return load_factor_file("cars_per_1000.csv")

@st.cache_data
def load_divorces():
    return load_factor_file("divorces_per_1000.csv")

@st.cache_data
def load_commute_distance():
    return load_factor_file("commute_distance_km.csv")

@st.cache_data
def load_education():
    return load_factor_file("education.csv")

@st.cache_data
def load_age65():
    return load_factor_file("age65_pct.csv")

@st.cache_data
def load_employment():
    return load_factor_file("employment_per_1000.csv")

@st.cache_data
def load_turnout():
    return load_factor_file("turnout_pct.csv")

@st.cache_data
def load_immigration():
    return load_factor_file("immigration_share_pct.csv")

@st.cache_data
def load_population_density():
    return load_factor_file("population_density.csv")

@st.cache_data
def load_unemployment():
    return load_factor_file("unemployment_pct.csv")

@st.cache_data
def load_owner_occupied_housing():
    return load_factor_file("owner_occupied_dwelling_share_pct.csv")

@st.cache_data
def load_detached_houses():
    return load_factor_file("detached_house_dwelling_share_pct.csv")

@st.cache_data
def load_one_person_households():
    return load_factor_file("one_person_household_share_pct.csv")

mun           = load_municipal()
nat           = load_national()
pop_df        = load_population()
income_df     = load_income()
social_df     = load_social()
crime_df      = load_crime()
cars_df       = load_cars()
divorce_df    = load_divorces()
commute_df    = load_commute_distance()
employment_df = load_employment()
education_df  = load_education()
age65_df      = load_age65()
turnout_df    = load_turnout()
immigration_df = load_immigration()
density_df    = load_population_density()
unemployment_df = load_unemployment()
owner_occupied_df = load_owner_occupied_housing()
detached_houses_df = load_detached_houses()
one_person_households_df = load_one_person_households()

# ── sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="hr-wordmark">HEDEGREEN RESEARCH<span class="dot"> ●</span></div>', unsafe_allow_html=True)
    st.markdown("**Danish Politics Data**")
    st.markdown(
        "<p style='font-size:0.75rem;color:#6a6a7a;line-height:1.6;margin-top:0.3rem;'>"
        "National vote trends 1953–2022. Municipality vote share 2007–2026, with the 2026 layer bridged from the official VALG export."
        "</p>", unsafe_allow_html=True
    )
    st.divider()
    party_name_mode = st.selectbox("Party names", PARTY_NAME_MODES, index=1)
    st.divider()
    page = st.radio("nav", ["Explore", "Compare municipalities", "By Municipality", "National trends", "About & sources"],
                    label_visibility="collapsed")
    st.divider()
    render_country_sidebar_footer(get_country_config("denmark"))

# ── Explore (guided discovery) ────────────────────────────────────────────────

METRIC_OPTIONS = [
    ("Population",  "Population (reference count)",               "population",   "Do larger municipalities vote differently?"),
    ("Education",   "Higher education share (%)",                "education",   "Do more educated municipalities vote differently?"),
    ("Income",      "Avg. disposable income (DKK per person)",   "income",      "Do wealthier municipalities vote differently?"),
    ("Commute distance", "Avg. commute distance (km)",           "commute",     "Do long-commute municipalities vote differently?"),
    ("Employment",  "Full-time employees per 1,000 residents",   "employment",  "Do areas with higher employment vote differently?"),
    ("Welfare",     "Social assistance recipients per 1,000 residents", "social", "Do areas with more people on benefits vote differently?"),
    ("Crime",       "Reported crimes per 1,000 residents",       "crime",       "Is there a link between crime rates and voting patterns?"),
    ("Cars",        "Passenger cars per 1,000 residents",        "cars",        "Do car-heavy (rural) areas vote differently from urban ones?"),
    ("Age 65+",     "Share aged 65+ (%)",                        "age65",       "Do older municipalities vote differently?"),
    ("Turnout",     "Votes cast as share of voters (%)",         "turnout",     "Do high-turnout municipalities vote differently?"),
    ("Immigration share", "Residents without Danish origin (%)", "immigration", "Do municipalities with larger immigrant and descendant shares vote differently?"),
    ("Population density", "Residents per km²",                  "density",     "Does dense settlement correlate with voting behaviour?"),
    ("Unemployment", "Full-time unemployment rate (%)",          "unemployment","Do municipalities with higher unemployment vote differently?"),
    ("Owner-occupied housing", "Owner-occupied occupied dwellings (%)", "owner_occupied", "Do municipalities with more owner-occupied housing vote differently?"),
    ("Detached houses", "Detached/farmhouse occupied dwellings (%)", "detached_houses", "Do municipalities with more detached-house living patterns vote differently?"),
    ("One-person households", "Occupied dwellings with 1 person (%)", "one_person_households", "Do municipalities with more one-person households vote differently?"),
]
ALL_METRIC_KEYS    = [m[0] for m in METRIC_OPTIONS]
ALL_PARTY_NAMES    = sorted(mun["party"].unique())
ALL_ELECTION_YEARS = sorted(mun["year"].unique())
DEFAULT_EXPLORE_YEAR = 2022 if 2022 in ALL_ELECTION_YEARS else ALL_ELECTION_YEARS[-1]
MUNICIPAL_ELECTION_RANGE_LABEL = f"{ALL_ELECTION_YEARS[0]}–{ALL_ELECTION_YEARS[-1]}"

def get_metric_series(metric_key, year, _population, _income, _social, _crime, _cars, _divorces, _commute, _employment, _education, _age65, _turnout, _immigration, _density, _unemployment, _owner_occupied, _detached_houses, _one_person_households):
    if metric_key == "population":
        df = _population[_population["year"] == year][["municipality", "population"]].copy()
        df["metric"] = df["population"]
        return df[["municipality", "metric"]]
    if metric_key == "education":
        df = _education[_education["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "age65":
        df = _age65[_age65["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "income":
        df = _income[_income["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "commute":
        df = _commute[_commute["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "employment":
        df = _employment[_employment["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "social":
        df = _social[_social["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "crime":
        df = _crime[_crime["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "cars":
        df = _cars[_cars["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "divorces":
        df = _divorces[_divorces["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "turnout":
        df = _turnout[_turnout["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "immigration":
        df = _immigration[_immigration["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "density":
        df = _density[_density["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "unemployment":
        df = _unemployment[_unemployment["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "owner_occupied":
        df = _owner_occupied[_owner_occupied["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "detached_houses":
        df = _detached_houses[_detached_houses["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    elif metric_key == "one_person_households":
        df = _one_person_households[_one_person_households["year"] == year][["municipality","value"]].copy()
        df["metric"] = df["value"]
        return df[["municipality","metric"]]
    return pd.DataFrame()


def metric_has_usable_year_data(metric_frame):
    if metric_frame.empty or "municipality" not in metric_frame.columns or "metric" not in metric_frame.columns:
        return False
    usable = metric_frame.dropna(subset=["metric"]).copy()
    if usable.empty:
        return False
    if usable["municipality"].nunique() < 10:
        return False
    if usable["metric"].nunique() <= 1:
        return False
    return True


def available_metric_keys_for_year(year, _population, _income, _social, _crime, _cars, _divorces, _commute, _employment, _education, _age65, _turnout, _immigration, _density, _unemployment, _owner_occupied, _detached_houses, _one_person_households):
    available = []
    for metric_name, _, metric_key, _ in METRIC_OPTIONS:
        metric_frame = get_metric_series(
            metric_key,
            year,
            _population,
            _income,
            _social,
            _crime,
            _cars,
            _divorces,
            _commute,
            _employment,
            _education,
            _age65,
            _turnout,
            _immigration,
            _density,
            _unemployment,
            _owner_occupied,
            _detached_houses,
            _one_person_households,
        )
        if metric_has_usable_year_data(metric_frame):
            available.append(metric_name)
    return available


def available_parties_for_year(year, municipal_df):
    year_frame = municipal_df[municipal_df["year"] == year].copy()
    if year_frame.empty:
        return []
    year_frame["share"] = pd.to_numeric(year_frame["share"], errors="coerce")
    active = year_frame.groupby("party", dropna=False)["share"].sum(min_count=1).reset_index()
    active = active[active["share"].fillna(0) > 0]
    return sorted(active["party"].unique())

@st.cache_data
def precompute_all_correlations(_mun, _pop_df, _income_df, _social_df, _crime_df, _cars_df, _divorce_df, _commute_df, _employment_df, _education_df, _age65_df, _turnout_df, _immigration_df, _density_df, _unemployment_df, _owner_occupied_df, _detached_houses_df, _one_person_households_df):
    rows = []
    for year in sorted(_mun["year"].unique()):
        for party in sorted(_mun["party"].unique()):
            votes = _mun[(_mun["year"] == year) & (_mun["party"] == party)][["municipality","share"]]
            if votes.empty: continue
            for m_name, m_label, m_key, _ in METRIC_OPTIONS:
                ms = get_metric_series(m_key, year, _pop_df, _income_df, _social_df, _crime_df, _cars_df, _divorce_df, _commute_df, _employment_df, _education_df, _age65_df, _turnout_df, _immigration_df, _density_df, _unemployment_df, _owner_occupied_df, _detached_houses_df, _one_person_households_df)
                if ms.empty or "municipality" not in ms.columns: continue
                merged = votes.merge(ms, on="municipality", how="inner")
                computed = compute_correlation_result(merged, factor=m_name, party=party, year=year, mode="precompute")
                if not computed["valid"]:
                    continue
                rows.append({"year": year, "party": party, "factor": m_name, "label": m_label, "r": computed["r"]})
    return pd.DataFrame(rows)

all_corr_df = precompute_all_correlations(mun, pop_df, income_df, social_df, crime_df, cars_df, divorce_df, commute_df, employment_df, education_df, age65_df, turnout_df, immigration_df, density_df, unemployment_df, owner_occupied_df, detached_houses_df, one_person_households_df)

if page == "Explore":

    # Initialise session state defaults (must happen before widgets render)
    if "cx_factors" not in st.session_state:
        st.session_state["cx_factors"] = ["Income"]
    if "cx_year" not in st.session_state:
        st.session_state["cx_year"] = DEFAULT_EXPLORE_YEAR
    if "cx_all_parties" not in st.session_state:
        st.session_state["cx_all_parties"] = True
    if "cx_parties" not in st.session_state:
        st.session_state["cx_parties"] = []
    if "cx_year_seen" not in st.session_state:
        st.session_state["cx_year_seen"] = st.session_state["cx_year"]
    if "cx_parties_seen_for_year" not in st.session_state:
        st.session_state["cx_parties_seen_for_year"] = []

    # Apply surprise values BEFORE widgets render (Streamlit requires this order)
    if st.session_state.get("_surprise_pending"):
        st.session_state["cx_year"]    = st.session_state.pop("_surprise_year")
        st.session_state["cx_factors"] = st.session_state.pop("_surprise_factors")
        st.session_state["cx_parties"] = st.session_state.pop("_surprise_parties")
        st.session_state["cx_all_parties"] = False
        del st.session_state["_surprise_pending"]

    st.markdown("<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>Danish Politics Data</p>", unsafe_allow_html=True)
    st.title("Is there a pattern?")
    st.markdown(
        "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:2rem;'>"
        "Pick one or more factors, one or more parties, and an election year. Then find out."
        "</p>", unsafe_allow_html=True
    )

    # ── Step 1: year ──────────────────────────────────────────────────────────
    st.markdown('<div class="step-label">Step 1 — Which election year?</div>', unsafe_allow_html=True)
    cx_year = st.select_slider("year", options=ALL_ELECTION_YEARS, key="cx_year",
                               label_visibility="collapsed")

    available_metric_keys = available_metric_keys_for_year(
        cx_year,
        pop_df,
        income_df,
        social_df,
        crime_df,
        cars_df,
        divorce_df,
        commute_df,
        employment_df,
        education_df,
        age65_df,
        turnout_df,
        immigration_df,
        density_df,
        unemployment_df,
        owner_occupied_df,
        detached_houses_df,
        one_person_households_df,
    )
    parties_for_year = available_parties_for_year(cx_year, mun)

    current_metric_selection = [m for m in st.session_state.get("cx_factors", []) if m in available_metric_keys]
    if available_metric_keys and not current_metric_selection:
        current_metric_selection = [available_metric_keys[0]]
    st.session_state["cx_factors"] = current_metric_selection

    previous_year = st.session_state.get("cx_year_seen")
    previous_parties_for_year = st.session_state.get("cx_parties_seen_for_year", [])
    year_changed = previous_year != cx_year
    current_party_selection = [p for p in st.session_state.get("cx_parties", []) if p in parties_for_year]
    if st.session_state.get("cx_all_parties"):
        current_party_selection = parties_for_year
    elif year_changed:
        newly_available = [p for p in parties_for_year if p not in previous_parties_for_year]
        if newly_available:
            current_party_selection = [
                party for party in parties_for_year
                if party in set(current_party_selection) | set(newly_available)
            ]
    st.session_state["cx_parties"] = current_party_selection
    st.session_state["cx_year_seen"] = cx_year
    st.session_state["cx_parties_seen_for_year"] = parties_for_year

    # ── Step 2: metrics (year-aware selector) ────────────────────────────────
    st.markdown('<div class="step-label" style="margin-top:1rem;">Step 2 — What factors are available for that year?</div>', unsafe_allow_html=True)
    if available_metric_keys:
        cx_metric_keys = st.pills(
            "factors",
            available_metric_keys,
            key="cx_factors",
            selection_mode="multi",
            label_visibility="collapsed",
        )
    else:
        cx_metric_keys = []
        st.markdown(
            "<p style='font-size:0.74rem;color:#8888a0;margin-bottom:0;'>"
            "No usable municipality factor layer is available for that election year yet."
            "</p>",
            unsafe_allow_html=True,
        )

    # ── Step 3: parties (year-aware quick buttons + advanced multi) ─────────
    st.markdown('<div class="step-label" style="margin-top:1rem;">Step 3 — Pick a party</div>', unsafe_allow_html=True)
    all_toggle = st.checkbox("All parties", key="cx_all_parties")
    if all_toggle:
        cx_parties = parties_for_year
        st.session_state["cx_parties"] = parties_for_year
    else:
        cx_parties = st.pills(
            "parties",
            parties_for_year,
            key="cx_parties",
            selection_mode="multi",
            format_func=lambda p: format_party_name(p, mode=party_name_mode, compact=True, include_code=True),
            label_visibility="collapsed",
        )
        if not cx_parties:
            st.markdown(
                "<p style='font-size:0.74rem;color:#8888a0;margin-top:0.45rem;margin-bottom:0;'>"
                "No party is currently selected. Municipality-level pattern analysis requires at least one party selection."
                "</p>",
                unsafe_allow_html=True,
            )

    # ── Step 4: highlight a municipality (optional) ───────────────────────────
    st.markdown('<div class="step-label" style="margin-top:1rem;">Step 4 — Highlight a specific municipality? (optional)</div>', unsafe_allow_html=True)
    all_munis_explore = ["— none —"] + sorted(mun["municipality"].unique())
    cx_highlight = st.selectbox("highlight", all_munis_explore, key="cx_highlight",
                                label_visibility="collapsed")
    highlight_muni = None if cx_highlight == "— none —" else cx_highlight

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    if cx_year == 2026:
        st.markdown(
            "<p style='font-size:0.74rem;color:#8888a0;margin-top:0.2rem;margin-bottom:0.9rem;'>"
            "2026 municipality vote share comes from an official VALG fine-count aggregation. "
            "The wider municipality indicator refresh is still partial, so some factor combinations remain unavailable."
            "</p>",
            unsafe_allow_html=True,
        )

    col_main, col_surprise = st.columns([3, 1])
    with col_main:
        if st.button("Show me what the data reveals →", type="primary", use_container_width=True, disabled=(not available_metric_keys or not parties_for_year or not cx_parties)):
            st.session_state["explore_show"] = True
    with col_surprise:
        if st.button("Surprise me →", use_container_width=True):
            interesting = all_corr_df[all_corr_df["r"].abs() >= 0.40]
            if not interesting.empty:
                mode = random.choice(["single", "multi_factor", "multi_party"])
                anchor = interesting.sample(1).iloc[0]
                s_year = int(anchor["year"])
                if mode == "single":
                    # Case A: 1 factor, 1 party
                    factors  = [anchor["factor"]]
                    parties  = [anchor["party"]]
                elif mode == "multi_factor":
                    # Case B: top 2–3 factors for a random party in a random year
                    same = interesting[(interesting["party"] == anchor["party"]) &
                                       (interesting["year"]  == s_year)].nlargest(3, "r" if anchor["r"] > 0 else "r")
                    same = same.reindex(same["r"].abs().sort_values(ascending=False).index)
                    factors = same["factor"].tolist() if len(same) >= 2 else [anchor["factor"]]
                    parties = [anchor["party"]]
                else:
                    # Case C: top 2–3 parties for a random factor in a random year
                    same = interesting[(interesting["factor"] == anchor["factor"]) &
                                       (interesting["year"]  == s_year)]
                    same = same.reindex(same["r"].abs().sort_values(ascending=False).index)
                    factors = [anchor["factor"]]
                    parties = same["party"].tolist()[:3] if len(same) >= 2 else [anchor["party"]]
                st.session_state["_surprise_year"]    = s_year
                st.session_state["_surprise_factors"] = factors
                st.session_state["_surprise_parties"] = parties
                st.session_state["_surprise_pending"] = True
                st.session_state["explore_show"] = True
                st.rerun()

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.get("explore_show"):
        s_year, s_parties, s_metric_keys = cx_year, cx_parties, cx_metric_keys

        if not s_metric_keys or not s_parties:
            st.markdown(
                '<div class="finding weak">'
                '<div class="strength-tag">SELECTION INCOMPLETE</div>'
                '<div class="headline">This analysis cannot run yet.</div>'
                '<div class="body">A municipality-level correlation requires at least one factor and at least one party selection. No result should be inferred from an empty selection state.</div>'
                '</div>', unsafe_allow_html=True
            )
            st.stop()

        # Build correlation matrix: rows=parties, cols=metrics
        results = []
        for party in s_parties:
            votes = mun[(mun["year"] == s_year) & (mun["party"] == party)][["municipality","share"]]
            for mk in s_metric_keys:
                m_info  = next(m for m in METRIC_OPTIONS if m[0] == mk)
                m_label = m_info[1]
                ms = get_metric_series(m_info[2], s_year, pop_df, income_df, social_df, crime_df, cars_df, divorce_df, commute_df, employment_df, education_df, age65_df, turnout_df, immigration_df, density_df, unemployment_df, owner_occupied_df, detached_houses_df, one_person_households_df)
                if ms.empty or "municipality" not in ms.columns:
                    continue
                merged  = votes.merge(ms, on="municipality", how="inner")
                if merged.empty: continue
                computed = compute_correlation_result(merged, factor=mk, party=party, year=s_year, mode="explore")
                results.append({
                    "party": party,
                    "factor": mk,
                    "label": m_label,
                    "r": computed["r"],
                    "merged": computed["merged"],
                    "valid": computed["valid"],
                    "n": computed["n"],
                    "reason": computed["reason"],
                    "strength": corr_strength_label(computed["r"])
                })

        if not results:
            st.markdown(
                '<div class="finding weak">'
                '<div class="strength-tag">NO DATA</div>'
                '<div class="headline">This combination has no data.</div>'
                '<div class="body">The selected factor is not available for this election year. Try a different year or factor.</div>'
                '</div>', unsafe_allow_html=True
            )
            st.stop()

        # Visual break before result
        st.markdown(
            "<div style='margin:2rem 0 0.5rem;border-top:2px solid #0d0d14;'>"
            "<span style='font-size:0.58rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;"
            "color:#0d0d14;background:#f5f5f7;padding:0 0.6rem;position:relative;top:-0.7rem;'>RESULT</span>"
            "</div>", unsafe_allow_html=True
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
                st.markdown("""
**STRONG PATTERN (abs(r) ≥ 0.70)** — Write: *"Data from 98 municipalities shows a clear link."*
**MODERATE PATTERN (abs(r) 0.50–0.70)** — Write: *"There is a consistent tendency."*
**WEAK PATTERN (abs(r) 0.30–0.50)** — Use with caution. It is a weak municipality-level association, not an explanation.
**NO PATTERN (abs(r) below 0.30)** — Do not write a pattern claim. The data does not support it.

Positive r = both go up together. Negative r = they go in opposite directions.

*Correlation ≠ cause. The data shows a pattern — not why it exists.*
                """)

        # ── Case A: 1 party, 1 metric → full finding + scatter ───────────────
        if len(s_parties) == 1 and len(s_metric_keys) == 1:
            row = results[0]
            if not row["valid"]:
                invalid_body = (
                    f"{invalid_result_detail(row['reason'])} "
                    "No pattern claim should be made for this result."
                )
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">RESULT UNAVAILABLE</div>'
                    '<div class="headline">Result unavailable</div>'
                    f'<div class="body">{invalid_body}</div>'
                    '</div>', unsafe_allow_html=True
                )
                st.stop()
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                row["r"], row["factor"], row["label"], row["party"], s_year, row["merged"], party_name_mode)
            st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note),
                        unsafe_allow_html=True)
            how_to_read()

            # Always show the extremes — the concrete municipalities at both ends
            metric_short = METRIC_SHORT_LABELS.get(row["factor"], row["label"])
            ranked_data = row["merged"].sort_values("metric").rename(columns={
                "municipality": "Municipality",
                "share": "Vote %",
                "metric": metric_short
            })
            tab_lo, tab_hi = st.tabs([f"Lowest {metric_short}", f"Highest {metric_short}"])
            with tab_lo:
                st.markdown(
                    f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
                    f"color:#aaaabc;margin-bottom:0.3rem;'>Lowest {metric_short} →</p>",
                    unsafe_allow_html=True
                )
                render_compact_dataframe(ranked_data.head(10))
            with tab_hi:
                st.markdown(
                    f"<p style='font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;"
                    f"color:#aaaabc;margin-bottom:0.3rem;'>Highest {metric_short} →</p>",
                    unsafe_allow_html=True
                )
                render_compact_dataframe(ranked_data.tail(10).sort_values(metric_short, ascending=False))

            # ── Highlight callout ──────────────────────────────────────────────
            if highlight_muni:
                h_row = row["merged"][row["merged"]["municipality"] == highlight_muni]
                if not h_row.empty:
                    h_metric = h_row["metric"].iloc[0]
                    h_share  = h_row["share"].iloc[0]
                    # Rank position
                    sorted_all = row["merged"].sort_values("metric").reset_index(drop=True)
                    h_rank = sorted_all[sorted_all["municipality"] == highlight_muni].index[0] + 1
                    st.markdown(
                        f'<div style="border:1px solid #22d966;padding:0.8rem 1.1rem;margin-bottom:1rem;background:#f4fef8;">'
                        f'<span style="font-size:0.58rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;color:#22d966;">HIGHLIGHTED: {highlight_muni}</span><br>'
                        f'<span style="font-size:0.88rem;color:#0d0d14;">{row["label"]}: <strong>{h_metric:.1f}</strong> &nbsp;·&nbsp; '
                        f'Vote share: <strong>{h_share:.1f}%</strong> &nbsp;·&nbsp; '
                        f'Rank {h_rank} of {len(sorted_all)} municipalities by {metric_short.lower()}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.caption(f"No data for {highlight_muni} in {s_year}.")

            st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-top:1rem;'>Each dot = one municipality. Named dots = extremes.</p>", unsafe_allow_html=True)
            scatter_df = row["merged"].copy()
            scatter_df["vote_share"] = pd.to_numeric(scatter_df["share"], errors="coerce")
            scatter_df["metric_value"] = pd.to_numeric(scatter_df["metric"], errors="coerce")
            scatter_df = scatter_df.dropna(subset=["vote_share", "metric_value"]).copy()
            # Label top 5 + bottom 5 by metric, plus the highlighted municipality
            sorted_sc = scatter_df.sort_values("metric_value")
            label_munis = set(sorted_sc.head(5)["municipality"]) | set(sorted_sc.tail(5)["municipality"])
            if highlight_muni:
                label_munis.add(highlight_muni)
            scatter_df["label"] = scatter_df["municipality"].where(scatter_df["municipality"].isin(label_munis), "")
            scatter_df["highlighted"] = scatter_df["municipality"] == (highlight_muni or "")
            base = alt.Chart(scatter_df).encode(
                x=alt.X("metric_value:Q", title=row["label"]),
                y=alt.Y("vote_share:Q", title="Vote share (%)"),
                tooltip=[
                    alt.Tooltip("municipality:N", title="Municipality"),
                    alt.Tooltip("metric_value:Q", title=row["label"]),
                    alt.Tooltip("vote_share:Q", title="Vote share (%)"),
                ]
            )
            points_normal = base.transform_filter(
                alt.datum.highlighted == False
            ).mark_circle(size=55, color="#22d966", opacity=0.65)
            points_highlight = base.transform_filter(
                alt.datum.highlighted == True
            ).mark_circle(size=120, color="#e63946", opacity=1.0)
            labels = base.mark_text(align="left", dx=5, dy=-4, fontSize=10, color="#5a5a6a").encode(
                text="label:N"
            )
            st.altair_chart((points_normal + points_highlight + labels).properties(height=350), use_container_width=True)
            with st.expander(f"See all {len(ranked_data)} municipalities"):
                render_compact_dataframe(ranked_data.sort_values("Vote %", ascending=False))

        # ── Case B: multiple metrics, 1 party → "what predicts this party?" ──
        elif len(s_parties) == 1 and len(s_metric_keys) > 1:
            party = s_parties[0]
            valid_results = [r for r in results if r["valid"]]
            if not valid_results:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">NO VALID RESULT</div>'
                    '<div class="headline">No valid correlation result available</div>'
                    '<div class="body">None of the selected factor-party combinations produced a valid correlation value. No strongest signal is shown.</div>'
                    '</div>', unsafe_allow_html=True
                )
                st.stop()
            ranked = sorted(valid_results, key=lambda x: abs(float(x["r"])), reverse=True)
            # Bar chart first — most informative view
            summary = pd.DataFrame([{
                "Factor": r["factor"],
                "Label": METRIC_SHORT_LABELS.get(r["factor"], r["factor"]),
                "r": r["r"],
                "Strength": r["strength"],
            } for r in ranked])
            st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>", unsafe_allow_html=True)
            render_bar_chart(summary, "Label", "r", tooltip_label="Factor", full_label_col="Factor")
            # Compute inter-factor overlaps
            overlap_notes = {}
            if len(s_metric_keys) >= 2:
                factor_series = {}
                for mk in s_metric_keys:
                    m_info = next(m for m in METRIC_OPTIONS if m[0] == mk)
                    ms = get_metric_series(m_info[2], s_year, pop_df, income_df, social_df, crime_df, cars_df, divorce_df, commute_df, employment_df, education_df, age65_df, turnout_df, immigration_df, density_df, unemployment_df, owner_occupied_df, detached_houses_df, one_person_households_df)
                    if not ms.empty:
                        factor_series[mk] = ms.set_index("municipality")["metric"]
                rank_order = {r["factor"]: i for i, r in enumerate(ranked)}
                factor_names = list(factor_series.keys())
                for fi, fa in enumerate(factor_names):
                    for fb in factor_names[fi+1:]:
                        combined = pd.DataFrame({"a": factor_series[fa], "b": factor_series[fb]}).dropna()
                        if len(combined) >= 10:
                            inter_r = round(float(combined["a"].corr(combined["b"])), 2)
                            if abs(inter_r) >= 0.60:
                                higher = fa if rank_order.get(fa, 999) < rank_order.get(fb, 999) else fb
                                lower = fb if higher == fa else fa
                                if lower not in overlap_notes:
                                    overlap_notes[lower] = f"Note: {lower} and {higher} tend to move together across municipalities (r = {inter_r:.2f})."
            # Show a finding box for every factor with |r| ≥ 0.30
            meaningful = [r for r in ranked if abs(float(r["r"])) >= 0.30]
            no_pattern = [r for r in ranked if abs(float(r["r"])) < 0.30]
            if not meaningful:
                meaningful = [ranked[0]]  # always show at least the top one
            for i, row in enumerate(meaningful):
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                    row["r"], row["factor"], row["label"], party, s_year, row["merged"], party_name_mode)
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note),
                            unsafe_allow_html=True)
            if overlap_notes:
                for note_text in overlap_notes.values():
                    st.markdown(
                        f"<p style='font-size:0.72rem;color:#8888a0;margin-top:0.3rem;margin-bottom:0.3rem;'>"
                        f"{note_text}</p>",
                        unsafe_allow_html=True
                    )
            if no_pattern:
                no_pattern_names = ", ".join(r["factor"] for r in no_pattern)
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>"
                    f"No pattern found for: {no_pattern_names} (abs(r) below 0.30).</p>",
                    unsafe_allow_html=True
                )
            how_to_read()
            with st.expander("See full ranking table"):
                render_compact_dataframe(summary[["Factor", "r", "Strength"]])

        # ── Case C: multiple parties, 1 metric → "which parties link to X?" ──
        elif len(s_parties) > 1 and len(s_metric_keys) == 1:
            valid_results = [r for r in results if r["valid"]]
            if not valid_results:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">NO VALID RESULT</div>'
                    '<div class="headline">No valid correlation result available</div>'
                    '<div class="body">None of the selected factor-party combinations produced a valid correlation value. No strongest signal is shown.</div>'
                    '</div>', unsafe_allow_html=True
                )
                st.stop()
            ranked = sorted(valid_results, key=lambda x: abs(float(x["r"])), reverse=True)
            # Bar chart first
            summary = pd.DataFrame([{
                "Party": format_party_name(r["party"], mode=party_name_mode, compact=True, include_code=True),
                "Party_full": format_party_name(r["party"], mode=party_name_mode, include_code=True),
                "r": r["r"],
                "Strength": r["strength"],
            } for r in ranked])
            st.markdown("<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>", unsafe_allow_html=True)
            render_bar_chart(summary, "Party", "r", tooltip_label="Party", full_label_col="Party_full")
            # Finding box for every party with |r| ≥ 0.30
            meaningful = [r for r in ranked if abs(float(r["r"])) >= 0.30]
            no_pattern = [r for r in ranked if abs(float(r["r"])) < 0.30]
            if not meaningful:
                meaningful = [ranked[0]]
            for i, row in enumerate(meaningful):
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                    row["r"], row["factor"], row["label"], row["party"], s_year, row["merged"], party_name_mode)
                st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note),
                            unsafe_allow_html=True)
            if no_pattern:
                no_pattern_names = ", ".join(format_party_name(r["party"], mode=party_name_mode, compact=True) for r in no_pattern)
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>"
                    f"No pattern found for: {no_pattern_names} (abs(r) below 0.30).</p>",
                    unsafe_allow_html=True
                )
            how_to_read()
            with st.expander("See full ranking table"):
                render_compact_dataframe(summary[["Party_full", "r", "Strength"]], rename_map={"Party_full": "Party"})

        # ── Case D: multiple parties + multiple metrics → matrix ──────────────
        else:
            valid_results = [r for r in results if r["valid"]]
            if not valid_results:
                st.markdown(
                    '<div class="finding weak">'
                    '<div class="strength-tag">NO VALID RESULT</div>'
                    '<div class="headline">No valid correlation result available</div>'
                    '<div class="body">None of the selected factor-party combinations produced a valid correlation value. No strongest signal is shown.</div>'
                    '</div>', unsafe_allow_html=True
                )
                st.stop()
            top = max(valid_results, key=lambda x: abs(float(x["r"])))
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_finding(
                top["r"], top["factor"], top["label"], top["party"], s_year, top["merged"], party_name_mode)
            st.markdown(
                "<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.5rem;'>"
                "Showing highest correlation across selected factors and parties. "
                "Use the full correlation table to inspect all results.</p>",
                unsafe_allow_html=True
            )
            st.markdown(finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note,
                                     context_label=f"Strongest signal: {format_party_name(top['party'], mode=party_name_mode, compact=True)} × {top['factor']}"),
                        unsafe_allow_html=True)
            other_count = len(valid_results) - 1
            if other_count > 0:
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.3rem;'>"
                    f"{other_count} other signal{'s' if other_count > 1 else ''} exist — see full correlation table.</p>",
                    unsafe_allow_html=True
                )
            how_to_read()
            with st.expander("See full correlation table"):
                flat = [{"Party": format_party_name(r["party"], mode=party_name_mode, include_code=True), "Factor": r["factor"], "r": r["r"]} for r in valid_results]
                flat_df = pd.DataFrame(flat).assign(abs_r=lambda d: d["r"].abs()).sort_values("abs_r", ascending=False).drop(columns="abs_r").reset_index(drop=True)
                render_compact_dataframe(flat_df)

# ── Compare municipalities ────────────────────────────────────────────────────

elif page == "Compare municipalities":
    st.markdown("<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>Danish Politics Data</p>", unsafe_allow_html=True)
    st.title("Compare two municipalities")
    st.markdown(
        "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:1.5rem;'>"
        "Pick two municipalities. See how their voting patterns and socioeconomic profiles differ."
        "</p>", unsafe_allow_html=True
    )

    all_munis = sorted(mun["municipality"].unique())
    col1, col2 = st.columns(2)
    with col1:
        mun_a = st.selectbox("Municipality A", all_munis, index=0)
    with col2:
        mun_b = st.selectbox("Municipality B", all_munis, index=1)

    if mun_a == mun_b:
        st.warning("Select two different municipalities.")
        st.stop()

    # ── Voting patterns ───────────────────────────────────────────────────────
    st.markdown("## Voting patterns")

    votes_a = mun[mun["municipality"] == mun_a].pivot_table(index="year", columns="party", values="share")
    votes_b = mun[mun["municipality"] == mun_b].pivot_table(index="year", columns="party", values="share")

    # Parties where they differ most on average
    common = votes_a.columns.intersection(votes_b.columns)
    diff_abs = (votes_a[common] - votes_b[common]).abs()
    top_parties = diff_abs.mean().sort_values(ascending=False).head(6).index.tolist()

    gap_df = (votes_a[top_parties] - votes_b[top_parties]).round(1)
    gap_chart_df = pd.DataFrame({
        "Party": [format_party_name(p, mode=party_name_mode, compact=True, include_code=True) for p in top_parties],
        "Party_full": [format_party_name(p, mode=party_name_mode, include_code=True) for p in top_parties],
        "Gap": [gap_df[p].mean() for p in top_parties],
    })

    st.markdown(
        f"<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.5rem;'>"
        f"Percentage point gap in vote share: <strong>{mun_a}</strong> minus <strong>{mun_b}</strong>. "
        f"Positive bar = {mun_a} votes more for that party. Negative = {mun_b} does.</p>",
        unsafe_allow_html=True
    )
    render_bar_chart(gap_chart_df, "Party", "Gap", tooltip_label="Party", full_label_col="Party_full")

    # Biggest single gap
    max_gap_row = gap_chart_df.iloc[gap_chart_df["Gap"].abs().idxmax()]
    max_gap_party = max_gap_row["Party_full"]
    max_gap_val = round(float(max_gap_row["Gap"]), 1)
    direction = mun_a if max_gap_val > 0 else mun_b
    st.markdown(
        f'<div class="finding moderate">'
        f'<div class="headline">Biggest difference: {max_gap_party}</div>'
        f'<div class="body">On average across all elections, <strong>{direction}</strong> votes '
        f'<strong>{abs(max_gap_val):.1f} percentage points more</strong> for {max_gap_party} than the other municipality.</div>'
        f'<div class="footnote">Based on {MUNICIPAL_ELECTION_RANGE_LABEL} municipality elections · Danmarks Statistik (2007–2022) + official VALG bridge (2026)</div>'
        f'</div>', unsafe_allow_html=True
    )

    with st.expander("See full vote history for both municipalities"):
        display_columns = [format_party_name(p, mode=party_name_mode, compact=True, include_code=True) for p in top_parties]
        votes_a_display = votes_a[top_parties].round(1).copy()
        votes_b_display = votes_b[top_parties].round(1).copy()
        votes_a_display.columns = display_columns
        votes_b_display.columns = display_columns
        tab_a, tab_b = st.tabs([mun_a, mun_b])
        with tab_a:
            st.markdown(f"**{mun_a}**")
            st.dataframe(votes_a_display, use_container_width=True)
        with tab_b:
            st.markdown(f"**{mun_b}**")
            st.dataframe(votes_b_display, use_container_width=True)

    # ── Socioeconomic profile ─────────────────────────────────────────────────
    st.markdown("## Socioeconomic profile")
    st.markdown(
        "<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.8rem;'>"
        "Current municipality profile using the most recent available data for each metric. "
        "Years may differ by metric. Per-1,000 and percentage factors are shown directly from the normalized public factor layer."
        "</p>", unsafe_allow_html=True
    )

    def latest_val(df, municipality, year_col="year", val_col="value"):
        sub = df[df["municipality"] == municipality]
        if sub.empty: return None, None
        yr = sub[year_col].max()
        v = sub[sub[year_col] == yr][val_col]
        return (float(v.values[0]) if len(v) > 0 else None), int(yr)

    def pop_for(municipality):
        sub = pop_df[pop_df["municipality"] == municipality].sort_values(["year", "reference_period"], ascending=False)
        if sub.empty: return None
        return float(sub["population"].values[0])

    pop_a = pop_for(mun_a)
    pop_b = pop_for(mun_b)

    profile_rows = []

    pop_value_a, pop_year = latest_val(pop_df, mun_a, val_col="population")
    pop_value_b, _ = latest_val(pop_df, mun_b, val_col="population")
    if pop_value_a is not None and pop_value_b is not None:
        profile_rows.append({"Metric": "Population", mun_a: f"{pop_value_a:,.0f}", mun_b: f"{pop_value_b:,.0f}", "Year": pop_year})

    edu_a, yr = latest_val(education_df, mun_a)
    edu_b, _  = latest_val(education_df, mun_b)
    if edu_a is not None and edu_b is not None:
        profile_rows.append({"Metric": "Higher education (%)", mun_a: f"{edu_a:.1f}%", mun_b: f"{edu_b:.1f}%", "Year": yr})

    inc_a, yr = latest_val(income_df, mun_a)
    inc_b, _  = latest_val(income_df, mun_b)
    if inc_a is not None and inc_b is not None:
        profile_rows.append({"Metric": "Avg. disposable income (DKK)", mun_a: f"{inc_a:,.0f}", mun_b: f"{inc_b:,.0f}", "Year": yr})

    commute_a, yr = latest_val(commute_df, mun_a)
    commute_b, _  = latest_val(commute_df, mun_b)
    if commute_a is not None and commute_b is not None:
        profile_rows.append({"Metric": "Avg. commute distance (km)", mun_a: f"{commute_a:.1f}", mun_b: f"{commute_b:.1f}", "Year": yr})

    emp_a, yr = latest_val(employment_df, mun_a)
    emp_b, _  = latest_val(employment_df, mun_b)
    if emp_a is not None and emp_b is not None:
        profile_rows.append({"Metric": "Full-time employees per 1,000", mun_a: f"{emp_a:.1f}", mun_b: f"{emp_b:.1f}", "Year": yr})

    soc_a, yr = latest_val(social_df, mun_a)
    soc_b, _  = latest_val(social_df, mun_b)
    if soc_a is not None and soc_b is not None:
        profile_rows.append({"Metric": "Welfare recipients per 1,000", mun_a: f"{soc_a:.1f}", mun_b: f"{soc_b:.1f}", "Year": yr})

    cr_a, yr = latest_val(crime_df, mun_a)
    cr_b, _  = latest_val(crime_df, mun_b)
    if cr_a is not None and cr_b is not None:
        profile_rows.append({"Metric": "Reported crimes per 1,000", mun_a: f"{cr_a:.1f}", mun_b: f"{cr_b:.1f}", "Year": yr})

    car_a, yr = latest_val(cars_df, mun_a)
    car_b, _  = latest_val(cars_df, mun_b)
    if car_a is not None and car_b is not None:
        profile_rows.append({"Metric": "Passenger cars per 1,000", mun_a: f"{car_a:.1f}", mun_b: f"{car_b:.1f}", "Year": yr})

    div_a, yr = latest_val(divorce_df, mun_a)
    div_b, _  = latest_val(divorce_df, mun_b)
    if div_a is not None and div_b is not None:
        profile_rows.append({"Metric": "Divorces per 1,000", mun_a: f"{div_a:.1f}", mun_b: f"{div_b:.1f}", "Year": yr})

    age_a, yr = latest_val(age65_df, mun_a)
    age_b, _  = latest_val(age65_df, mun_b)
    if age_a is not None and age_b is not None:
        profile_rows.append({"Metric": "Aged 65+ (%)", mun_a: f"{age_a:.1f}%", mun_b: f"{age_b:.1f}%", "Year": yr})

    turnout_a, yr = latest_val(turnout_df, mun_a)
    turnout_b, _ = latest_val(turnout_df, mun_b)
    if turnout_a is not None and turnout_b is not None:
        profile_rows.append({"Metric": "Turnout (%)", mun_a: f"{turnout_a:.1f}%", mun_b: f"{turnout_b:.1f}%", "Year": yr})

    imm_a, yr = latest_val(immigration_df, mun_a)
    imm_b, _ = latest_val(immigration_df, mun_b)
    if imm_a is not None and imm_b is not None:
        profile_rows.append({"Metric": "Residents without Danish origin (%)", mun_a: f"{imm_a:.1f}%", mun_b: f"{imm_b:.1f}%", "Year": yr})

    dens_a, yr = latest_val(density_df, mun_a)
    dens_b, _ = latest_val(density_df, mun_b)
    if dens_a is not None and dens_b is not None:
        profile_rows.append({"Metric": "Population density (per km²)", mun_a: f"{dens_a:.1f}", mun_b: f"{dens_b:.1f}", "Year": yr})

    unemp_a, yr = latest_val(unemployment_df, mun_a)
    unemp_b, _ = latest_val(unemployment_df, mun_b)
    if unemp_a is not None and unemp_b is not None:
        profile_rows.append({"Metric": "Unemployment (%)", mun_a: f"{unemp_a:.1f}%", mun_b: f"{unemp_b:.1f}%", "Year": yr})

    owner_a, yr = latest_val(owner_occupied_df, mun_a)
    owner_b, _ = latest_val(owner_occupied_df, mun_b)
    if owner_a is not None and owner_b is not None:
        profile_rows.append({"Metric": "Owner-occupied dwellings (%)", mun_a: f"{owner_a:.1f}%", mun_b: f"{owner_b:.1f}%", "Year": yr})

    detached_a, yr = latest_val(detached_houses_df, mun_a)
    detached_b, _ = latest_val(detached_houses_df, mun_b)
    if detached_a is not None and detached_b is not None:
        profile_rows.append({"Metric": "Detached/farmhouse dwellings (%)", mun_a: f"{detached_a:.1f}%", mun_b: f"{detached_b:.1f}%", "Year": yr})

    one_person_a, yr = latest_val(one_person_households_df, mun_a)
    one_person_b, _ = latest_val(one_person_households_df, mun_b)
    if one_person_a is not None and one_person_b is not None:
        profile_rows.append({"Metric": "One-person households (%)", mun_a: f"{one_person_a:.1f}%", mun_b: f"{one_person_b:.1f}%", "Year": yr})

    if profile_rows:
        render_profile_cards(profile_rows, mun_a, mun_b)
        with st.expander("See profile as full table"):
            st.dataframe(pd.DataFrame(profile_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Socioeconomic data not available for this combination.")

    st.markdown(
        "<p style='font-size:0.68rem;color:#aaaabc;margin-top:1rem;'>"
        "Source: Danmarks Statistik (CC 4.0 BY) · Correlation ≠ causation</p>",
        unsafe_allow_html=True
    )

# ── By Municipality ───────────────────────────────────────────────────────────

elif page == "By Municipality":
    st.subheader("By Municipality")
    st.markdown(
        "<p style='color:#6a6a7a;font-size:0.82rem;margin-bottom:1.2rem;'>"
        "Pick a party and a year. See all 98 municipalities ranked by vote share."
        "</p>", unsafe_allow_html=True
    )
    col1, col2 = st.columns(2)
    with col1:
        year  = st.selectbox("Election year", sorted(mun["year"].unique(), reverse=True))
    with col2:
        parties_for_year = available_parties_for_year(year, mun)
        party = st.selectbox("Party", parties_for_year, format_func=lambda p: format_party_name(p, mode=party_name_mode, include_code=True))

    filtered = mun[(mun["year"] == year) & (mun["party"] == party)].sort_values("share", ascending=False)
    top    = filtered.iloc[0]
    bottom = filtered.iloc[-1]
    avg    = filtered["share"].mean()

    st.markdown(
        f"<p style='font-size:0.82rem;color:#3a3a4a;margin-bottom:0.8rem;'>"
        f"<strong>Highest:</strong> {top['municipality']} ({top['share']}%) &nbsp;·&nbsp; "
        f"<strong>Lowest:</strong> {bottom['municipality']} ({bottom['share']}%) &nbsp;·&nbsp; "
        f"<strong>Avg:</strong> {avg:.1f}%</p>",
        unsafe_allow_html=True
    )
    render_compact_dataframe(
        filtered[["municipality","share"]].rename(columns={"municipality": "Municipality", "share":"Vote %"})
    )
    with st.expander("Show full municipality bar chart"):
        st.bar_chart(filtered.set_index("municipality")["share"])

# ── National trends ───────────────────────────────────────────────────────────

elif page == "National trends":
    st.subheader("National vote share, 1953–2022")
    st.markdown(
        "<p style='color:#6a6a7a;font-size:0.82rem;margin-bottom:1rem;'>"
        "25 elections across 70 years. Select which parties to compare."
        "</p>", unsafe_allow_html=True
    )
    parties_nat = ordered_national_parties(nat)
    default_nat = [party for party in top_national_parties(nat, top_n=5) if party in parties_nat]
    selected = st.multiselect("Parties", parties_nat,
                              default=default_nat,
                              format_func=lambda p: format_party_code(p, mode=party_name_mode, compact=True))
    if selected:
        chart_df = nat[nat["party"].isin(selected)].copy()
        chart_df["party_label"] = chart_df["party"].apply(lambda code: format_party_code(code, mode=party_name_mode, compact=True))
        pivot = chart_df.pivot_table(index="year", columns="party_label", values="share")
        pivot = pivot.rename(columns=lambda code: format_party_code(code, mode=party_name_mode, compact=True))
        render_national_trend_chart(chart_df, "year", "party_label", "share")
        table = pivot.round(1).astype(object).where(pivot.notna(), "—")
        st.dataframe(table, use_container_width=True)

# ── About & sources ───────────────────────────────────────────────────────────

elif page == "About & sources":
    st.subheader("About & Sources")
    st.markdown("""
National Danish election results 1953–2022, plus municipality-level vote share 2007–2026, cross-referenced with a growing set of municipality-level indicators from Danmarks Statistik.
Built for journalists and researchers. No login required. All data is public and open-licensed (CC 4.0 BY).

Built by [Hedegreen Research](https://hedegreenresearch.com).

**Method note**
- Correlation ≠ causation.
- Some municipality indicators use the most recent available year for that metric, so years can differ in profile-style views.
- The 2026 municipality vote-share layer is currently bridged from the official `VALG` export before the familiar Statistikbanken municipality tables catch up.
- Wave 2 commute and housing factors are year-aware by design. Housing coverage starts in `2010`, and owner-occupied housing currently skips `2021–2022` because DST keeps those years closed in `BOL101`.
- `Divorces` stays withheld from the public factor layer until the municipality-total source path is trustworthy.
- Party name mode changes only labels in the interface. Data values and party IDs stay the same.
    """)
    st.subheader("Data sources")
    st.markdown("""
<div class="source-item"><strong>FVPANDEL</strong> — Party vote share per municipality, 2007–2022. Danmarks Statistik</div>
<div class="source-item"><strong>VALG public export</strong> — Official 2026 fine-count results aggregated from polling-area level to municipality level for the public bridge layer.</div>
<div class="source-item"><strong>Straubinger/folketingsvalg</strong> — National vote counts, 1953–2022. GitHub</div>
<div class="source-item"><strong>INDKP101</strong> — Avg. disposable income per municipality, 1987–2024. Danmarks Statistik</div>
<div class="source-item"><strong>AUK01</strong> — Social assistance recipients per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>STRAF11</strong> — Reported crimes per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>BIL707</strong> — Passenger cars per municipality, 2007–present. Danmarks Statistik</div>
<div class="source-item"><strong>FOLK1AM</strong> — Population per municipality. Danmarks Statistik</div>
<div class="source-item"><strong>FVKOM</strong> — Municipality turnout can be derived from valid + invalid votes versus number of voters. Danmarks Statistik</div>
<div class="source-item"><strong>FOLK1E</strong> — Immigration share at municipality level via herkomst categories. Danmarks Statistik</div>
<div class="source-item"><strong>ARE207</strong> — Area per municipality for density calculations. Danmarks Statistik</div>
<div class="source-item"><strong>AUP02</strong> — Unemployment rate per municipality. Danmarks Statistik</div>
<div class="source-item"><strong>AFSTB4</strong> — Average commute distance by municipality (employed total, ultimo November). Danmarks Statistik</div>
<div class="source-item"><strong>BOL101</strong> — Owner-occupied share within occupied dwellings. Danmarks Statistik</div>
<div class="source-item"><strong>BOL103</strong> — Detached-house share and one-person-household share within occupied dwellings. Danmarks Statistik</div>
    """, unsafe_allow_html=True)
