# B-GaitRepo

B-GaitRepo collects small reusable gait/fall-detection tools, dataset metadata,
and links that may useful.

## Contents

```text
B-GaitRepo/
├── annotator/                 # B_8Fall_Demo local video annotation tool
├── datasets/
│   └── B_8Fall_Demo/          # exported annotation JSON files
└── README.md
```

## B_8Fall_Demo

- Web annotator: [`annotator/`](annotator/)
- Annotation metadata: [`metadata/B_8Fall_Demo/`](metadata/B_8Fall_Demo/)

Run the annotator from `annotator/`:

```bash
cd annotator
python -m B_8Fall_Demo.annotator \
  --video-dir <video-directory> \
  --output-dir <annotations-dir>
```

## Other Repo
- [B-MCFD](https://github.com/xiaoran007/B-MCFD): utils and metadata for multi-camera fall detection datasets.
- [Kinetics-i3d-for-modern-pytorch](https://github.com/xiaoran007/Kinetics-i3d-for-modern-pytorch): modern PyTorch I3D reference implementation.
- [multi_cam_jetson PR #2](https://github.com/C-H-Chien/multi_cam_jetson/pull/2): 8-camera recording utils for Jetson Orin Nano Super.

## Contributors
T. Fang

