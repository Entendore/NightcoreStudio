# Nightcore App

A desktop application built with PySide6 for batch-remixing audio files into Nightcore, Nightstep, Slowed, or custom variations using FFmpeg.

## Features
* **Batch Processing:** Queue multiple files and render them concurrently with configurable thread counts.
* **Audio Controls:** Adjust speed, pitch, reverb, bass boost, and fade in/out.
* **Presets:** One-click modes for Nightcore, Nightstep, and Slowed + Reverb.
* **YouTube Import:** Directly download and queue audio from YouTube URLs via `yt-dlp`.
* **Drag & Drop:** Add files or entire folders via drag-and-drop or file picker.
* **Smart Queue:** Skip already-processed files, or re-render them. Supports mid-batch cancellation.
* **Modern UI:** Dark-themed, responsive interface with real-time progress tracking and activity logging.

## Prerequisites
* **Python 3.9+**
* **FFmpeg & FFprobe:** Must be installed and accessible in your system's `PATH`. ([Download FFmpeg](https://ffmpeg.org/download.html))

## Installation

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <your-repo-folder>
   ```

2. Install Python dependencies:
   ```bash
   pip install PySide6 yt-dlp
   ```

## Usage

Run the application:
```bash
python app.py
```

### Workflow
1. **Add Files:** Drag and drop audio files/folders into the drop zone, click "Add Files/Folder", or paste a YouTube URL and click "Download Audio".
2. **Configure:** Select a Preset (Nightcore, Nightstep, Slowed) or choose "Custom" to manually adjust sliders and effects.
3. **Set Output:** Check "Save to same folder as source" or browse for a specific output directory.
4. **Render:** Click **RENDER ALL** or select specific files and click **RENDER SELECTED**.
5. **Monitor:** View progress in the progress bar and check the Activity Log for detailed status updates. You can click **STOP** to gracefully cancel the batch.

## How It Works
* **Audio Engine:** Uses `FFmpeg` to apply an audio filter chain (`-af`) dynamically generated based on UI settings. 
* **Pitch/Speed:** Uses `asetrate` and chained `atempo` filters for precise, coupled, or decoupled pitch/speed manipulation.
* **Effects:** Applies `aecho` for reverb, `bass` for EQ, `afade` for fades, and `alimiter` to prevent clipping.
* **Threading:** Uses `QThreadPool` and `QRunnable` to process multiple files concurrently without freezing the UI.
