# Sweden Factor Transfer Risks

See also:

- `sweden-factor-board.md` for the current add/investigate/block ordering
- `../provenance/sweden_internal_harvest_manifest.json` for the current internal harvest statuses

Current risk notes:

- `population`
  Safe as a country-local baseline. Cross-country comparison still needs denominator discipline.
- `age65`
  Concept transfers well, but age buckets and source timing must still be documented.
- `education`
  Public label can transfer, but the exact education-system mapping is still country-local and needs explicit source notes.
- `income`
  Sweden v1 uses average disposable income in `price-base-amounts`, not a generic currency-facing public label. It should stay country-local.
- `turnout`
  Transfers conceptually, but election administration and turnout definitions still need explicit country notes.
- `cars`
  Safe as a country-local structural factor when read as passenger cars per 1,000 residents. It should not be oversold as a climate or class proxy by itself.

Default status:

- `country_local` or `family_mapped`
- not `cross_country_ready`
