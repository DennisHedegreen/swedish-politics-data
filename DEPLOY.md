# Deploy

Sweden public deploy checklist.

Primary target:

- Platform: `Streamlit Community Cloud`
- Repo: `DennisHedegreen/swedish-politics-data`
- Branch: `main`
- Entrypoint: `app.py`
- Suggested app URL: `swedish-politics-data.streamlit.app`
- Secrets: none required for the current public build

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

## Streamlit Community Cloud

Official deploy flow:

- `Create app`
- repository: `DennisHedegreen/swedish-politics-data`
- branch: `main`
- main file path: `app.py`
- optional custom subdomain: `swedish-politics-data`
- Python version: leave default `3.12` unless the platform forces a different supported version
- secrets: leave empty

After first deploy:

- verify `Explore`
- verify `Compare municipalities`
- verify `By Municipality`
- verify `National trends`
- verify `About & Sources`
- copy the final live URL into the Sweden TID door
- replace the current repo-first note in TID with a live-app note

## Before pushing live

- confirm the Sweden data pack exists and loads cleanly
- confirm the latest screenshots still match the current UI
- confirm the TID door wording is still true
- confirm the repo README and methodology still match the live app scope
