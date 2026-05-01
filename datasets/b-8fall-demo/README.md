# B_8Fall_Demo Metadata

This directory is reserved for metadata products extracted from
`B_8Fall_Demo`.

## Scope

Store here:

- Annotation exports.
- Video or sample manifests.
- Dataset split files.
- Schema documents explaining metadata fields.
- Notes about the annotation protocol.

Do not store here:

- Raw videos.
- Extracted frames.
- Model checkpoints.
- Large generated experiment artifacts.

## Metadata Layout

```text
datasets/b-8fall-demo/
└── metadata/
    ├── annotations/     # Label exports from the web annotator
    ├── manifests/       # Video/sample inventory files
    ├── schemas/         # JSON Schema, YAML schema, or column dictionaries
    └── splits/          # Train/validation/test split definitions
```

## Provenance Template

When adding a metadata export, include a nearby `README.md` or manifest entry
with:

- Source project path or repository.
- Source commit or snapshot date.
- Export command or manual export procedure.
- Annotation tool version, if available.
- File format and field definitions.
