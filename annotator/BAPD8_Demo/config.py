from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


DEFAULT_ROWS = 2
DEFAULT_COLS = 4
DEFAULT_PREVIEW_CODEC = "mp4v"


@dataclass(frozen=True)
class LayoutConfig:
    rows: int = DEFAULT_ROWS
    cols: int = DEFAULT_COLS

    @property
    def view_count(self) -> int:
        return self.rows * self.cols


def build_output_paths(input_path: Path, output_dir: Path) -> tuple[Path, Path, Path]:
    stem = input_path.stem
    return (
        output_dir / f"{stem}.auto.json",
        output_dir / f"{stem}.annotation.json",
        output_dir / f"{stem}.preview.mp4",
    )


def build_annotation_preview_path(input_path: Path, output_dir: Path) -> Path:
    return output_dir / f"{input_path.stem}.annotation.preview.mp4"
