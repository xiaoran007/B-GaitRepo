# Tools

This directory contains reusable utilities extracted from research projects.
Each tool should be self-contained enough for lab members to inspect, run, and
adapt without reading the original source repository first.

## Organization

Each tool gets its own subdirectory:

```text
tools/
└── <tool-name>/
    ├── README.md
    ├── src/ or app/
    ├── config/          # Example configs, if needed
    ├── examples/        # Small examples only
    └── docs/            # Tool-specific notes, if needed
```

## Tool Documentation Checklist

- Original source path or repository.
- Main use case.
- Required runtime and dependencies.
- Minimal launch or usage command.
- Input and output formats.
- Known limitations.
- Migration status.
