from __future__ import annotations

import streamlit as st


APP_CSS = """
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

.metric-tile {
    border: 1px solid #e0e0e8; padding: 1.1rem 1.2rem; margin-bottom: 0.5rem;
    background: #fff; line-height: 1.5;
}
.metric-tile.selected { border-color: #22d966; background: #f4fef8; }
.metric-tile .q { font-size: 0.92rem; font-weight: 400; color: #0d0d14; margin-bottom: 0.2rem; }
.metric-tile .hint { font-size: 0.72rem; color: #8888a0; }

.step-label {
    font-size: 0.6rem; font-weight: 500; letter-spacing: 0.14em;
    text-transform: uppercase; color: #aaaabc; margin-bottom: 0.5rem;
}

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
"""


def apply_global_styles() -> None:
    st.markdown(APP_CSS, unsafe_allow_html=True)
