# Swedish Politics Data

> Sorry — the live Streamlit app is not functioning reliably right now. If you want to debug it, investigate the code, or send a fix, you are very welcome.

A public reading surface for Swedish Riksdag results at municipality level, paired with a deliberately narrow Sweden-safe factor layer.

This repo is the Sweden-only public surface extracted from the internal World-politics-data engine. It keeps the public app shell, Sweden data pack, Sweden scope notes, and Sweden-only documentation without exposing the internal multi-country registry.

## Public door

- TID door: `https://hedegreenresearch.com/tid/swedish-politics-data/`
- GitHub repo: `https://github.com/DennisHedegreen/swedish-politics-data`

## Current scope

- Election type: `Riksdag`
- Municipality election years: `2014`, `2018`, `2022`
- National trend years: `2002`, `2006`, `2010`, `2014`, `2018`, `2022`
- Public geography: `municipality`
- Current public factors: `population`, `age65`, `education`, `income`, `turnout`, `population density`, `cars`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## What this repo is not

- Not a multi-country politics product
- Not a prediction model
- Not an explanation engine
- Not a broader politics product beyond the declared Sweden scope
- Not a full Sweden election archive beyond the declared Riksdag scope

## Intentionally missing

- `Regional` and `municipal` election layers
- `Employment`, `unemployment`, and `welfare` as public factors until year-coverage and semantics are strong enough
- Housing and forest layers until they survive source and coverage review

## Data sources

- Election source: `Valmyndigheten municipality election exports for 2014, 2018, and 2022 + Statistics Sweden municipal indicators`
- Statistics source: `Statistics Sweden`

## Repo structure

```text
app.py               Single-country public wrapper
engine_app.py        Shared app shell extracted from the internal engine
correlation_utils.py Shared correlation helpers
country_registry.py  Single-country registry for this public surface
sweden/               Country data pack and scope notes
provenance/          Public-safe manifests copied from the internal engine
tests/               Country-surface smoke tests
```

## Source of truth

This repo is a public country surface. The shared internal source tree still exists separately and remains the source of truth for shell changes and future extraction work.
