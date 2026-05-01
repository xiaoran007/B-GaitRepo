# B-GaitRepo

B-GaitRepo collects small reusable gait/fall-detection tools, dataset metadata,
and links that are useful inside the lab.

This is intentionally lightweight: no raw videos, no checkpoints, no large
experiment outputs, and no copied external repositories unless there is a clear
reason.

## Contents

```text
B-GaitRepo/
├── annotator/                 # B_8Fall_Demo local video annotation tool
├── metadata/
│   └── B_8Fall_Demo/          # exported annotation JSON files
├── links.md                   # related repos and PRs
└── README.md
```

## B_8Fall_Demo

- Web annotator: [`annotator/`](annotator/)
- Annotation metadata: [`metadata/B_8Fall_Demo/`](metadata/B_8Fall_Demo/)

Run the annotator from `annotator/`:

```bash
cd annotator
python -m B_8Fall_Demo.annotator \
  --video <stitched-video.mp4> \
  --output-dir ../metadata/B_8Fall_Demo/annotations
```

## Related Work

See [`links.md`](links.md).
