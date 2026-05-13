#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlparse

try:
    import yt_dlp
except ImportError:
    print("Missing dependency: yt-dlp")
    print("Install it with: pip install yt-dlp")
    sys.exit(1)


def download_source(
    url: str,
    output_dir: Path,
    audio_only: bool,
    download_playlist: bool,
) -> list[Path]:
    source_format = "bestaudio[ext=webm]/bestaudio" if audio_only else "best[ext=webm]/best"
    outtmpl = "%(playlist_index)s - %(title)s.%(ext)s" if download_playlist else "%(title)s.%(ext)s"
    downloaded_files: list[Path] = []
    seen: set[str] = set()

    def progress_hook(status: dict) -> None:
        if status.get("status") != "finished":
            return
        filename = status.get("filename")
        if not filename:
            return
        file_path = Path(filename)
        key = str(file_path).lower()
        if key in seen:
            return
        seen.add(key)
        downloaded_files.append(file_path)
    opts = {
        "format": source_format,
        "outtmpl": str(output_dir / outtmpl),
        "noplaylist": not download_playlist,
        "quiet": False,
        "progress_hooks": [progress_hook],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    if not downloaded_files:
        raise RuntimeError("No downloadable media was found for the provided link.")
    return downloaded_files


def resolve_ffmpeg_tools() -> tuple[str, str] | None:
    ffmpeg_names = ["ffmpeg.exe", "ffmpeg"]
    ffprobe_names = ["ffprobe.exe", "ffprobe"]
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
            for ffmpeg_name in ffmpeg_names:
                for ffprobe_name in ffprobe_names:
                    ffmpeg = directory / ffmpeg_name
                    ffprobe = directory / ffprobe_name
                    if ffmpeg.exists() and ffprobe.exists():
                        return str(ffmpeg), str(ffprobe)

    ffmpeg_path = shutil.which("ffmpeg")
    ffprobe_path = shutil.which("ffprobe")
    if ffmpeg_path and ffprobe_path:
        return ffmpeg_path, ffprobe_path

    return None


def convert_media(source_path: Path, target_format: str, ffmpeg_cmd: str) -> Path:
    target_ext = f".{target_format}"
    if source_path.suffix.lower() == target_ext:
        return source_path
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


def is_playlist_url(url: str) -> bool:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    playlist_id = params.get("list", [""])[0].strip()
    return bool(playlist_id)


def choose_playlist_scope() -> bool:
    while True:
        print("\nPlaylist detected:")
        print("1) Download entire playlist")
        print("2) Download only the currently selected video")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return True
        if choice == "2":
            return False
        print("Invalid option. Please enter 1 or 2.")

def get_default_output_dir() -> Path:
    downloads_dir = Path.home() / "Downloads"
    if downloads_dir.exists():
        return downloads_dir / "YouTube Downloader"
    return Path.home() / "YouTube Downloader"


def main() -> None:
    output_dir = get_default_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(r"""
__  __           ______      __            ____                      __                __              __   __  _______ _____         __     __  _______  __ __     _ 
\ \/ /___  __  _/_  __/_  __/ /_  ___     / __ \____ _      ______  / /___  ____ _____/ /__  _____   _/_/  /  |/  / __ \__  /       _/_/    /  |/  / __ \/ // /    | |
 \  / __ \/ / / // / / / / / __ \/ _ \   / / / / __ \ | /| / / __ \/ / __ \/ __ `/ __  / _ \/ ___/  / /   / /|_/ / /_/ //_ <      _/_/     / /|_/ / /_/ / // /_    / /
 / / /_/ / /_/ // / / /_/ / /_/ /  __/  / /_/ / /_/ / |/ |/ / / / / / /_/ / /_/ / /_/ /  __/ /     / /   / /  / / ____/__/ /    _/_/      / /  / / ____/__  __/   / / 
/_/\____/\__,_//_/  \__,_/_.___/\___/  /_____/\____/|__/|__/_/ /_/_/\____/\__,_/\__,_/\___/_/     / /   /_/  /_/_/   /____/    /_/       /_/  /_/_/      /_/    _/_/  
                                                                                                  |_|                                                          /_/    
""")
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
        download_playlist = False
        if is_playlist_url(url):
            download_playlist = choose_playlist_scope()

        fmt = choose_format()
        try:
            print("Downloading source file(s)...")
            sources = download_source(
                url=url,
                output_dir=output_dir,
                audio_only=(fmt == "mp3"),
                download_playlist=download_playlist,
            )
            print(f"Downloaded {len(sources)} source file(s).")

            tools = resolve_ffmpeg_tools()
            if tools:
                ffmpeg_cmd, _ffprobe_cmd = tools
                for index, source in enumerate(sources, start=1):
                    print(f"Converting ({index}/{len(sources)}): {source.name}")
                    converted = convert_media(source, fmt, ffmpeg_cmd)
                    print(f"Converted file: {converted.name}")
                    if converted.resolve() != source.resolve():
                        source.unlink(missing_ok=True)
            else:
                print("ffmpeg/ffprobe not found. Keeping source files without conversion.")
                print("Set FFMPEG_DIR or bundle ffmpeg.exe + ffprobe.exe beside the EXE.")

            print("Done.")
        except Exception as exc:  # noqa: BLE001
            print(f"Download failed: {exc}")

        again = input("\nDownload another link? (y/n): ").strip().lower()
        if again not in {"y", "yes"}:
            print("Goodbye.")
            break


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"Fatal error: {exc}")
        if getattr(sys, "frozen", False):
            try:
                input("Press Enter to close...")
            except EOFError:
                pass
        sys.exit(1)
