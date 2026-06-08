import os
import yt_dlp
from PySide6.QtCore import QThread, Signal


class DownloadThread(QThread):
    """Downloads audio from YouTube in a background thread."""

    progress_signal = Signal(int)
    status_signal = Signal(str)
    log_signal = Signal(str)
    finished_signal = Signal(bool, str)

    def __init__(self, url: str, output_dir: str = "input"):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def run(self):
        os.makedirs(self.output_dir, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{self.output_dir}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
            'ignoreerrors': True,
            'geo_bypass': True,
            'progress_hooks': [self._hook],
            'quiet': True,
            'no_warnings': True,
        }

        try:
            self.status_signal.emit("Starting download…")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished_signal.emit(True, os.path.abspath(self.output_dir))
        except Exception as e:
            self.log_signal.emit(f"Critical error: {e}")
            self.finished_signal.emit(False, self.output_dir)

    def _hook(self, d):
        if self._cancel:
            raise Exception("Cancelled by user")
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            done = d.get('downloaded_bytes', 0)
            if total:
                self.progress_signal.emit(int(done * 100 / total))
            self.status_signal.emit(f"Downloading: {os.path.basename(d.get('filename', ''))}")
        elif d['status'] == 'finished':
            self.status_signal.emit("Converting to MP3…")
            self.progress_signal.emit(100)