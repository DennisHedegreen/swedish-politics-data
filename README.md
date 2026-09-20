# Swedish Politics Data

Swedish Politics Data compares Swedish Riksdag election vote shares with municipality-level structural factors. It is built for finding reporting leads and visible patterns, not for proving why people vote as they do.

This repo is the country-only public surface for the declared scope.

## Public Door

- TID door: [hedegreenresearch.com/tid/swedish-politics-data](https://hedegreenresearch.com/tid/swedish-politics-data/)
- Live app: [swedish-politics-data Streamlit app](https://swedish-politics-data-s7o3pezehv8somxirp8pde.streamlit.app/)
- GitHub repo: [DennisHedegreen/swedish-politics-data](https://github.com/DennisHedegreen/swedish-politics-data)

## Declared Scope

- Country: Sweden
- Election type: Riksdag
- Unit of analysis: municipality
- Municipality election years: `2014`, `2018`, `2022`, `2026`
- National trend years: `2002`, `2006`, `2010`, `2014`, `2018`, `2022`, `2026`
- Public geography: `municipality`
- Factors: Population, Age 65+, Education, Income, Turnout, Population density, Cars, Rented accommodation, One-/two-dwelling buildings, Employment, Unemployment

This repo is the Sweden-only public surface extracted from the internal World-politics-data engine. It keeps the public app shell, Sweden data pack, Sweden scope notes, and Sweden-only documentation without exposing the internal multi-country registry.

## What You Can Do

- Compare party vote share with one or more municipality-level factors.
- Read whether the relationship is positive, negative, weak, moderate, or strong.
- Inspect high and low municipalities before turning a pattern into a claim.
- Use the result as a lead for reporting, not as the final story.

## What Not To Infer

- Correlation is not causation.
- Municipality-level patterns do not describe individual voters.
- A strong result does not prove why people voted as they did.
- A weak or missing result does not prove that a factor is irrelevant.
- The app is not a prediction model, campaign tool, or causal engine.

This repo is Sweden-only and Riksdag-only. It does not cover regional or municipal election layers.

## How To Read Results

Positive correlation means higher party vote share tends to appear in municipalities where the selected factor is higher. Negative correlation means higher party vote share tends to appear where the selected factor is lower. The result is ranked by absolute correlation strength, so `-0.62` is treated as stronger than `0.31`.

Example: if a party has `r = 0.58` with population density, a responsible reading is: "The party tended to have higher vote shares in denser municipalities in this election year." It is not: "Density made voters choose this party."

## Quick Case

A journalist could start with a strong party-factor result, open the high and low municipality tables, and ask a concrete reporting question: is this a real geographic pattern, a party-history pattern, or just a one-year artifact? The app gives the lead. The reporting still has to do the verification.

See [METHODOLOGY.md](METHODOLOGY.md) before using results in public claims.

## Boundary

- Not a multi-country politics product
- Not a prediction model
- Not an explanation engine
- Not a broader politics product beyond the declared Sweden scope
- Not a full Sweden election archive beyond the declared Riksdag scope

Intentionally missing:

- `Regional` and `municipal` election layers
- `Welfare` as a public factor until coverage and semantics are strong enough
- Housing and forest layers until they survive source and coverage review

## Public Sources

- Election source: `Valmyndigheten municipality election exports for 2014, 2018, and 2022 + Statistics Sweden municipal indicators`
- Statistics source: `Statistics Sweden`
- Provenance notes: [provenance/](provenance/)

## Repo Structure

```text
app.py               Single-country public wrapper
engine_app.py        Shared app shell extracted from the internal engine
correlation_utils.py Compatibility import for correlation helpers
core/                Runtime, presentation, correlation, and failure-state helpers
country_registry.py  Sweden-only public registry
sweden/              Country data pack and scope notes
provenance/          Public-safe manifests
tests/               Country-surface and logic contract tests
```

## Source Of Truth

This repo is a public country surface. The shared internal source tree still exists separately and remains the source of truth for shell changes and future extraction work. Public claims should cite this repo, its provenance notes, and the named public sources, not private working files.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
