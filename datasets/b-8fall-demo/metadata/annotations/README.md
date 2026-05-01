# Annotation Exports

This folder contains exported manual annotation files for `B_8Fall_Demo`.

Current files were copied from:

```text
/Users/xiaoran/Desktop/temp/outputs/B_8Fall_Demo
```

The corresponding reusable annotator is in:

```text
tools/video-web-annotator/
```

The copied JSON files use video filenames in `video.path` instead of the
original local absolute paths, so consumers should resolve them against their
own B_8Fall_Demo video storage location.

Recommended file naming:

```text
<dataset>_<task>_<export-date>.<csv|json|jsonl>
```

For future exports, record the source annotator version and field definitions
in `metadata/schemas/` or in a small adjacent README.
