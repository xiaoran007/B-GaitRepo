# B-8Fall-Demo Annotation Tools

This directory contains helper tools for the `B-8Fall-Demo` fall-simulation
videos.

This copy lives under `tools/video-web-annotator/` in `B-GaitRepo`. Run module
commands from that directory so `python -m B_8Fall_Demo...` resolves the copied
package.

## Manual Annotator

The recommended workflow is the local manual annotator. It opens one stitched `2 x 4` video in a browser and writes a human annotation file.

Runtime dependencies are listed in `../requirements.txt`.

Run after activating the Python environment:

```bash
cd tools/video-web-annotator
python -m B_8Fall_Demo.annotator \
  --video <stitched-video.mp4> \
  --output-dir ../../datasets/b-8fall-demo/metadata/annotations
```

For a directory of videos, launch once and switch videos inside the UI:

```bash
cd tools/video-web-annotator
python -m B_8Fall_Demo.annotator \
  --video-dir <stitched-video-directory> \
  --output-dir ../../datasets/b-8fall-demo/metadata/annotations
```

Open the printed local URL in a browser. The annotator loads data in this order:

1. Existing `video_c1.annotation.json`
2. Existing `video_c1.auto.json`
3. A default full-video `normal` segment

Saving writes only:

```text
datasets/b-8fall-demo/metadata/annotations/video_c1.annotation.json
```

The tool never writes `.auto.json` from the manual annotator.

### Shortcuts

- `Space`: play or pause
- `A` / `D`: step backward or forward 1 second
- `Q` / `E`: step backward or forward 5 seconds
- `,` / `.`: step backward or forward 1 frame
- `1`..`6`: select `ignore`, `normal`, `transition_nonfall`, `falling`, `post_fall`, `recovery`
- `I` / `O`: set selection in/out point
- `Enter`: apply selected state to the selection
- `M`: apply selected state to the selected segment
- `B`: split the current segment at the current frame
- `Backspace`: reset the selected segment to `normal`
- `S`: save

### Annotation Preview

After saving an annotation, click `Render Preview` in the local web UI to write:

```text
datasets/b-8fall-demo/metadata/annotations/video_c1.annotation.preview.mp4
```

You can also render it from the command line:

```bash
cd tools/video-web-annotator
python -m B_8Fall_Demo.render_annotation_preview \
  --video <stitched-video.mp4> \
  --output-dir ../../datasets/b-8fall-demo/metadata/annotations
```

The preview overlays the current state, frame/time, segment range, camera ids,
and a compact timeline bar onto the video.
