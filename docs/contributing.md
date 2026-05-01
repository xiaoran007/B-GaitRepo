# Contributing Notes

This repository is meant to stay small, navigable, and provenance-aware.

## Adding a Tool

1. Create `tools/<tool-name>/`.
2. Add a `README.md` describing the source, purpose, setup, input, and output.
3. Keep example data tiny.
4. Put dataset-specific outputs under `datasets/<dataset-name>/metadata/`
   instead of inside the tool folder.
5. Document dependencies before adding installation instructions.

## Adding Dataset Metadata

1. Create or reuse `datasets/<dataset-name>/metadata/`.
2. Put annotations, manifests, schemas, and splits in their matching folders.
3. Include provenance for every exported metadata product.
4. Avoid raw media and large derived artifacts.

## Adding External Links

1. Add the link to `external/README.md`.
2. State why the link matters.
3. Record license or access constraints when known.

## Naming

- Use lowercase directory names with hyphens, for example
  `video-web-annotator`.
- Use stable dataset identifiers, for example `b-8fall-demo`.
- Prefer descriptive metadata filenames with dates or version tags.
