# Deploy

Sweden public deploy checklist.

## Local smoke

```bash
pip install -r requirements.txt
streamlit run app.py
```

Check:

- `Explore`
- `Compare municipalities`
- `By Municipality`
- `National trends`
- `About & Sources`

## Public deploy shape

- App title: `Swedish Politics Data`
- Country exposure: `Sweden` only
- No public country selector
- No other-country wording in the visible surface

## Before pushing live

- confirm the sweden data pack exists and loads cleanly
- confirm the latest screenshots still match the current UI
- confirm the TID door wording is still true
- confirm the repo README and methodology still match the live app scope
