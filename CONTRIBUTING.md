# Contributing

This repo is a public research surface, so changes should protect scope and trust before adding features.

## Rules

- Keep the repo Sweden-only, Riksdag-only, and municipality-level.
- Do not add regional or municipal election layers to this surface.
- Do not add causal or prediction language.
- Do not add a factor unless coverage, meaning, and source path are clear.
- Keep public docs aligned with the app and data pack.
- Add or update tests for public-surface contracts when behavior changes.

## Before Opening A Change

Run:

```bash
python -m unittest discover -s tests -v
```

If the change touches data, also update the relevant provenance or scope note.

## License

This repo uses the MIT License. Keep source attribution and provenance notes intact when changing data or public-method documentation.
