from __future__ import annotations

import argparse
import json
import mimetypes
import re
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .annotation import load_initial_annotation, normalize_annotation_payload, write_annotation
from .annotation_render import render_annotation_preview
from .config import DEFAULT_COLS, DEFAULT_ROWS, LayoutConfig, build_annotation_preview_path, build_output_paths
from .video import read_video_info, validate_layout


PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"
VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".avi"}


class AnnotatorContext:
    def __init__(self, *, video_paths: list[Path], output_dir: Path, layout: LayoutConfig) -> None:
        if not video_paths:
            raise ValueError("at least one video is required")
        self.video_paths = {path.name: path for path in video_paths}
        if len(self.video_paths) != len(video_paths):
            raise ValueError("video file names should be unique")
        self.default_video_name = video_paths[0].name
        self.output_dir = output_dir
        self.layout = layout
        self._video_info_cache = {}

    def videos(self) -> dict:
        return {
            "videos": [
                {"name": name, "path": str(path), "stem": path.stem}
                for name, path in sorted(self.video_paths.items(), key=lambda item: _natural_sort_key(item[0]))
            ],
            "default_video": self.default_video_name,
        }

    def resolve_video_name(self, requested_name: str | None) -> str:
        name = requested_name or self.default_video_name
        if name not in self.video_paths:
            raise FileNotFoundError(f"video is not available in this annotator session: {name}")
        return name

    def video_path(self, video_name: str) -> Path:
        return self.video_paths[self.resolve_video_name(video_name)]

    def video_info(self, video_name: str):
        name = self.resolve_video_name(video_name)
        if name not in self._video_info_cache:
            info = read_video_info(self.video_paths[name])
            validate_layout(info, self.layout)
            self._video_info_cache[name] = info
        return self._video_info_cache[name]

    def output_paths(self, video_name: str) -> tuple[Path, Path, Path]:
        return build_output_paths(self.video_path(video_name), self.output_dir)

    def annotation_preview_path(self, video_name: str) -> Path:
        return build_annotation_preview_path(self.video_path(video_name), self.output_dir)

    def metadata(self, video_name: str) -> dict:
        info = self.video_info(video_name)
        auto_path, annotation_path, _ = self.output_paths(video_name)
        preview_path = self.annotation_preview_path(video_name)
        tile_width, tile_height = validate_layout(info, self.layout)
        return {
            "dataset": "B-8Fall-Demo",
            "video": {
                "name": self.resolve_video_name(video_name),
                "path": str(info.path),
                "stem": info.stem,
                "width": info.width,
                "height": info.height,
                "fps": info.fps,
                "frame_count": info.frame_count,
                "duration_sec": round(info.duration_sec, 3),
            },
            "layout": {
                "rows": self.layout.rows,
                "cols": self.layout.cols,
                "tile_width": tile_width,
                "tile_height": tile_height,
                "view_ids": list(range(1, self.layout.view_count + 1)),
            },
            "paths": {
                "auto": str(auto_path),
                "annotation": str(annotation_path),
                "annotation_preview": str(preview_path),
            },
        }

    def load_annotation(self, video_name: str) -> dict:
        info = self.video_info(video_name)
        auto_path, annotation_path, _ = self.output_paths(video_name)
        return load_initial_annotation(
            annotation_path=annotation_path,
            auto_path=auto_path,
            video_info=info,
            layout=self.layout,
        )

    def save_annotation(self, video_name: str, payload: dict) -> dict:
        info = self.video_info(video_name)
        _, annotation_path, _ = self.output_paths(video_name)
        created_at = None
        if annotation_path.exists():
            current = self.load_annotation(video_name)
            metadata = current.get("metadata", {})
            if isinstance(metadata, dict):
                created_at = metadata.get("created_at")
        normalized = normalize_annotation_payload(
            payload=payload,
            video_info=info,
            layout=self.layout,
            created_at=created_at,
        )
        write_annotation(annotation_path, normalized)
        normalized["source"] = "annotation"
        return normalized

    def render_annotation_preview(self, video_name: str) -> dict:
        info = self.video_info(video_name)
        _, annotation_path, _ = self.output_paths(video_name)
        preview_path = self.annotation_preview_path(video_name)
        if not annotation_path.exists():
            raise FileNotFoundError(f"annotation file does not exist: {annotation_path}")
        annotation = self.load_annotation(video_name)
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        render_annotation_preview(
            video_info=info,
            layout=self.layout,
            output_path=preview_path,
            timeline=annotation["timeline"],
        )
        return {"preview_path": str(preview_path)}


def make_handler(context: AnnotatorContext):
    class AnnotatorHandler(BaseHTTPRequestHandler):
        server_version = "B8FallAnnotator/0.1"

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            if path == "/":
                self._send_static(STATIC_DIR / "index.html")
            elif path.startswith("/static/"):
                self._send_static(STATIC_DIR / path.removeprefix("/static/"))
            elif path == "/video":
                self._send_video(self._query_video_name(parsed))
            elif path == "/api/videos":
                self._send_json(context.videos())
            elif path == "/api/metadata":
                self._send_json(context.metadata(self._query_video_name(parsed)))
            elif path == "/api/annotation":
                self._send_json(context.load_annotation(self._query_video_name(parsed)))
            else:
                self.send_error(HTTPStatus.NOT_FOUND, "not found")

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            path = parsed.path
            if path != "/api/annotation":
                if path == "/api/preview":
                    self._handle_preview(self._query_video_name(parsed))
                    return
                self.send_error(HTTPStatus.NOT_FOUND, "not found")
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                payload = json.loads(body.decode("utf-8")) if body else {}
                if not isinstance(payload, dict):
                    raise ValueError("request payload should be a JSON object")
                saved = context.save_annotation(self._query_video_name(parsed), payload)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json(saved)

        def _handle_preview(self, video_name: str | None) -> None:
            try:
                result = context.render_annotation_preview(video_name)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
                return
            self._send_json(result)

        def log_message(self, format: str, *args) -> None:
            print(f"{self.address_string()} - {format % args}")

        def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_static(self, path: Path) -> None:
            if not path.exists() or not path.is_file():
                self.send_error(HTTPStatus.NOT_FOUND, "not found")
                return
            data = path.read_bytes()
            content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _query_video_name(self, parsed) -> str | None:
            values = parse_qs(parsed.query).get("video")
            if not values:
                return None
            return values[0]

        def _send_video(self, video_name: str | None) -> None:
            try:
                video_path = context.video_path(video_name)
            except Exception as exc:
                self._send_json({"error": str(exc)}, status=HTTPStatus.NOT_FOUND)
                return
            file_size = video_path.stat().st_size
            range_header = self.headers.get("Range")
            content_type = mimetypes.guess_type(str(video_path))[0] or "video/mp4"
            if not range_header:
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", content_type)
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Content-Length", str(file_size))
                self.end_headers()
                with open(video_path, "rb") as f:
                    _write_video_chunk(self.wfile, f.read())
                return

            start, end = _parse_range(range_header, file_size)
            chunk_size = end - start + 1
            self.send_response(HTTPStatus.PARTIAL_CONTENT)
            self.send_header("Content-Type", content_type)
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(chunk_size))
            self.end_headers()
            with open(video_path, "rb") as f:
                f.seek(start)
                remaining = chunk_size
                while remaining > 0:
                    chunk = f.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    if not _write_video_chunk(self.wfile, chunk):
                        break
                    remaining -= len(chunk)

    return AnnotatorHandler


def _parse_range(range_header: str, file_size: int) -> tuple[int, int]:
    unit, _, value = range_header.partition("=")
    if unit.strip() != "bytes" or "-" not in value:
        return 0, file_size - 1
    start_text, end_text = value.split("-", 1)
    if start_text:
        start = int(start_text)
        end = int(end_text) if end_text else file_size - 1
    else:
        suffix = int(end_text)
        start = max(file_size - suffix, 0)
        end = file_size - 1
    start = min(max(start, 0), file_size - 1)
    end = min(max(end, start), file_size - 1)
    return start, end


def _write_video_chunk(wfile, chunk: bytes) -> bool:
    try:
        wfile.write(chunk)
    except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
        return False
    return True


def _natural_sort_key(value: str) -> list[int | str]:
    parts = re.split(r"(\d+)", value.lower())
    return [int(part) if part.isdigit() else part for part in parts]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch the B-8Fall-Demo local manual annotation UI.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--video", help="Path to one stitched/mosaic video.")
    group.add_argument("--video-dir", help="Directory containing stitched/mosaic videos.")
    parser.add_argument("--output-dir", required=True, help="Directory containing .auto.json and .annotation.json files.")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="Mosaic row count.")
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS, help="Mosaic column count.")
    parser.add_argument("--host", default="127.0.0.1", help="Host for the local annotation server.")
    parser.add_argument("--port", type=int, default=8765, help="Port for the local annotation server.")
    return parser.parse_args()


def resolve_video_paths(args: argparse.Namespace) -> list[Path]:
    if args.video:
        path = Path(args.video).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"video does not exist: {path}")
        return [path]
    video_dir = Path(args.video_dir).expanduser().resolve()
    if not video_dir.exists() or not video_dir.is_dir():
        raise FileNotFoundError(f"video directory does not exist: {video_dir}")
    paths = sorted(
        [path for path in video_dir.iterdir() if path.is_file() and path.suffix.lower() in VIDEO_SUFFIXES],
        key=lambda path: path.name.lower(),
    )
    if not paths:
        raise FileNotFoundError(f"no supported video files found in: {video_dir}")
    return paths


def main() -> None:
    args = parse_args()
    video_paths = resolve_video_paths(args)
    context = AnnotatorContext(
        video_paths=video_paths,
        output_dir=Path(args.output_dir).expanduser().resolve(),
        layout=LayoutConfig(rows=args.rows, cols=args.cols),
    )
    context.output_dir.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(context))
    url = f"http://{args.host}:{args.port}/"
    print(f"B-8Fall-Demo annotator: {url}")
    print(f"Videos: {len(video_paths)}")
    print(f"Output dir: {context.output_dir}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
