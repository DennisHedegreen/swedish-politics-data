# Public Repo Improvement Plan

## Audit Summary

Already strong:

- Clear single-country wrapper around the shared engine.
- Sweden-only registry and public data pack.
- Public provenance notes and a visible Streamlit app.
- Tests that protect the basic public surface.

Creates trust:

- Declared Sweden-only, Riksdag-only, municipality-level scope.
- Narrow factor layer instead of pretending all interesting factors are ready.
- Withheld or constrained layers are named directly.
- Public source names are visible.

Still too builder-internal:

- The public README assumed too much context about the internal engine.
- The methodology note was too short for skeptical external readers.
- Test coverage was mostly smoke-level.

Missing for journalists and analysts:

- A plain guide for turning a result into a cautious reporting lead.
- More explicit warnings about ecological fallacy and causal overread.
- Deterministic tests for correlation and ranking behavior.
- Minimal contribution and license-status hygiene.

## Priorities

1. Make the public purpose and scope readable in under a minute.
2. Strengthen methodology without pretending the tool is more sophisticated than it is.
3. Add journalist-facing guardrails for responsible phrasing.
4. Add logic and public-scope tests.
5. Prepare a conservative first release tag.

## Risks

- Riksdag results can be misread as covering Swedish regional or municipal elections.
- Municipality-level results can be misread as individual voter behavior.
- Correlation can be misread as causal explanation.
- License terms should stay aligned with the selected MIT License.

## Proposed File Changes

- `README.md`: faster public overview, scope, interpretation, sources, source-of-truth note.
- `METHODOLOGY.md`: stronger public methods note.
- `HOW_TO_READ_RESULTS.md`: journalist-facing interpretation guide.
- `CONTRIBUTING.md`: minimal contribution and scope rules.
- `core/correlation.py`: small ranking helper for testable public ordering behavior.
- `tests/`: deterministic correlation, ranking, scope, and public contract tests.
- `CHANGELOG.md`: record release-prep trust pass.

## Acceptance Criteria

- README states what the tool does, what not to infer, and how to read results.
- Methodology covers Pearson correlation, missingness, limits, and ecological fallacy.
- Journalist guide includes responsible and irresponsible phrasing.
- Tests pass with `python -m unittest discover -s tests -v`.
- LICENSE exists and uses MIT.
- First release can be tagged as `v0.1.0` after final review.
