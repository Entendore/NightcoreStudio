import sys
import os
import yt_dlp
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QProgressBar, QTextEdit)
from PySide6.QtCore import QThread, Signal, Qt

class DownloadThread(QThread):
    """
    Worker thread to handle yt-dlp downloads without freezing the GUI.
    """
    progress_signal = Signal(int)       
    status_signal = Signal(str)         
    log_signal = Signal(str)            
    finished_signal = Signal(bool)      

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.is_cancelled = False

    def run(self):
        output_dir = "input"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.log_signal.emit(f"Created directory: {output_dir}")

        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            
            # Post-processor to extract audio and convert to mp3
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0', 
            }],
            
            'sleep_interval': 5, 
            
            # --- FIXES APPLIED HERE ---
            # 1. Ignore errors (like copyright blocks) and continue to next video in playlist
            'ignoreerrors': True, 
            
            # 2. Attempt to bypass geographical restrictions
            'geo_bypass': True,
            # --------------------------
            
            'progress_hooks': [self._progress_hook],
            
            # 'quiet': True is better for GUIs, but we keep verbose logs for debugging if needed
            'quiet': True, 
            'no_warnings': True,
            # Optional: Hook to capture yt-dlp console output to GUI
            'logger': self._YtdlLogger(self.log_signal), 
        }

        try:
            self.status_signal.emit("Starting download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # download returns 0 on success, but ignoreerrors handles the flow
                ydl.download([self.url])
            self.finished_signal.emit(True)
        except Exception as e:
            self.log_signal.emit(f"Critical Error: {str(e)}")
            self.finished_signal.emit(False)

    # Custom logger class to pipe yt-dlp messages to the GUI
    class _YtdlLogger:
        def __init__(self, signal):
            self.signal = signal
        def debug(self, msg):
            if '[download]' in msg or '[info]' in msg:
                self.signal.emit(msg)
        def warning(self, msg):
            self.signal.emit(f"Warning: {msg}")
        def error(self, msg):
            self.signal.emit(f"Error: {msg}")

    def _progress_hook(self, d):
        if self.is_cancelled:
            raise Exception("Download cancelled by user")

        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)
            
            if total:
                percent = int(downloaded * 100 / total)
                self.progress_signal.emit(percent)
            
            filename = d.get('filename', 'file')
            self.status_signal.emit(f"Downloading: {os.path.basename(filename)}")

        elif d['status'] == 'finished':
            self.status_signal.emit("Processing (Converting to MP3)...")
            self.progress_signal.emit(100)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Audio Downloader")
        self.resize(500, 300)
        self.download_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label_url = QLabel("YouTube URL:")
        layout.addWidget(self.label_url)
        
        self.input_url = QLineEdit()
        self.input_url.setPlaceholderText("Paste link here (Video or Playlist)")
        layout.addWidget(self.input_url)

        self.btn_download = QPushButton("Download")
        self.btn_download.clicked.connect(self.start_download)
        layout.addWidget(self.btn_download)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        self.label_status = QLabel("Ready")
        self.label_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_status)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(100)
        layout.addWidget(self.log_area)

        self.setLayout(layout)

    def start_download(self):
        url = self.input_url.text().strip()
        
        if not url:
            self.log_area.append("Please enter a valid URL.")
            return

        self.btn_download.setEnabled(False)
        self.btn_download.setText("Downloading...")
        self.log_area.clear()
        self.log_area.append(f"Target: {url}")
        self.log_area.append("Files will be saved in './input' folder.")
        
        self.download_thread = DownloadThread(url)
        
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.status_signal.connect(self.update_status)
        self.download_thread.log_signal.connect(self.append_log)
        self.download_thread.finished_signal.connect(self.on_download_finished)
        
        self.download_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_status(self, text):
        self.label_status.setText(text)

    def append_log(self, text):
        self.log_area.append(text)

    def on_download_finished(self, success):
        self.btn_download.setEnabled(True)
        self.btn_download.setText("Download")
        
        if success:
            self.update_status("Process finished.")
            self.progress_bar.setValue(100)
        else:
            self.update_status("Download failed or cancelled.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())