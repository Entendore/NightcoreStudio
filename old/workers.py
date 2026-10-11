import os
import subprocess
import json
import time
from PySide6.QtCore import QRunnable, Signal, QObject
from utils import calculate_filter_chain


class WorkerSignals(QObject):
    """Signals emitted from a worker thread back to the main thread."""
    finished = Signal(str, str)   # input_path, output_path
    error = Signal(str, str)      # input_path, error_message


class FileWorker(QRunnable):
    """Processes a single audio file with FFmpeg. Supports cancellation."""

    def __init__(self, input_path: str, output_folder: str,
                 settings: dict, cancel_event=None):
        super().__init__()
        self.input_path = input_path
        self.output_folder = output_folder
        self.settings = settings
        self.cancel_event = cancel_event   # threading.Event — shared across batch
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    def run(self):
        try:
            # Check cancel before starting
            if self._cancelled():
                self.signals.error.emit(self.input_path, "Cancelled")
                return

            # ── 1. Output path ──
            base = os.path.basename(self.input_path)
            name_no_ext = os.path.splitext(base)[0]
            suffix = self.settings.get('mode_suffix', '_remix')
            out_name = f"{name_no_ext}{suffix}.mp3"
            save_dir = (self.output_folder if self.output_folder
                        else os.path.dirname(self.input_path))
            output_path = os.path.join(save_dir, out_name)

            # ── 2. Probe duration ──
            probe = [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json", self.input_path
            ]
            result = subprocess.run(
                probe, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            data = json.loads(result.stdout)
            total_duration = float(data['format']['duration'])

            # ── 3. Build filter ──
            filter_str = calculate_filter_chain(self.settings, total_duration)

            # ── 4. Execute FFmpeg (with cancel polling) ──
            cmd = [
                "ffmpeg", "-i", self.input_path,
                "-af", filter_str,
                "-y", "-ac", "2", "-ar", "44100",
                "-b:a", "320k",
                output_path
            ]

            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Poll instead of wait() so we can react to cancellation
            while proc.poll() is None:
                if self._cancelled():
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=3)
                    # Clean up partial file
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except OSError:
                            pass
                    self.signals.error.emit(self.input_path, "Cancelled by user")
                    return
                time.sleep(0.15)

            if proc.returncode == 0:
                self.signals.finished.emit(self.input_path, output_path)
            else:
                err = proc.stderr.read()[-400:] if proc.stderr else "Unknown FFmpeg error"
                self.signals.error.emit(self.input_path, err)

        except Exception as e:
            self.signals.error.emit(self.input_path, str(e))

    def _cancelled(self) -> bool:
        return self.cancel_event is not None and self.cancel_event.is_set()