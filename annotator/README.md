# BAPD8-Demo Video Annotator

Local browser-based annotation tool for stitched `2 x 4` BAPD8-Demo videos (may also work with other videos).

## Files

```text
annotator/
├── README.md
├── requirements.txt
└── BAPD8_Demo/
    ├── annotator.py
    ├── render_annotation_preview.py
    └── static/
```

The package name `BAPD8_Demo` uses underscores so module commands work without
extra packaging.

## Run

Install the dependencies from `requirements.txt` in your chosen environment,
then run from this folder:

```bash
cd annotator
python -m BAPD8_Demo.annotator \
  --video <stitched-video.mp4> \
  --output-dir <annotations-dir>
```

For a directory of stitched videos:

```bash
cd annotator
python -m BAPD8_Demo.annotator \
  --video-dir <video-directory> \
  --output-dir <annotations-dir>
```

The tool opens a local URL in the browser. It loads an existing
`*.annotation.json` if present, otherwise falls back to a full-video `normal`
segment. Saving writes one JSON file per video.

## Preview

After saving, click `Render Preview` in the UI, or run:

```bash
cd annotator
python -m BAPD8_Demo.render_annotation_preview \
  --video <stitched-video.mp4> \
  --output-dir <annotations-dir>
```

Preview videos are generated files and should not be committed.
