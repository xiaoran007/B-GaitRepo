# Video Web Annotator

Migrated from: `/Users/xiaoran/Desktop/code/B-Gait/B_8Fall_Demo`.

This folder contains the reusable local web annotator used by `B_8Fall_Demo`.
The original Python package name, `B_8Fall_Demo`, is preserved so the copied
tool can keep its relative imports and legacy absolute package imports.

## Layout

```text
tools/video-web-annotator/
├── README.md
└── B_8Fall_Demo/
    ├── annotator.py
    ├── render_annotation_preview.py
    └── static/
```

## Run

Runtime dependencies are listed in `requirements.txt`.

Run commands from this directory so `python -m B_8Fall_Demo...` resolves the
copied package:

```bash
cd tools/video-web-annotator
python -m B_8Fall_Demo.annotator \
  --video <stitched-video.mp4> \
  --output-dir ../../datasets/b-8fall-demo/metadata/annotations
```

For a directory of stitched videos:

```bash
cd tools/video-web-annotator
python -m B_8Fall_Demo.annotator \
  --video-dir <stitched-video-directory> \
  --output-dir ../../datasets/b-8fall-demo/metadata/annotations
```

The copied tool still expects stitched `2 x 4` videos by default. Use
`--rows` and `--cols` if the mosaic layout changes.

## Metadata Location

Committed annotation metadata lives in:

```text
datasets/b-8fall-demo/metadata/annotations/
```

Large raw videos, extracted frames, rendered preview videos, and other generated
media should stay outside this repository.
