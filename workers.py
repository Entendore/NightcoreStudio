# workers.py
import os
import subprocess
import json
from PySide6.QtCore import QRunnable, Signal, QObject
from utils import calculate_filter_chain

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    finished = Signal(str)       # Emits output path on success
    error = Signal(str, str)     # Emits filename, error message
    progress = Signal(int)       # Emits percentage (not used in parallel batch but kept for single file)

class FileWorker(QRunnable):
    """
    Worker thread for processing a single audio file.
    Used in conjunction with QThreadPool for parallel execution.
    """
    def __init__(self, input_path, output_folder, settings):
        super().__init__()
        self.input_path = input_path
        self.output_folder = output_folder
        self.settings = settings
        self.signals = WorkerSignals()
        self.setAutoDelete(True)

    def run(self):
        try:
            # 1. Determine Output Path
            base_name = os.path.basename(self.input_path)
            name_no_ext = os.path.splitext(base_name)[0]
            mode_suffix = self.settings.get('mode_suffix', '_remix')
            output_filename = f"{name_no_ext}{mode_suffix}.mp3"
            
            # Handle "Same as Input" logic (empty output_folder string)
            save_dir = self.output_folder if self.output_folder else os.path.dirname(self.input_path)
            output_path = os.path.join(save_dir, output_filename)

            # 2. Get Audio Duration (needed for Fade Out)
            probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", self.input_path]
            result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            duration_data = json.loads(result.stdout)
            total_duration = float(duration_data['format']['duration'])

            # 3. Build FFmpeg Command
            filter_str = calculate_filter_chain(self.settings, total_duration)

            command = [
                "ffmpeg",
                "-i", self.input_path,
                "-af", filter_str,
                "-y",           # Overwrite
                "-ac", "2",     # Stereo
                "-ar", "44100", # Standard sample rate
                output_path
            ]

            # 4. Execute
            # In batch mode, we skip progress updates for performance
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            process.wait()

            if process.returncode == 0:
                self.signals.finished.emit(output_path)
            else:
                err = process.stderr.read()
                self.signals.error.emit(os.path.basename(self.input_path), err[:200])

        except Exception as e:
            self.signals.error.emit(os.path.basename(self.input_path), str(e))