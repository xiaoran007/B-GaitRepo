# Datasets

This directory stores dataset-facing documentation and metadata products. It is
not intended to store raw videos, extracted frames, or model outputs.

## Organization

Each dataset gets one directory:

```text
datasets/
└── <dataset-name>/
    ├── README.md
    ├── metadata/
    │   ├── annotations/
    │   ├── manifests/
    │   ├── schemas/
    │   └── splits/
    └── docs/
```

## Metadata Principles

- Prefer stable, machine-readable files such as CSV, JSON, JSONL, or YAML.
- Include schema documentation when columns or nested fields are non-obvious.
- Record provenance: source repository, export command, export date, and source
  commit if available.
- Keep paths portable when possible. If local absolute paths are unavoidable,
  document the expected lab storage layout.
