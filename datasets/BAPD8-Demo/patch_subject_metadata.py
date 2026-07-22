from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


SUBJECT_BY_VIDEO = {
    "video_c1": 1,
    "video_c2": 2,
    "video_c3": 3,
    "video_c4": 2,
    "video_c5": 2,
    "video_c6": 3,
    "video_c7": 2,
    "video_c8": 1,
    "video_c9": 1,
    "video_c10": 1,
    "video_c11": 3,
    "video_c12": 2,
    "video_c13": 1,
    "video_c14": 3,
    "video_c15": 2,
    "video_c16": 1,
    "video_c17": 3,
    "video_c18": 2,
    "video_c19": 1,
    "video_c20": 1,
    "video_c21": 3,
    "video_c22": 1,
    "video_c23": 3,
    "video_c24": 1,
    "video_c25": 2,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Patch fixed BAPD8-Demo subject metadata.")
    parser.add_argument(
        "--annotation-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "annotations",
        help="Directory containing video_c*.annotation.json files.",
    )
    return parser.parse_args()


def add_subject(payload: dict[str, Any], subject: int) -> dict[str, Any]:
    if payload.get("dataset") != "BAPD8-Demo":
        raise ValueError("annotation dataset should be BAPD8-Demo")
    if "annotation_type" not in payload:
        raise ValueError("annotation_type is required")

    updated: dict[str, Any] = {}
    for key, value in payload.items():
        if key == "subject":
            continue
        updated[key] = value
        if key == "annotation_type":
            updated["subject"] = subject
    return updated


def main() -> None:
    annotation_dir = parse_args().annotation_dir.expanduser().resolve()
    for video_stem, subject in SUBJECT_BY_VIDEO.items():
        annotation_path = annotation_dir / f"{video_stem}.annotation.json"
        with open(annotation_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        if not isinstance(payload, dict):
            raise ValueError(f"annotation payload should be a JSON object: {annotation_path}")

        updated = add_subject(payload, subject)
        with open(annotation_path, "w", encoding="utf-8") as f:
            json.dump(updated, f, indent=2)
            f.write("\n")

    print(f"Patched subject metadata in {len(SUBJECT_BY_VIDEO)} annotations: {annotation_dir}")


if __name__ == "__main__":
    main()
