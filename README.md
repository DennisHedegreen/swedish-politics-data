# Swedish Politics Data

Swedish Politics Data is a public Streamlit tool for reading Swedish Riksdag election results at municipality level beside a deliberately narrow Sweden-safe factor layer. It helps journalists, analysts, and curious readers see where vote shares move together with measurable local conditions, without treating those patterns as explanations.

## Public Door

- TID door: `https://hedegreenresearch.com/tid/swedish-politics-data/`
- Live app: `https://swedish-politics-data-s7o3pezehv8somxirp8pde.streamlit.app/`
- GitHub repo: `https://github.com/DennisHedegreen/swedish-politics-data`

## Declared Scope

- Country: Sweden
- Election type: Riksdag
- Unit of analysis: municipality
- Municipality election years: `2014`, `2018`, `2022`
- National trend years: `2002`, `2006`, `2010`, `2014`, `2018`, `2022`
- Public factors: population, age 65+, education, income, turnout, population density, cars, rented accommodation, one-/two-dwelling buildings, employment (2022 only), unemployment (2022 only)

This repo is Sweden-only and Riksdag-only. It does not cover Swedish regional or municipal elections.

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

## How To Read Results

Positive correlation means higher party vote share tends to appear in municipalities where the selected factor is higher. Negative correlation means higher party vote share tends to appear where the selected factor is lower. The result is ranked by absolute correlation strength, so `-0.62` is treated as stronger than `0.31`.

Example: if a party has `r = -0.54` with rented accommodation in 2022, a responsible reading is: "The party tended to have lower vote shares in municipalities with higher rented-accommodation shares in this election year." It is not: "Rental housing caused voters to reject this party."

See [HOW_TO_READ_RESULTS.md](HOW_TO_READ_RESULTS.md) and [METHODOLOGY.md](METHODOLOGY.md) before using results in public claims.

## Public Sources

- Election source: `Valmyndigheten municipality election exports for 2014, 2018, and 2022`
- Statistics source: `Statistics Sweden`
- Public-safe provenance notes: [provenance/](provenance/)

## Repo Structure

```text
app.py               Single-country public wrapper
engine_app.py        Shared app shell extracted from the internal engine
correlation_utils.py Compatibility import for correlation helpers
core/                Runtime, presentation, correlation, and failure-state helpers
country_registry.py  Sweden-only public registry
sweden/              Sweden data pack and scope notes
provenance/          Public-safe manifests
tests/               Public-surface and logic contract tests
```

## Source Of Truth

This repo is a public country surface. The shared internal source tree still exists separately and remains the source of truth for shell changes and future extraction work. Public claims should cite this repo, its provenance notes, and the named public sources, not private working files.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
