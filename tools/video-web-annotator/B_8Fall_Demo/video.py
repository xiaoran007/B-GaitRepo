from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

from .config import LayoutConfig


@dataclass(frozen=True)
class VideoInfo:
    path: Path
    stem: str
    width: int
    height: int
    fps: float
    frame_count: int
    duration_sec: float


@dataclass(frozen=True)
class Tile:
    view_id: int
    row: int
    col: int
    x0: int
    y0: int
    width: int
    height: int
    image: np.ndarray


def open_video(path: Path) -> cv2.VideoCapture:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {path}")
    return cap


def read_video_info(path: Path) -> VideoInfo:
    if not path.exists():
        raise FileNotFoundError(f"input video does not exist: {path}")
    cap = open_video(path)
    try:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    finally:
        cap.release()
    if width <= 0 or height <= 0:
        raise RuntimeError(f"invalid video dimensions for {path}: {width}x{height}")
    if fps <= 0:
        fps = 30.0
    duration_sec = frame_count / fps if frame_count > 0 else 0.0
    return VideoInfo(
        path=path,
        stem=path.stem,
        width=width,
        height=height,
        fps=fps,
        frame_count=frame_count,
        duration_sec=duration_sec,
    )


def validate_layout(info: VideoInfo, layout: LayoutConfig) -> tuple[int, int]:
    if info.width % layout.cols != 0:
        raise ValueError(f"video width {info.width} is not divisible by cols={layout.cols}")
    if info.height % layout.rows != 0:
        raise ValueError(f"video height {info.height} is not divisible by rows={layout.rows}")
    return info.width // layout.cols, info.height // layout.rows


def split_tiles(frame: np.ndarray, layout: LayoutConfig) -> list[Tile]:
    height, width = frame.shape[:2]
    tile_width = width // layout.cols
    tile_height = height // layout.rows
    tiles: list[Tile] = []
    for row in range(layout.rows):
        for col in range(layout.cols):
            view_id = row * layout.cols + col + 1
            x0 = col * tile_width
            y0 = row * tile_height
            tiles.append(
                Tile(
                    view_id=view_id,
                    row=row,
                    col=col,
                    x0=x0,
                    y0=y0,
                    width=tile_width,
                    height=tile_height,
                    image=frame[y0 : y0 + tile_height, x0 : x0 + tile_width],
                )
            )
    return tiles


def iter_sampled_frames(path: Path, stride: int) -> Iterator[tuple[int, np.ndarray]]:
    cap = open_video(path)
    frame_index = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_index % stride == 0:
                yield frame_index, frame
            frame_index += 1
    finally:
        cap.release()


def read_frame_at(path: Path, frame_index: int) -> np.ndarray:
    cap = open_video(path)
    try:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            raise RuntimeError(f"failed to read frame {frame_index} from {path}")
        return frame
    finally:
        cap.release()
