![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/SnowWasTakenWasTaken/mp3-4-downloader/total?style=for-the-badge)

[![Download latest release](https://img.shields.io/badge/Download-Latest%20Release-blue?style=for-the-badge)](https://github.com/SnowWasTakenWasTaken/mp3-4-downloader/releases/download/v2/YouTubeDownloaderSetup.exe)

## Program Description

This project is a command-line YouTube downloader and converter built in Python using `yt-dlp` and `ffmpeg`. It accepts YouTube links, supports both single videos and playlists, allows output selection as MP3 or MP4, and automatically removes temporary source files after successful conversion so the user ends up with only final media files.

The application is also designed to work well both as a normal Python script and as a packaged executable (for example, with PyInstaller), including logic to find bundled `ffmpeg` binaries when distributed as an `.exe`.

---

## How the Program Works (End-to-End)

1. **Startup and dependency check**
   - On startup, the script imports required Python modules and attempts to import `yt_dlp`.
   - If `yt-dlp` is missing, it prints an install message and exits immediately.

2. **Output directory initialization**
   - The program creates a default output folder in a user-writable location:
     - Preferred: `~/Downloads/YouTube Downloader`
     - Fallback: `~/YouTube Downloader`
   - This avoids permission problems common with protected install folders.

3. **Interactive main loop**
   - The user is prompted to paste a YouTube URL.
   - Entering `q`, `quit`, or `exit` ends the program.
   - Empty input is rejected with a retry message.

4. **Playlist detection and scope selection**
   - The program checks the URL query string for a `list` parameter.
   - If present, the user is prompted to choose:
     - Download the **entire playlist**
     - Download only the **currently selected video** in that playlist URL

5. **Format selection**
   - The user selects output format:
     - `1` = MP3 (audio-only)
     - `2` = MP4 (video)

6. **Source download phase**
   - Media is first downloaded in source form (typically WebM preference).
   - For playlist downloads, files are named with playlist index prefix (for stable ordering).
   - A progress hook captures every completed source file path, including multi-item playlist downloads.

7. **ffmpeg discovery**
   - The program attempts to find `ffmpeg` and `ffprobe` in this order:
     1. Directory from `FFMPEG_DIR` environment variable
     2. Directory of the running executable (when packaged/frozen)
     3. PyInstaller extraction directory (`_MEIPASS`)
     4. Script directory
     5. System `PATH`
   - If not found, source files are kept and conversion is skipped with a clear message.

8. **Conversion phase**
   - Each downloaded source file is converted to selected format:
     - MP3: uses `libmp3lame` with quality setting
     - MP4: uses `libx264` video + `aac` audio with faststart optimization
   - If file is already in target extension, conversion is skipped for that file.

9. **Temporary file cleanup**
   - After successful conversion, the original source file is deleted.
   - This ensures users only keep final `.mp3` or `.mp4` outputs when conversion succeeds.

10. **Repeat or exit**
    - User can choose to download another URL or exit.

11. **Top-level fatal error handling**
    - Unhandled exceptions are caught at the entry point.
    - In frozen/executable mode, the app waits for user input before closing so errors are visible.

---

## Function-by-Function Breakdown

### `download_source(url, output_dir, audio_only, download_playlist) -> list[Path]`
**Purpose:** Download one or more source media files using `yt-dlp`.

**Behavior:**
- Chooses source format:
  - Audio-only mode prefers `bestaudio[ext=webm]`
  - Video mode prefers `best[ext=webm]`
- Chooses output filename template:
  - Playlist mode includes `%(playlist_index)s - %(title)s`
  - Single mode uses `%(title)s`
- Sets `noplaylist` based on user playlist choice.
- Registers a **progress hook** that collects completed download filenames.
- Returns a list of downloaded file paths.
- Raises a `RuntimeError` if no files were downloaded.

---

### `resolve_ffmpeg_tools() -> tuple[str, str] | None`
**Purpose:** Locate usable `ffmpeg.exe` and `ffprobe.exe`.

**Behavior:**
- Builds a list of candidate roots from environment/runtime context.
- Searches common subfolders under each root (`bin`, `ffmpeg`, `ffmpeg/bin`).
- Falls back to `shutil.which("ffmpeg")` / `shutil.which("ffprobe")`.
- Returns `(ffmpeg_path, ffprobe_path)` when found.
- Returns `None` when tools are not found.

---

### `convert_media(source_path, target_format, ffmpeg_cmd) -> Path`
**Purpose:** Convert a source media file to the target format.

**Behavior:**
- If source extension already matches target (`.mp3` or `.mp4`), returns source unchanged.
- Builds an ffmpeg command:
  - **MP3:** strips video, encodes with `libmp3lame`, quality-based output
  - **MP4:** encodes video with `libx264`, audio with `aac`, adds `+faststart`
- Executes conversion via `subprocess.run`.
- Raises `RuntimeError` with ffmpeg stderr on failure.
- Returns output file path on success.

---

### `choose_format() -> str`
**Purpose:** Collect and validate output format choice from user.

**Behavior:**
- Repeatedly prompts until valid input is entered.
- Returns `"mp3"` or `"mp4"`.

---

### `is_playlist_url(url) -> bool`
**Purpose:** Detect whether a pasted URL refers to a playlist context.

**Behavior:**
- Parses URL query params.
- Returns `True` if a non-empty `list` parameter exists.

---

### `choose_playlist_scope() -> bool`
**Purpose:** Ask user whether to download full playlist or only current video.

**Behavior:**
- Repeated prompt until valid input.
- Returns:
  - `True` for entire playlist
  - `False` for single selected video

---

### `get_default_output_dir() -> Path`
**Purpose:** Choose a safe default destination folder.

**Behavior:**
- Prefers `~/Downloads/YouTube Downloader` if `Downloads` exists.
- Otherwise uses `~/YouTube Downloader`.

---

### `main() -> None`
**Purpose:** Orchestrate interactive program flow.

**Behavior:**
- Creates output directory.
- Runs URL input loop.
- Handles quit/empty input.
- Performs playlist detection and user scope selection.
- Performs format selection.
- Downloads sources.
- Resolves ffmpeg tools.
- Converts each source.
- Deletes source files after successful conversion.
- Prompts whether to continue.

---

### Top-level entry block
```python
if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        ...
```
**Purpose:** Provide robust fatal error handling for both script and packaged executable use.

**Behavior:**
- Prints fatal error message.
- In frozen executable mode, pauses for user input before exit so error details remain visible.

---

## Key Design Characteristics

- Supports both **single-video** and **playlist-aware** workflows.
- Uses **temporary source download + conversion** model.
- Automatically cleans temporary media after successful conversion.
- Handles missing ffmpeg gracefully instead of hard-crashing.
- Includes runtime logic compatible with **bundled ffmpeg in packaged `.exe` builds**.
