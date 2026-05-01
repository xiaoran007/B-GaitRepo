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

## B-8Fall-Demo

- Web annotator: [`annotator/`](annotator/)
- Annotation metadata: [`metadata/B_8Fall_Demo/`](metadata/B_8Fall_Demo/)

The dataset contains 25 videos:
```text
.
├── video_c1.mp4
├── video_c2.mp4
├── video_c3.mp4
├── video_c4.mp4
├── video_c5.mp4
├── video_c6.mp4
├── video_c7.mp4
├── video_c8.mp4
├── video_c9.mp4
├── video_c10.mp4
├── video_c11.mp4
├── video_c12.mp4
├── video_c13.mp4
├── video_c14.mp4
├── video_c15.mp4
├── video_c16.mp4
├── video_c17.mp4
├── video_c18.mp4
├── video_c19.mp4
├── video_c20.mp4
├── video_c21.mp4
├── video_c22.mp4
├── video_c23.mp4
├── video_c24.mp4
└── video_c25.mp4
```

Annotation metadata contains `json` files like this:
```json
{
  "dataset": "B-8Fall-Demo",
  "annotation_type": "manual",
  "video": {
    "path": "video_c1.mp4",
    "stem": "video_c1",
    "width": 2560,
    "height": 800,
    "fps": 30.0,
    "frame_count": 519,
    "duration_sec": 17.3
  },
  "layout": {
    "rows": 2,
    "cols": 4,
    "tile_width": 640,
    "tile_height": 400,
    "view_ids": [
      1,
      2,
      3,
      4,
      5,
      6,
      7,
      8
    ]
  },
  "timeline": [
    {
      "start_frame": 0,
      "end_frame": 79,
      "start_time_sec": 0.0,
      "end_time_sec": 2.667,
      "state": "ignore"
    },
    {
      "start_frame": 80,
      "end_frame": 440,
      "start_time_sec": 2.667,
      "end_time_sec": 14.7,
      "state": "normal"
    },
    {
      "start_frame": 441,
      "end_frame": 518,
      "start_time_sec": 14.7,
      "end_time_sec": 17.3,
      "state": "ignore"
    }
  ],
  "key_events": {},
  "metadata": {
    "tool": "B_8Fall_Demo.annotator",
    "created_at": "2026-05-01T18:00:02+00:00",
    "updated_at": "2026-05-01T18:00:02+00:00"
  }
}

```

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

