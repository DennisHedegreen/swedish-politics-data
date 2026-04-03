# Sweden Factor Board

Internal prioritization note for the next Sweden factor passes.

This is not a public comparability claim.
It is a working board for deciding what should enter the Sweden public layer next.

## Add Now

### `population_density`

Why:

- already harvested
- covers `2014`, `2018`, `2022`
- full municipality coverage: `290` in each public year
- strongest next public-safe candidate

Current disposition:

- promoted to the Sweden public layer on `2026-04-03`
- now part of the public Sweden factor set

### `cars`

Why:

- official municipality-safe bulk source from Statistics Sweden
- aligned public years: `2014`, `2018`, `2022`
- easy public reading as `passenger cars per 1,000 residents`
- useful structural complement to `population_density`

Current disposition:

- promoted to the Sweden public layer on `2026-04-03`
- now part of the public Sweden factor set

## Investigate Next

### `rental-vs-tenant-owned housing`

Why:

- highly Sweden-relevant housing structure
- likely stronger and more distinctive than adding another generic labour-market factor first
- can make the Sweden surface feel more structurally Swedish instead of just more generic

Current disposition:

- official SCB municipality path identified:
  - `AA0003D/IntGr6Kom`
- promising as two separate person-based housing factors:
  - `rented accommodation`
  - `tenant-owned homes`
- still blocked in this session by SCB `429` throttling during harvest

### `one-/two-dwelling building share`

Why:

- strong settlement and housing structure signal
- likely readable in the public app
- plausible complement to `population_density`

Current disposition:

- investigate next

### `productive_forest_land_share`

Why:

- genuinely Sweden-specific structural factor
- more honest than `forest per citizen`, which risks becoming just a density proxy
- could help Sweden develop its own factor identity

Current disposition:

- investigate through Skogsstyrelsen municipality statistics

## Internal-First / Needs More Care

### `employment`

Current reality:

- harvested
- clean municipality coverage
- current year coverage is `2022`, `2023`, `2024`
- does not line up with the first Sweden election-year layer

Current disposition:

- internal candidate
- blocked on year alignment

### `unemployment`

Current reality:

- harvested
- clean municipality coverage
- current year coverage is `2022`, `2023`, `2024`
- does not line up with the first Sweden election-year layer

Current disposition:

- internal candidate
- blocked on year alignment

### `welfare`

Current reality:

- harvested as income-support share
- election-year coverage exists for `2014`, `2018`, `2022`
- municipality coverage is uneven:
  - `2014`: `253`
  - `2018`: `281`
  - `2022`: `282`
- semantically country-local and not equivalent to a broader public welfare label without extra defense

Current disposition:

- keep internal-first until both coverage and wording are defended

## Later / Thematic

### `house_price_level`

Why:

- potentially strong
- more market-facing than the first Sweden public factor layer needs right now

### `protected_forest_area`

Why:

- politically and ecologically interesting
- likely better as a later thematic layer than as a core public factor

### `forest_per_citizen`

Why not now:

- likely to behave mostly as a repackaged rurality / density signal
- weaker first choice than `productive_forest_land_share`

## Blocked For Now

### `immigration_share`

Why:

- semantically risky
- high chance of fake comparability or muddy public wording

### `crime`

Why:

- no clean municipality-safe source path is locked yet

### `commute_distance`

Why:

- source and year continuity are not locked yet

## Working order

1. retry `rental-vs-tenant-owned housing` harvest when SCB rate limit clears
2. investigate `one-/two-dwelling building share`
3. investigate `productive_forest_land_share`
4. revisit `employment`, `unemployment`, `welfare` only after the above are clearer
