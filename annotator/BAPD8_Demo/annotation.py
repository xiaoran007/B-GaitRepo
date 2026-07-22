from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from . import DATASET_NAME
from .config import LayoutConfig
from .video import VideoInfo, validate_layout


STATES = ("ignore", "normal", "transition_nonfall", "falling", "post_fall", "recovery")
TOOL_NAME = "BAPD8_Demo.annotator"


def load_initial_annotation(
    *,
    annotation_path: Path,
    auto_path: Path,
    video_info: VideoInfo,
    layout: LayoutConfig,
) -> dict[str, Any]:
    if annotation_path.exists():
        payload = _read_json(annotation_path)
        source = "annotation"
    elif auto_path.exists():
        payload = _read_json(auto_path)
        source = "auto"
    else:
        payload = {"timeline": [_default_segment(video_info)]}
        source = "default"

    normalized = normalize_annotation_payload(
        payload=payload,
        video_info=video_info,
        layout=layout,
        created_at=payload.get("metadata", {}).get("created_at") if isinstance(payload.get("metadata"), dict) else None,
    )
    normalized["source"] = source
    return normalized


def normalize_annotation_payload(
    *,
    payload: dict[str, Any],
    video_info: VideoInfo,
    layout: LayoutConfig,
    created_at: str | None = None,
) -> dict[str, Any]:
    tile_width, tile_height = validate_layout(video_info, layout)
    timeline = normalize_timeline(
        timeline=payload.get("timeline", []),
        frame_count=video_info.frame_count,
        fps=video_info.fps,
    )
    now = _now_iso()
    return {
        "dataset": DATASET_NAME,
        "annotation_type": "manual",
        "video": {
            "path": str(video_info.path),
            "stem": video_info.stem,
            "width": video_info.width,
            "height": video_info.height,
            "fps": video_info.fps,
            "frame_count": video_info.frame_count,
            "duration_sec": round(video_info.duration_sec, 3),
        },
        "layout": {
            "rows": layout.rows,
            "cols": layout.cols,
            "tile_width": tile_width,
            "tile_height": tile_height,
            "view_ids": list(range(1, layout.view_count + 1)),
        },
        "timeline": timeline,
        "key_events": derive_key_events(timeline),
        "metadata": {
            "tool": TOOL_NAME,
            "created_at": created_at or now,
            "updated_at": now,
        },
    }


def normalize_timeline(*, timeline: list[Any], frame_count: int, fps: float) -> list[dict[str, Any]]:
    last_frame = max(frame_count - 1, 0)
    clean: list[dict[str, Any]] = []
    for item in timeline:
        if not isinstance(item, dict):
            continue
        state = str(item.get("state", "normal"))
        if state not in STATES:
            state = "normal"
        start = _coerce_frame(item.get("start_frame", 0), 0, last_frame)
        end = _coerce_frame(item.get("end_frame", start), 0, last_frame)
        if end < start:
            start, end = end, start
        clean.append({"start_frame": start, "end_frame": end, "state": state})

    if not clean:
        clean = [{"start_frame": 0, "end_frame": last_frame, "state": "normal"}]

    clean.sort(key=lambda item: (item["start_frame"], item["end_frame"]))
    filled: list[dict[str, Any]] = []
    cursor = 0
    for item in clean:
        start = max(item["start_frame"], cursor)
        end = max(item["end_frame"], start)
        if start > cursor:
            filled.append({"start_frame": cursor, "end_frame": start - 1, "state": "normal"})
        if start <= last_frame:
            filled.append({"start_frame": start, "end_frame": min(end, last_frame), "state": item["state"]})
            cursor = min(end + 1, last_frame + 1)
        if cursor > last_frame:
            break
    if cursor <= last_frame:
        filled.append({"start_frame": cursor, "end_frame": last_frame, "state": "normal"})

    merged = _merge_adjacent(filled)
    return [_with_time_fields(item, fps) for item in merged]


def derive_key_events(timeline: list[dict[str, Any]]) -> dict[str, Any]:
    events: dict[str, Any] = {}
    for event_name, state in (
        ("falling_start", "falling"),
        ("post_fall_start", "post_fall"),
        ("recovery_start", "recovery"),
    ):
        segment = next((item for item in timeline if item.get("state") == state), None)
        if segment is not None:
            events[event_name] = {
                "frame": segment["start_frame"],
                "time_sec": segment["start_time_sec"],
            }
    return events


def write_annotation(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")


def _read_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError(f"annotation payload should be a JSON object: {path}")
    return payload


def _default_segment(video_info: VideoInfo) -> dict[str, Any]:
    return {
        "start_frame": 0,
        "end_frame": max(video_info.frame_count - 1, 0),
        "state": "normal",
    }


def _merge_adjacent(timeline: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    for item in timeline:
        if merged and merged[-1]["state"] == item["state"] and merged[-1]["end_frame"] + 1 >= item["start_frame"]:
            merged[-1]["end_frame"] = max(merged[-1]["end_frame"], item["end_frame"])
        else:
            merged.append(dict(item))
    return merged


def _with_time_fields(item: dict[str, Any], fps: float) -> dict[str, Any]:
    start = int(item["start_frame"])
    end = int(item["end_frame"])
    return {
        "start_frame": start,
        "end_frame": end,
        "start_time_sec": round(start / fps, 3) if fps > 0 else 0.0,
        "end_time_sec": round((end + 1) / fps, 3) if fps > 0 else 0.0,
        "state": item["state"],
    }


def _coerce_frame(value: Any, lower: int, upper: int) -> int:
    try:
        frame = int(round(float(value)))
    except (TypeError, ValueError):
        frame = lower
    return min(max(frame, lower), upper)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
