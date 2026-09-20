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

## Live Streamlit Preview

- Live app: [swedish-politics-data Streamlit app](https://swedish-politics-data-s7o3pezehv8somxirp8pde.streamlit.app/)

## Streamlit Community Cloud settings

Current Streamlit Community Cloud settings:

- Repository: `DennisHedegreen/swedish-politics-data`
- Branch: `main`
- Main file path: `app.py`
- Python version: `3.12`
- Secrets: none
- Suggested app URL: leave blank and use the generated URL

Deploy privacy:

- The GitHub repo is public.
- Keep the Streamlit app public after public launch.

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
