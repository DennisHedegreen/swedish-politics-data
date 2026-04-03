# Methodology — Swedish Politics Data

## What this tool is

A public reading surface for Swedish politics data. It pairs Riksdag election results with a municipality-safe public factor layer and surfaces patterns without pretending they are explanations.

## What this tool is not

- It is not a prediction model.
- It is not a political recommendation engine.
- Correlation is not causation.
- Municipal-level patterns do not describe individual voters.

## Public scope

- Country: `Sweden`
- Election type: `Riksdag`
- Public geography: `municipality`
- Public geography count: `290`
- Current public factors: `Population, Age 65+, Education, Income, Turnout, Population density, Cars`

## Data handling rules

- Missing data is shown honestly rather than backfilled.
- Public factors only enter the surface when municipality coverage and semantics are good enough.
- Party label mode only changes displayed labels. Data values and party IDs remain the same.
- The public layer stays narrower than the internal engine on purpose.

## Sources

- Election source: `Valmyndigheten municipality election exports for 2014, 2018, and 2022 + Statistics Sweden municipal indicators`
- Statistics source: `Statistics Sweden`

## Known limitations

- This surface intentionally keeps a narrower public scope than the internal engine.
- If a factor or year combination does not hold up, it should disappear rather than survive as a lie.
- Some future country-specific factors may exist internally before they earn public release here.
