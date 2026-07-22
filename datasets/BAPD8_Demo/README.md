# BAPD8-Demo Metadata

This folder stores the exported manual annotations for BAPD8-Demo.

Current contents:

- `annotations/*.annotation.json`: manual labels.

The JSON files use video filenames such as `video_c1.mp4` in `video.path`.
Resolve those names against your own local video storage path.

The annotator that reads and writes these files is in [`../../annotator/`](../../annotator/).

Do not put raw videos, rendered previews, checkpoints, or experiment outputs in
this repository.
