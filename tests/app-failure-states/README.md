# App Failure States

Lille test-rum for appens tomme eller ufuldstændige data-pack scenarier.

Formål:

- bekræfte hvad appen bør sige når et land mangler valgdata
- bekræfte hvad appen bør sige når factor-filer findes men er tomme
- holde `ready` vs `partial` vs `missing` tydeligt adskilt
- kunne starte appen i en bevidst tom Sweden-tilstand uden at røre de rigtige data

Fixtures ligger i `fixtures/`.

Kør kun denne testfil:

```bash
cd "/home/dennis-hedegreen/hedegreen research/World-politics-data"
./.venv/bin/python -m unittest tests.test_app_failure_states
```

Kør hele testpakken:

```bash
cd "/home/dennis-hedegreen/hedegreen research/World-politics-data"
./.venv/bin/python -m unittest discover -s tests -p 'test_*'
```

Live app-fixtures:

```bash
cd "/home/dennis-hedegreen/hedegreen research/World-politics-data"
source .venv/bin/activate

WPD_DATA_VARIANT="sweden-no-election-data" streamlit run app.py
WPD_DATA_VARIANT="sweden-no-factor-data" streamlit run app.py
```

De to varianter gør dette:

- `sweden-no-election-data`: Sweden tæller ikke som et eksponeret public country pack og bør derfor forsvinde fra country-selector
- `sweden-no-factor-data`: Sweden tæller heller ikke som et eksponeret public country pack, fordi public factor layer mangler

Hvis du vil teste kun Sweden-profilet:

```bash
WPD_DATA_VARIANT="sweden-no-election-data" WPD_EXPOSE_COUNTRIES="sweden" streamlit run app.py
```

I den situation bør appen sige:

- `No public country data packs are currently exposed for this app profile.`
