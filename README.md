# B-GaitRepo

B-GaitRepo is a lab-facing collection of reusable gait, fall-detection, and
multi-camera research assets. It is intended to gather small tools, dataset
metadata products, and pointers to related research repositories without
duplicating large raw datasets.

## Repository Layout

```text
B-GaitRepo/
├── tools/
│   └── video-web-annotator/        # Web annotation tool migrated from B_8Fall_Demo
├── datasets/
│   └── b-8fall-demo/               # B_8Fall_Demo documentation and metadata products
│       └── metadata/
│           ├── annotations/         # Exported labels and annotation tables
│           ├── manifests/           # Video/sample manifests
│           ├── schemas/             # Metadata schema definitions
│           └── splits/              # Train/val/test or experiment split files
├── external/                        # Curated links to related repositories and PRs
├── docs/                            # Migration and contribution notes
└── templates/                       # Reusable metadata and documentation templates
```

## Current Migration Status

1. `B_8Fall_Demo` video web annotation tool: migrated to
   `tools/video-web-annotator/`.
2. `B_8Fall_Demo` dataset annotation metadata products: copied to
   `datasets/b-8fall-demo/metadata/annotations/`.
3. [B-MCFD](https://github.com/xiaoran007/B-MCFD).
4. [Kinetics-i3d-for-modern-pytorch](https://github.com/xiaoran007/Kinetics-i3d-for-modern-pytorch).
5. [multi_cam_jetson PR #2](https://github.com/C-H-Chien/multi_cam_jetson/pull/2).

## What Belongs Here

- Small reusable tools that lab members can run or adapt.
- Metadata files that describe datasets, annotations, schemas, and splits.
- Documentation that explains provenance, usage, and expected formats.
- Links to external repositories, PRs, or papers when copying code is not the
  right choice.

## What Should Stay Outside

- Raw videos, large frame dumps, checkpoints, and generated experiment outputs.
- Private or license-restricted data unless the repository access model permits
  redistribution.
- Forked copies of external repositories when a stable link or submodule would
  be clearer.

## Quick Start for Lab Members

- Start from [`external/README.md`](external/README.md) to find related code.
- Use [`datasets/b-8fall-demo/README.md`](datasets/b-8fall-demo/README.md) for
  B_8Fall_Demo metadata conventions.
- Use [`tools/video-web-annotator/README.md`](tools/video-web-annotator/README.md)
  once the annotator is migrated.
- Follow [`docs/contributing.md`](docs/contributing.md) when adding a new tool,
  dataset metadata folder, or external reference.
