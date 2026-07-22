# BAPD8-Demo Metadata

This folder stores the exported manual annotations for BAPD8-Demo.

Current contents:

- `annotations/*.annotation.json`: manual labels.

Each annotation has a top-level integer `subject` field. Values 1-3 identify
the three actors consistently across videos.

The annotator does not write this fixed field. After annotation, apply the
video-to-subject mapping with:

```bash
python datasets/BAPD8-Demo/patch_subject_metadata.py \
  --annotation-dir <annotations-dir>
```

If `--annotation-dir` is omitted, the script updates the sibling
`annotations/` directory.

The JSON files use video filenames such as `video_c1.mp4` in `video.path`.
Resolve those names against your own local video storage path.

The annotator that reads and writes these files is in [`../../annotator/`](../../annotator/).

Do not put raw videos, rendered previews, checkpoints, or experiment outputs in
this repository.
