from __future__ import annotations

import argparse
import json
from pathlib import Path

from .annotation import normalize_annotation_payload
from .annotation_render import render_annotation_preview
from .config import DEFAULT_COLS, DEFAULT_ROWS, LayoutConfig, build_annotation_preview_path, build_output_paths
from .video import read_video_info


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a video preview with manual annotation labels overlaid.")
    parser.add_argument("--video", required=True, help="Path to one stitched/mosaic video.")
    parser.add_argument("--output-dir", required=True, help="Directory containing the .annotation.json file.")
    parser.add_argument("--annotation", default=None, help="Optional explicit annotation JSON path.")
    parser.add_argument("--output", default=None, help="Optional preview output path.")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="Mosaic row count.")
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS, help="Mosaic column count.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    video_path = Path(args.video).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    layout = LayoutConfig(rows=args.rows, cols=args.cols)
    video_info = read_video_info(video_path)
    _, default_annotation_path, _ = build_output_paths(video_path, output_dir)
    annotation_path = Path(args.annotation).expanduser().resolve() if args.annotation else default_annotation_path
    preview_path = Path(args.output).expanduser().resolve() if args.output else build_annotation_preview_path(video_path, output_dir)

    if not annotation_path.exists():
        raise FileNotFoundError(f"annotation file does not exist: {annotation_path}")
    with open(annotation_path, "r", encoding="utf-8") as f:
        annotation = json.load(f)
    if not isinstance(annotation, dict):
        raise ValueError(f"annotation payload should be a JSON object: {annotation_path}")

    normalized = normalize_annotation_payload(payload=annotation, video_info=video_info, layout=layout)
    preview_path.parent.mkdir(parents=True, exist_ok=True)
    render_annotation_preview(
        video_info=video_info,
        layout=layout,
        output_path=preview_path,
        timeline=normalized["timeline"],
    )
    print(f"Annotation preview: {preview_path}")


if __name__ == "__main__":
    main()
