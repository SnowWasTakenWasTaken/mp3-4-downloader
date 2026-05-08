#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Missing dependency: yt-dlp")
    print("Install it with: pip install yt-dlp")
    sys.exit(1)


def download_source(url: str, output_dir: Path, audio_only: bool) -> Path:
    source_format = "bestaudio[ext=webm]/bestaudio" if audio_only else "best[ext=webm]/best"
    opts = {
        "format": source_format,
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "noplaylist": True,
        "quiet": False,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return Path(ydl.prepare_filename(info))


def resolve_ffmpeg_tools() -> tuple[str, str] | None:
    env_dir = os.environ.get("FFMPEG_DIR", "").strip()
    search_roots: list[Path] = []

    if env_dir:
        search_roots.append(Path(env_dir))
    if getattr(sys, "frozen", False):
        search_roots.append(Path(sys.executable).resolve().parent)

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        search_roots.append(Path(meipass))

    search_roots.append(Path(__file__).resolve().parent)

    unique_roots: list[Path] = []
    seen: set[str] = set()
    for root in search_roots:
        key = str(root).lower()
        if key not in seen:
            unique_roots.append(root)
            seen.add(key)

    for root in unique_roots:
        candidate_dirs = (root, root / "bin", root / "ffmpeg", root / "ffmpeg" / "bin")
        for directory in candidate_dirs:
            ffmpeg = directory / "ffmpeg.exe"
            ffprobe = directory / "ffprobe.exe"
            if ffmpeg.exists() and ffprobe.exists():
                return str(ffmpeg), str(ffprobe)

    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        return ffmpeg_path, ffprobe_path

    return None


def convert_media(source_path: Path, target_format: str, ffmpeg_cmd: str) -> Path:
    target_path = source_path.with_suffix(f".{target_format}")
    if target_format == "mp3":
        cmd = [
            ffmpeg_cmd,
            "-y",
            "-i",
            str(source_path),
            "-vn",
            "-acodec",
            "libmp3lame",
            "-q:a",
            "2",
            str(target_path),
        ]
    else:
        cmd = [
            ffmpeg_cmd,
            "-y",
            "-i",
            str(source_path),
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            str(target_path),
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        stderr = result.stderr.strip() or "Unknown ffmpeg error."
        raise RuntimeError(stderr)
    return target_path


def choose_format() -> str:
    while True:
        print("\nChoose download format:")
        print("1) MP3 (audio only)")
        print("2) MP4 (video)")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "mp3"
        if choice == "2":
            return "mp4"
        print("Invalid option. Please enter 1 or 2.")


def main() -> None:
    output_dir = Path.cwd() / "downloads"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("YouTube Downloader (MP3/MP4)")
    print("Type 'q' to quit.")
    print(f"Files will be saved in: {output_dir}")

    while True:
        url = input("\nPaste a YouTube link: ").strip()
        if url.lower() in {"q", "quit", "exit"}:
            print("Goodbye.")
            break
        if not url:
            print("No link provided. Try again.")
            continue

        fmt = choose_format()
        try:
            print("Downloading source file...")
            source = download_source(url, output_dir, audio_only=(fmt == "mp3"))
            print(f"Source downloaded: {source.name}")

            tools = resolve_ffmpeg_tools()
            if tools:
                ffmpeg_cmd, _ffprobe_cmd = tools
                print(f"Converting to {fmt.upper()}...")
                converted = convert_media(source, fmt, ffmpeg_cmd)
                print(f"Converted file: {converted.name}")
            else:
                print("ffmpeg/ffprobe not found. Keeping source file without conversion.")
                print("Set FFMPEG_DIR or bundle ffmpeg.exe + ffprobe.exe beside the EXE.")

            print("Done.")
        except Exception as exc:  # noqa: BLE001
            print(f"Download failed: {exc}")

        again = input("\nDownload another link? (y/n): ").strip().lower()
        if again not in {"y", "yes"}:
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()
