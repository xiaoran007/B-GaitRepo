from __future__ import annotations

from pathlib import Path

import cv2
from tqdm.auto import tqdm

from .config import DEFAULT_PREVIEW_CODEC, LayoutConfig
from .video import VideoInfo, open_video, split_tiles


TEXT_FONT = cv2.FONT_HERSHEY_SIMPLEX
STATE_COLORS = {
    "ignore": (120, 120, 120),
    "normal": (80, 190, 80),
    "transition_nonfall": (0, 190, 255),
    "falling": (0, 0, 255),
    "post_fall": (255, 110, 40),
    "recovery": (190, 80, 255),
}


def render_annotation_preview(
    *,
    video_info: VideoInfo,
    layout: LayoutConfig,
    output_path: Path,
    timeline: list[dict],
) -> None:
    cap = open_video(video_info.path)
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*DEFAULT_PREVIEW_CODEC),
        video_info.fps,
        (video_info.width, video_info.height),
    )
    if not writer.isOpened():
        cap.release()
        raise RuntimeError(f"failed to create annotation preview writer: {output_path}")

    segment_index = 0
    current_segment = timeline[0] if timeline else None
    progress = tqdm(total=video_info.frame_count or None, desc="annotation preview", unit="frame")
    frame_index = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            while (
                segment_index + 1 < len(timeline)
                and int(timeline[segment_index + 1]["start_frame"]) <= frame_index
            ):
                segment_index += 1
                current_segment = timeline[segment_index]

            tiles = split_tiles(frame, layout)
            _draw_tile_ids(frame, tiles)
            if current_segment is not None:
                _draw_annotation_header(frame, current_segment, frame_index, video_info.fps)
                _draw_annotation_timeline(frame, timeline, frame_index, video_info.frame_count)
            writer.write(frame)
            frame_index += 1
            progress.update(1)
    finally:
        progress.close()
        cap.release()
        writer.release()


def _draw_annotation_header(frame, segment: dict, frame_index: int, fps: float) -> None:
    state = str(segment.get("state", "normal"))
    color = STATE_COLORS.get(state, (255, 255, 255))
    start = int(segment.get("start_frame", frame_index))
    end = int(segment.get("end_frame", frame_index))
    text = (
        f"frame {frame_index}  time {frame_index / fps:.2f}s  "
        f"state {state}  segment {start}-{end}"
    )
    cv2.rectangle(frame, (0, 0), (frame.shape[1], 38), (0, 0, 0), thickness=-1)
    cv2.putText(frame, text, (12, 26), TEXT_FONT, 0.7, color, 2, cv2.LINE_AA)


def _draw_annotation_timeline(frame, timeline: list[dict], frame_index: int, frame_count: int) -> None:
    if frame_count <= 0:
        return
    height, width = frame.shape[:2]
    bar_height = 18
    y0 = height - bar_height - 10
    x0 = 12
    bar_width = width - 24
    cv2.rectangle(frame, (x0, y0), (x0 + bar_width, y0 + bar_height), (0, 0, 0), thickness=-1)
    for segment in timeline:
        state = str(segment.get("state", "normal"))
        color = STATE_COLORS.get(state, (255, 255, 255))
        start = int(segment.get("start_frame", 0))
        end = int(segment.get("end_frame", start))
        left = x0 + int(bar_width * start / frame_count)
        right = x0 + int(bar_width * min(end + 1, frame_count) / frame_count)
        cv2.rectangle(frame, (left, y0), (max(left + 1, right), y0 + bar_height), color, thickness=-1)
    play_x = x0 + int(bar_width * min(max(frame_index, 0), frame_count - 1) / frame_count)
    cv2.line(frame, (play_x, y0 - 4), (play_x, y0 + bar_height + 4), (255, 255, 255), 2, cv2.LINE_AA)


def _draw_tile_ids(frame, tiles) -> None:
    for tile in tiles:
        cv2.rectangle(frame, (tile.x0, tile.y0), (tile.x0 + tile.width, tile.y0 + tile.height), (80, 80, 80), 1)
        cv2.putText(
            frame,
            f"cam {tile.view_id}",
            (tile.x0 + 8, tile.y0 + 58),
            TEXT_FONT,
            0.55,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )
