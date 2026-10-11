import os
import sys
import math
import json
import time
import threading
import subprocess
from datetime import datetime

from PySide6.QtCore import Qt, QThreadPool, QEvent, QThread, QRunnable, Signal, QObject
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFileDialog, QSlider, QGroupBox,
    QRadioButton, QProgressBar, QMessageBox, QCheckBox,
    QSpinBox, QListWidget, QListWidgetItem, QAbstractItemView,
    QLineEdit, QTextEdit, QFrame, QButtonGroup
)

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════

DARK_STYLE = """
/* ─── Base ─── */
QMainWindow, QDialog {
    background-color: #0d1117;
}
QWidget {
    background-color: transparent;
    color: #e6edf3;
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial;
    font-size: 13px;
}
QLabel {
    background: transparent;
    color: #e6edf3;
}

/* ─── Group Box (Card) ─── */
QGroupBox {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    margin-top: 28px;
    padding: 18px 16px 14px 16px;
    font-weight: 600;
    font-size: 13px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 2px 10px;
    color: #58a6ff;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* ─── Buttons ─── */
QPushButton {
    background-color: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 7px 14px;
    color: #e6edf3;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #30363d;
    border-color: #8b949e;
}
QPushButton:pressed {
    background-color: #58a6ff;
    color: #0d1117;
}
QPushButton:disabled {
    background-color: #161b22;
    color: #484f58;
    border-color: #21262d;
}
QPushButton:checked {
    background-color: #1f6feb;
    border-color: #58a6ff;
    color: #ffffff;
}

/* ─── Primary Actions ─── */
QPushButton#renderAllBtn {
    background-color: #238636;
    border: 1px solid #2ea043;
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    padding: 13px 20px;
    border-radius: 8px;
}
QPushButton#renderAllBtn:hover { background-color: #2ea043; }
QPushButton#renderAllBtn:disabled { background-color: #162b1e; color: #2ea043; border-color: #162b1e; }

QPushButton#renderSelectedBtn {
    background-color: #1f6feb;
    border: 1px solid #388bfd;
    color: #ffffff;
    font-weight: 700;
    font-size: 14px;
    padding: 13px 20px;
    border-radius: 8px;
}
QPushButton#renderSelectedBtn:hover { background-color: #388bfd; }
QPushButton#renderSelectedBtn:disabled { background-color: #0d1d33; color: #1f6feb; border-color: #0d1d33; }

QPushButton#stopBtn {
    background-color: #da3633;
    border: 1px solid #f85149;
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    padding: 10px 20px;
    border-radius: 8px;
}
QPushButton#stopBtn:hover { background-color: #f85149; }
QPushButton#stopBtn:disabled { background-color: #2a1215; color: #da3633; border-color: #2a1215; }

/* ─── Sliders ─── */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #30363d;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #58a6ff;
    border: 2px solid #0d1117;
    width: 18px;
    height: 18px;
    margin: -7px 0;
    border-radius: 9px;
}
QSlider::sub-page:horizontal {
    background: #58a6ff;
    border-radius: 3px;
}
QSlider::groove:horizontal:disabled { background: #21262d; }
QSlider::handle:horizontal:disabled { background: #484f58; border-color: #161b22; }

/* ─── Progress Bar ─── */
QProgressBar {
    border: none;
    border-radius: 8px;
    text-align: center;
    background-color: #21262d;
    color: #e6edf3;
    min-height: 26px;
    font-weight: 700;
    font-size: 12px;
}
QProgressBar::chunk {
    background-color: #238636;
    border-radius: 8px;
}
QProgressBar#warningBar QProgressBar::chunk {
    background-color: #d29922;
}

/* ─── List Widget ─── */
QListWidget {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 4px;
    outline: none;
    font-size: 13px;
}
QListWidget::item {
    padding: 6px 10px;
    border-radius: 5px;
    margin: 1px 2px;
}
QListWidget::item:selected {
    background-color: #1f6feb33;
    color: #ffffff;
}
QListWidget::item:hover {
    background-color: #161b22;
}
QListWidget::indicator {
    width: 16px;
    height: 16px;
}

/* ─── Checkbox ─── */
QCheckBox {
    spacing: 8px;
    background: transparent;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 2px solid #30363d;
    background-color: #0d1117;
}
QCheckBox::indicator:checked {
    background-color: #58a6ff;
    border-color: #58a6ff;
}
QCheckBox::indicator:hover {
    border-color: #58a6ff;
}

/* ─── Radio Button ─── */
QRadioButton {
    spacing: 6px;
    background: transparent;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #30363d;
    background-color: #0d1117;
}
QRadioButton::indicator:checked {
    background-color: #58a6ff;
    border-color: #58a6ff;
}

/* ─── Spin Box ─── */
QSpinBox {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 5px 8px;
    color: #e6edf3;
    min-width: 60px;
}
QSpinBox:focus { border-color: #58a6ff; }

/* ─── Line Edit ─── */
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e6edf3;
    font-size: 13px;
}
QLineEdit:focus { border-color: #58a6ff; }
QLineEdit::placeholder { color: #484f58; }

/* ─── Text Edit (Log) ─── */
QTextEdit {
    background-color: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 8px;
    color: #8b949e;
    font-family: 'Cascadia Code', 'SF Mono', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
}

/* ─── Drop Zone ─── */
#DropZone {
    border: 2px dashed #30363d;
    border-radius: 12px;
    background-color: #0d1117;
    font-size: 14px;
    color: #484f58;
}
#DropZone[active="true"] {
    border-color: #58a6ff;
    background-color: #0d1b2a;
    color: #58a6ff;
}

/* ─── Scroll Bar ─── */
QScrollBar:vertical {
    background: #0d1117;
    width: 10px;
    border-radius: 5px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #30363d;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #484f58; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

/* ─── Tool Button ─── */
QPushButton#toolBtn {
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 600;
}

/* ─── Status Label ─── */
QLabel#statusLabel {
    font-weight: 700;
    font-size: 14px;
    padding: 4px;
}
"""

VALID_EXTENSIONS = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac', '.wma', '.opus')

PRESETS = {
    'nightcore':  {'speed': 130, 'pitch': 0,  'reverb': 0,  'bass': False, 'coupled': True},
    'nightstep':  {'speed': 125, 'pitch': 0,  'reverb': 40, 'bass': True,  'coupled': True},
    'slowed':     {'speed': 85,  'pitch': 0,  'reverb': 60, 'bass': False, 'coupled': True},
}

# ═══════════════════════════════════════════════════════════════
#  UTILS
# ═══════════════════════════════════════════════════════════════

def calculate_filter_chain(settings: dict, total_duration: float) -> str:
    filter_chain = []

    tempo = settings['speed'] / 100.0
    pitch_semitones = settings['pitch']

    # ── Pitch & Speed ──
    if settings.get('coupled'):
        # Coupled mode: speed change naturally shifts pitch
        if tempo > 0 and abs(tempo - 1.0) > 0.001:
            pitch_from_speed = 12 * math.log2(max(tempo, 0.01))
            total_pitch = pitch_from_speed + pitch_semitones
            rate_mult = 2 ** (total_pitch / 12)
            filter_chain.append(f"asetrate=44100*{rate_mult:.6f}")

            correction = rate_mult / max(tempo, 0.01)
            # FIX: skip atempo when correction ≈ 1.0 — FFmpeg rejects atempo=1.0
            if abs(correction - 1.0) > 0.001:
                filter_chain.extend(_atempo_chain(1.0 / correction))
        elif pitch_semitones != 0:
            # Speed is ~1.0 but user wants pitch shift
            pitch_mult = 2 ** (pitch_semitones / 12)
            filter_chain.append(f"asetrate=44100*{pitch_mult:.6f}")
            filter_chain.extend(_atempo_chain(1.0 / pitch_mult))
    else:
        # Custom mode: independent pitch and speed
        if pitch_semitones != 0:
            pitch_mult = 2 ** (pitch_semitones / 12)
            filter_chain.append(f"asetrate=44100*{pitch_mult:.6f}")
            filter_chain.extend(_atempo_chain(1.0 / pitch_mult))

        if tempo > 0 and abs(tempo - 1.0) > 0.001:
            filter_chain.extend(_atempo_chain(tempo))

    # ── Reverb (BEFORE bass boost to avoid boosting the reverb tail) ──
    reverb_amount = settings.get('reverb', 0)
    if reverb_amount > 0:
        mix = reverb_amount / 100.0
        # Short delays for a natural room-reverb feel, not a 1-second echo
        delay_ms = int(25 + 75 * mix)       # 25–100 ms
        out_gain = 0.30 + mix * 0.30        # 0.30–0.60  (keeps overall volume sane)
        decay    = 0.10 + mix * 0.25        # 0.10–0.35
        filter_chain.append(
            f"aecho=0.8:{out_gain:.2f}:{delay_ms}:{decay:.2f}"
        )

    # ── Bass Boost ──
    if settings.get('bass_boost'):
        filter_chain.append("bass=g=5:f=100:w=0.5")

    # ── Fade ──
    fade_in = settings.get('fade_in', 0)
    fade_out = settings.get('fade_out', 0)
    if fade_in > 0:
        filter_chain.append(f"afade=t=in:st=0:d={fade_in}")
    if fade_out > 0:
        start_t = max(0, total_duration - fade_out)
        filter_chain.append(f"afade=t=out:st={start_t:.3f}:d={fade_out}")

    # ── Limiter (always last — prevents clipping from any above filter) ──
    filter_chain.append("alimiter=limit=0.95:attack=5:release=50")

    return ",".join(filter_chain)


def _atempo_chain(rate: float) -> list:
    if rate < 0.5:
        return _atempo_chain(rate / 0.5) + ["atempo=0.5"]
    if rate > 100.0:
        return _atempo_chain(rate / 100.0) + ["atempo=100.0"]
    return [f"atempo={rate:.6f}"]


# ═══════════════════════════════════════════════════════════════
#  WORKERS
# ═══════════════════════════════════════════════════════════════

class WorkerSignals(QObject):
    finished = Signal(str, str)   # input_path, output_path
    error = Signal(str, str)      # input_path, error_message


class FileWorker(QRunnable):
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

            while proc.poll() is None:
                if self._cancelled():
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=3)
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


# ═══════════════════════════════════════════════════════════════
#  DOWNLOAD
# ═══════════════════════════════════════════════════════════════

class DownloadThread(QThread):
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
        if yt_dlp is None:
            self.log_signal.emit("yt-dlp is not installed. Please install it via 'pip install yt-dlp'")
            self.finished_signal.emit(False, self.output_dir)
            return

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


# ═══════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════

STATUS_IDLE       = "idle"
STATUS_QUEUED     = "queued"
STATUS_PROCESSING = "processing"
STATUS_DONE       = "done"
STATUS_ERROR      = "error"
STATUS_CANCELLED  = "cancelled"

STATUS_DISPLAY = {
    STATUS_IDLE:       ("   ", "#8b949e"),
    STATUS_QUEUED:     (" ⏳", "#d29922"),
    STATUS_PROCESSING: (" ⚙", "#58a6ff"),
    STATUS_DONE:       (" ✓", "#3fb950"),
    STATUS_ERROR:      (" ✗", "#f85149"),
    STATUS_CANCELLED:  (" ⏹", "#8b949e"),
}


class RemixMakerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Studio Pro  —  Batch Remix Engine")
        self.resize(1300, 820)
        self.setMinimumSize(1050, 680)
        self.setStyleSheet(DARK_STYLE)

        # ── File state ──
        self.file_item_map: dict[str, QListWidgetItem] = {}
        self.file_status: dict[str, str] = {}           # path → STATUS_*

        # ── Output ──
        self.output_folder = ""

        # ── Threading ──
        self.thread_pool = QThreadPool()
        self.download_thread = None

        # ── Batch processing state ──
        self.is_processing = False
        self.cancel_event = threading.Event()
        self.processing_queue: list[str] = []
        self.active_workers = 0
        self.completed_count = 0
        self.total_count = 0
        self.error_count = 0
        self.current_settings: dict = {}
        self.target_output = ""

        self._build_ui()

    # ═══════════════════════════════════════════════════════════
    #  UI Construction
    # ═══════════════════════════════════════════════════════════

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # Accent bar
        accent = QFrame()
        accent.setFixedWidth(3)
        accent.setStyleSheet("background-color: #58a6ff; border-radius: 1px;")
        root.addWidget(accent)

        # LEFT
        left = self._build_left_panel()
        root.addWidget(left, stretch=0)

        # Divider
        div = QFrame()
        div.setFixedWidth(1)
        div.setStyleSheet("background-color: #30363d;")
        root.addWidget(div)

        # RIGHT
        right = self._build_right_panel()
        root.addWidget(right, stretch=1)

        # Init
        self._sync_preset()
        self._toggle_output_controls(self.chk_same_as_input.isChecked())

    # ─── Left Panel ───────────────────────────────────────────

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(440)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # ── File Queue ──
        q_grp = QGroupBox("FILE  QUEUE")
        q_lay = QVBoxLayout(q_grp)
        q_lay.setSpacing(6)

        # Drop zone
        self.drop_zone = QLabel("  📂  Drop audio files or folders here")
        self.drop_zone.setObjectName("DropZone")
        self.drop_zone.setAlignment(Qt.AlignCenter)
        self.drop_zone.setMinimumHeight(56)
        self.drop_zone.setAcceptDrops(True)
        self.drop_zone.installEventFilter(self)
        q_lay.addWidget(self.drop_zone)

        # Toolbar 1
        tb1 = QHBoxLayout()
        tb1.setSpacing(4)
        for text, slot in [
            ("＋ Add Files", self.browse_files),
            ("📁 Add Folder", self.select_input_folder),
            ("✕ Remove", self.remove_selected_files),
            ("🗑 Clear", self.clear_file_list),
        ]:
            btn = QPushButton(text)
            btn.setObjectName("toolBtn")
            btn.clicked.connect(slot)
            tb1.addWidget(btn)
        q_lay.addLayout(tb1)

        # Toolbar 2 — select controls + count
        tb2 = QHBoxLayout()
        tb2.setSpacing(4)
        for text, slot in [("☑ All", self.select_all_files),
                           ("☐ None", self.deselect_all_files)]:
            btn = QPushButton(text)
            btn.setObjectName("toolBtn")
            btn.clicked.connect(slot)
            tb2.addWidget(btn)
        tb2.addStretch()
        self.lbl_count = QLabel("0 files")
        self.lbl_count.setStyleSheet("color:#8b949e; font-size:12px; font-weight:600;")
        tb2.addWidget(self.lbl_count)
        q_lay.addLayout(tb2)

        # File list
        self.file_list_widget = QListWidget()
        self.file_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list_widget.setMinimumHeight(120)
        self.file_list_widget.itemChanged.connect(self._on_item_changed)
        q_lay.addWidget(self.file_list_widget, stretch=1)

        lay.addWidget(q_grp, stretch=1)

        # ── Output ──
        o_grp = QGroupBox("OUTPUT")
        o_lay = QVBoxLayout(o_grp)
        o_lay.setSpacing(6)

        self.chk_same_as_input = QCheckBox("Save to same folder as source")
        self.chk_same_as_input.setChecked(True)
        self.chk_same_as_input.toggled.connect(self._toggle_output_controls)
        o_lay.addWidget(self.chk_same_as_input)

        self.lbl_output_path = QLabel("Folder:  (Same as source)")
        self.lbl_output_path.setStyleSheet("color:#3fb950; font-size:12px;")
        self.lbl_output_path.setWordWrap(True)
        o_lay.addWidget(self.lbl_output_path)

        self.btn_select_output = QPushButton("📂  Browse Output Folder")
        self.btn_select_output.setEnabled(False)
        self.btn_select_output.clicked.connect(self.select_output_folder)
        o_lay.addWidget(self.btn_select_output)

        lay.addWidget(o_grp)

        # ── YouTube Download ──
        yt_grp = QGroupBox("YOUTUBE  DOWNLOAD")
        yt_lay = QVBoxLayout(yt_grp)
        yt_lay.setSpacing(6)

        self.input_yt_url = QLineEdit()
        self.input_yt_url.setPlaceholderText("Paste YouTube video / playlist URL…")
        yt_lay.addWidget(self.input_yt_url)

        yt_row = QHBoxLayout()
        self.btn_yt_download = QPushButton("⬇  Download Audio")
        self.btn_yt_download.clicked.connect(self.start_yt_download)
        yt_row.addWidget(self.btn_yt_download, stretch=1)
        self.yt_progress = QProgressBar()
        self.yt_progress.setValue(0)
        self.yt_progress.setFixedHeight(20)
        self.yt_progress.setMaximumWidth(160)
        yt_row.addWidget(self.yt_progress)
        yt_lay.addLayout(yt_row)

        self.lbl_yt_status = QLabel("Ready")
        self.lbl_yt_status.setStyleSheet("color:#8b949e; font-size:11px;")
        yt_lay.addWidget(self.lbl_yt_status)

        lay.addWidget(yt_grp)

        return panel

    # ─── Right Panel ──────────────────────────────────────────

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # ── Presets ──
        p_grp = QGroupBox("PRESETS")
        p_lay = QHBoxLayout(p_grp)
        self.preset_group = QButtonGroup(self)
        for name in ["Nightcore", "Nightstep", "Slowed", "Custom"]:
            radio = QRadioButton(name)
            self.preset_group.addButton(radio)
            p_lay.addWidget(radio)
            setattr(self, f"radio_{name.lower()}", radio)
        self.radio_nightcore.setChecked(True)
        self.preset_group.buttonClicked.connect(self._sync_preset)
        lay.addWidget(p_grp)

        # ── Audio Controls ──
        c_grp = QGroupBox("AUDIO  CONTROLS")
        c_lay = QGridLayout(c_grp)
        c_lay.setHorizontalSpacing(14)
        c_lay.setVerticalSpacing(10)

        self._add_slider(c_lay, 0, "Speed", 50, 200, 130, "%")
        self._add_slider(c_lay, 1, "Pitch", -12, 12, 0, " st")
        self._add_slider(c_lay, 2, "Reverb", 0, 100, 0, "%")

        c_lay.addWidget(QLabel("Bass Boost"), 3, 0)
        self.chk_bass = QPushButton("Bass Boost")
        self.chk_bass.setCheckable(True)
        self.chk_bass.setMinimumHeight(30)
        c_lay.addWidget(self.chk_bass, 3, 1, 1, 2)

        c_lay.addWidget(QLabel("Fade In"), 4, 0)
        self.slider_fade_in = QSlider(Qt.Horizontal)
        self.slider_fade_in.setRange(0, 15)
        self.slider_fade_in.setValue(0)
        self.lbl_fade_in = QLabel("0 s")
        self.lbl_fade_in.setMinimumWidth(42)
        self.slider_fade_in.valueChanged.connect(lambda v: self.lbl_fade_in.setText(f"{v} s"))
        c_lay.addWidget(self.slider_fade_in, 4, 1)
        c_lay.addWidget(self.lbl_fade_in, 4, 2)

        c_lay.addWidget(QLabel("Fade Out"), 5, 0)
        self.slider_fade_out = QSlider(Qt.Horizontal)
        self.slider_fade_out.setRange(0, 15)
        self.slider_fade_out.setValue(0)
        self.lbl_fade_out = QLabel("0 s")
        self.lbl_fade_out.setMinimumWidth(42)
        self.slider_fade_out.valueChanged.connect(lambda v: self.lbl_fade_out.setText(f"{v} s"))
        c_lay.addWidget(self.slider_fade_out, 5, 1)
        c_lay.addWidget(self.lbl_fade_out, 5, 2)

        lay.addWidget(c_grp)

        # ── Performance ──
        pf_grp = QGroupBox("PERFORMANCE")
        pf_lay = QHBoxLayout(pf_grp)
        pf_lay.addWidget(QLabel("Parallel threads:"))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 16)
        self.spin_threads.setValue(4)
        pf_lay.addWidget(self.spin_threads)
        pf_lay.addStretch()
        lay.addWidget(pf_grp)

        # ── Skip completed ──
        skip_row = QHBoxLayout()
        self.chk_skip_done = QCheckBox("Skip already-completed files on render")
        self.chk_skip_done.setChecked(True)
        self.chk_skip_done.setStyleSheet("color:#8b949e; font-size:12px;")
        skip_row.addWidget(self.chk_skip_done)
        skip_row.addStretch()
        lay.addLayout(skip_row)

        # ── Action Buttons ──
        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.btn_render_all = QPushButton("▶   RENDER  ALL")
        self.btn_render_all.setObjectName("renderAllBtn")
        self.btn_render_all.clicked.connect(self._on_render_all)

        self.btn_render_selected = QPushButton("▶   RENDER  SELECTED")
        self.btn_render_selected.setObjectName("renderSelectedBtn")
        self.btn_render_selected.clicked.connect(self._on_render_selected)

        self.btn_stop = QPushButton("⏹   STOP")
        self.btn_stop.setObjectName("stopBtn")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self._on_stop)

        actions.addWidget(self.btn_render_all, stretch=3)
        actions.addWidget(self.btn_render_selected, stretch=3)
        actions.addWidget(self.btn_stop, stretch=1)
        lay.addLayout(actions)

        # ── Progress ──
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        lay.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color:#8b949e; font-size:13px; font-weight:700; padding:2px;")
        lay.addWidget(self.status_label)

        # ── Activity Log ──
        lg_grp = QGroupBox("ACTIVITY  LOG")
        lg_lay = QVBoxLayout(lg_grp)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(100)
        lg_lay.addWidget(self.log_area)

        btn_clear_log = QPushButton("Clear Log")
        btn_clear_log.setObjectName("toolBtn")
        btn_clear_log.clicked.connect(self.log_area.clear)
        lg_lay.addWidget(btn_clear_log)

        lay.addWidget(lg_grp, stretch=1)

        return panel

    # ─── Slider Helper ────────────────────────────────────────

    def _add_slider(self, grid, row, name, lo, hi, default, suffix):
        grid.addWidget(QLabel(name), row, 0)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(lo, hi)
        slider.setValue(default)
        lbl = QLabel(f"{default}{suffix}")
        lbl.setMinimumWidth(50)
        lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        slider.valueChanged.connect(lambda v, s=suffix, l=lbl: l.setText(f"{v}{s}"))
        grid.addWidget(slider, row, 1)
        grid.addWidget(lbl, row, 2)
        setattr(self, f"slider_{name.lower()}", slider)
        setattr(self, f"lbl_{name.lower()}", lbl)

    # ═══════════════════════════════════════════════════════════
    #  File List Management
    # ═══════════════════════════════════════════════════════════

    def _on_item_changed(self, item):
        self._refresh_count()

    def _refresh_count(self):
        total = self.file_list_widget.count()
        checked = sum(
            1 for i in range(total)
            if self.file_list_widget.item(i).checkState() == Qt.Checked
        )
        self.lbl_count.setText(f"{checked} / {total} selected")

    def _add_file(self, path: str):
        if path in self.file_item_map:
            return
        basename = os.path.basename(path)
        item = QListWidgetItem(f"    {basename}")
        item.setData(Qt.UserRole, path)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked)
        item.setForeground(QColor("#8b949e"))
        self.file_list_widget.addItem(item)
        self.file_item_map[path] = item
        self.file_status[path] = STATUS_IDLE
        self._refresh_count()

    def _remove_file(self, path: str):
        item = self.file_item_map.pop(path, None)
        self.file_status.pop(path, None)
        if item:
            row = self.file_list_widget.row(item)
            self.file_list_widget.takeItem(row)
            self._refresh_count()

    def _get_all_paths(self) -> list[str]:
        return [
            self.file_list_widget.item(i).data(Qt.UserRole)
            for i in range(self.file_list_widget.count())
        ]

    def _get_checked_paths(self) -> list[str]:
        return [
            self.file_list_widget.item(i).data(Qt.UserRole)
            for i in range(self.file_list_widget.count())
            if self.file_list_widget.item(i).checkState() == Qt.Checked
        ]

    def _is_file_done(self, path: str) -> bool:
        return self.file_status.get(path) == STATUS_DONE

    def _get_renderable(self, paths: list[str]) -> list[str]:
        if self.chk_skip_done.isChecked():
            renderable = [p for p in paths if not self._is_file_done(p)]
            skipped = len(paths) - len(renderable)
            if skipped > 0:
                self._log(f"⏩  Skipping {skipped} already-completed file(s)", "#8b949e")
            return renderable
        return list(paths)

    def _set_file_status(self, file_path: str, status: str):
        self.file_status[file_path] = status
        item = self.file_item_map.get(file_path)
        if not item:
            return
        basename = os.path.basename(file_path)
        icon, color = STATUS_DISPLAY.get(status, ("   ", "#8b949e"))
        item.setText(f" {icon}  {basename}")
        item.setForeground(QColor(color))

    # ─── Button Handlers (File List) ──────────────────────────

    def browse_files(self):
        exts = ' '.join(f'*{e}' for e in VALID_EXTENSIONS)
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Audio Files", "", f"Audio ({exts})"
        )
        for f in files:
            self._add_file(f)

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Audio Folder")
        if folder:
            self._load_folder(folder)

    def remove_selected_files(self):
        for item in self.file_list_widget.selectedItems():
            path = item.data(Qt.UserRole)
            self._remove_file(path)

    def clear_file_list(self):
        self.file_list_widget.clear()
        self.file_item_map.clear()
        self.file_status.clear()
        self._refresh_count()

    def select_all_files(self):
        for i in range(self.file_list_widget.count()):
            self.file_list_widget.item(i).setCheckState(Qt.Checked)

    def deselect_all_files(self):
        for i in range(self.file_list_widget.count()):
            self.file_list_widget.item(i).setCheckState(Qt.Unchecked)

    def _load_folder(self, folder: str):
        count_before = len(self.file_item_map)
        for root, _, files in os.walk(folder):
            for f in files:
                if f.lower().endswith(VALID_EXTENSIONS):
                    self._add_file(os.path.join(root, f))
        added = len(self.file_item_map) - count_before
        self._log(f"📂  Scanned folder — {added} new file(s) added", "#58a6ff")

    # ─── Drag & Drop ──────────────────────────────────────────

    def eventFilter(self, obj, event):
        if obj is self.drop_zone:
            if event.type() == QEvent.Type.DragEnter:
                event.acceptProposedAction()
                self.drop_zone.setProperty("active", "true")
                self.drop_zone.style().unpolish(self.drop_zone)
                self.drop_zone.style().polish(self.drop_zone)
                return True
            elif event.type() == QEvent.Type.DragLeave:
                self.drop_zone.setProperty("active", "false")
                self.drop_zone.style().unpolish(self.drop_zone)
                self.drop_zone.style().polish(self.drop_zone)
                return True
            elif event.type() == QEvent.Type.Drop:
                for url in event.mimeData().urls():
                    path = url.toLocalFile()
                    if os.path.isdir(path):
                        self._load_folder(path)
                    elif path.lower().endswith(VALID_EXTENSIONS):
                        self._add_file(path)
                self.drop_zone.setProperty("active", "false")
                self.drop_zone.style().unpolish(self.drop_zone)
                self.drop_zone.style().polish(self.drop_zone)
                return True
        return super().eventFilter(obj, event)

    # ─── Output Folder ────────────────────────────────────────

    def _toggle_output_controls(self, same: bool):
        self.btn_select_output.setEnabled(not same)
        if same:
            self.lbl_output_path.setText("Folder:  (Same as source)")
            self.lbl_output_path.setStyleSheet("color:#3fb950; font-size:12px;")
        elif not self.output_folder:
            self.lbl_output_path.setText("Folder:  Not set")
            self.lbl_output_path.setStyleSheet("color:#f85149; font-size:12px;")

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.lbl_output_path.setText(f"Folder:  {folder}")
            self.lbl_output_path.setStyleSheet("color:#3fb950; font-size:12px;")

    # ─── Presets ──────────────────────────────────────────────

    def _sync_preset(self):
        p = None
        if self.radio_nightcore.isChecked():
            p = PRESETS['nightcore']
        elif self.radio_nightstep.isChecked():
            p = PRESETS['nightstep']
        elif self.radio_slowed.isChecked():
            p = PRESETS['slowed']

        if p:
            self.slider_speed.setValue(p['speed'])
            self.slider_pitch.setValue(p['pitch'])
            self.slider_reverb.setValue(p['reverb'])
            self.chk_bass.setChecked(p['bass'])
            self.coupled_mode = True
        else:
            self.coupled_mode = False

    # ═══════════════════════════════════════════════════════════
    #  Batch Processing — Render / Stop / Restart
    # ═══════════════════════════════════════════════════════════

    def _on_render_all(self):
        paths = self._get_all_paths()
        if not paths:
            QMessageBox.warning(self, "Empty Queue", "Add audio files before rendering.")
            return
        renderable = self._get_renderable(paths)
        if not renderable:
            QMessageBox.information(self, "Nothing to Render",
                                    "All files are already completed.\n\n"
                                    "Uncheck 'Skip already-completed files' to re-render.")
            return
        self._start_batch(renderable)

    def _on_render_selected(self):
        paths = self._get_checked_paths()
        if not paths:
            QMessageBox.warning(self, "Nothing Selected",
                                "Check the files you want to render first.")
            return
        renderable = self._get_renderable(paths)
        if not renderable:
            QMessageBox.information(self, "Nothing to Render",
                                    "All selected files are already completed.\n\n"
                                    "Uncheck 'Skip already-completed files' to re-render.")
            return
        self._start_batch(renderable)

    def _on_stop(self):
        self.cancel_event.set()
        self._log("⚠  Stop requested — terminating active workers…", "#d29922")
        self.status_label.setText("Stopping…")
        self.status_label.setStyleSheet("color:#d29922; font-size:13px; font-weight:700; padding:2px;")
        self.btn_stop.setEnabled(False)

    # ─── Batch Engine ─────────────────────────────────────────

    def _start_batch(self, files: list[str]):
        # Output
        if self.chk_same_as_input.isChecked():
            self.target_output = ""
        else:
            if not self.output_folder:
                QMessageBox.warning(self, "No Output", "Select an output folder first.")
                return
            self.target_output = self.output_folder

        # Mode suffix
        if self.radio_nightcore.isChecked():
            suffix = "_Nightcore"
        elif self.radio_nightstep.isChecked():
            suffix = "_Nightstep"
        elif self.radio_slowed.isChecked():
            suffix = "_Slowed"
        else:
            suffix = "_remix"

        self.current_settings = {
            'speed':      self.slider_speed.value(),
            'pitch':      self.slider_pitch.value(),
            'bass_boost': self.chk_bass.isChecked(),
            'reverb':     self.slider_reverb.value(),
            'fade_in':    self.slider_fade_in.value(),
            'fade_out':   self.slider_fade_out.value(),
            'coupled':    self.coupled_mode,
            'mode_suffix': suffix,
        }

        # Reset batch state
        self.processing_queue = list(files)
        self.total_count = len(files)
        self.completed_count = 0
        self.error_count = 0
        self.active_workers = 0
        self.cancel_event.clear()
        self.is_processing = True

        # UI
        self._set_processing_ui(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("")  # reset to default green

        # Mark all files in this batch
        for fp in files:
            self._set_file_status(fp, STATUS_QUEUED)

        self._log(f"🚀  Batch started — {self.total_count} file(s), "
                  f"{self.spin_threads.value()} thread(s)", "#58a6ff")

        # Launch
        self.thread_pool.setMaxThreadCount(self.spin_threads.value())
        self._launch_next()

    def _launch_next(self):
        max_t = self.spin_threads.value()

        # If cancelled, don't launch new workers
        if self.cancel_event.is_set():
            if self.active_workers == 0:
                self._batch_complete()
            return

        # Launch up to max_t workers
        while self.active_workers < max_t and self.processing_queue:
            file_path = self.processing_queue.pop(0)
            self._set_file_status(file_path, STATUS_PROCESSING)
            self._log(f"⚙  Processing: {os.path.basename(file_path)}", "#58a6ff")

            worker = FileWorker(
                file_path, self.target_output,
                self.current_settings, self.cancel_event
            )
            worker.signals.finished.connect(self._on_worker_finished)
            worker.signals.error.connect(self._on_worker_error)
            self.active_workers += 1
            self.thread_pool.start(worker)

        # Check if everything is done
        if not self.processing_queue and self.active_workers == 0:
            self._batch_complete()

    def _on_worker_finished(self, input_path: str, output_path: str):
        self.active_workers -= 1
        self.completed_count += 1
        self._set_file_status(input_path, STATUS_DONE)
        self._log(f"✓  Done: {os.path.basename(output_path)}", "#3fb950")
        self._update_progress()
        self._launch_next()

    def _on_worker_error(self, input_path: str, error_msg: str):
        self.active_workers -= 1
        self.completed_count += 1

        # Distinguish cancellation from real errors
        if "Cancelled" in error_msg:
            self._set_file_status(input_path, STATUS_CANCELLED)
            self._log(f"⏹  Cancelled: {os.path.basename(input_path)}", "#8b949e")
        else:
            self.error_count += 1
            self._set_file_status(input_path, STATUS_ERROR)
            short = error_msg.replace('\n', ' ')[:150]
            self._log(f"✗  Error: {os.path.basename(input_path)} — {short}", "#f85149")

        self._update_progress()
        self._launch_next()

    def _update_progress(self):
        if self.total_count == 0:
            return
        pct = int(self.completed_count / self.total_count * 100)
        self.progress_bar.setValue(pct)
        self.status_label.setText(
            f"Processing…  {self.completed_count} / {self.total_count}  "
            f"({pct}%)  •  {self.error_count} error(s)"
        )

    def _batch_complete(self):
        self.is_processing = False
        self._set_processing_ui(False)

        was_cancelled = self.cancel_event.is_set()
        success_count = self.total_count - self.error_count

        # Count how many were cancelled (not processed at all)
        cancelled_count = sum(
            1 for fp, st in self.file_status.items()
            if st == STATUS_CANCELLED
        )
        remaining = self.total_count - self.completed_count

        if was_cancelled:
            self.progress_bar.setValue(self.progress_bar.value())  # freeze at current
            self.progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #d29922; border-radius: 8px; }"
            )
            self.status_label.setText(
                f"⏹  Stopped — {success_count} done, {self.error_count} error(s), "
                f"{remaining + cancelled_count} remaining"
            )
            self.status_label.setStyleSheet(
                "color:#d29922; font-size:13px; font-weight:700; padding:2px;"
            )
            self._log(
                f"⏹  Batch stopped — {success_count} completed, "
                f"{self.error_count} error(s), "
                f"{remaining + cancelled_count} remaining\n"
                f"     Click Render All or Render Selected to continue.",
                "#d29922"
            )
        else:
            self.progress_bar.setValue(100)
            self.progress_bar.setStyleSheet("")  # default green
            if self.error_count == 0:
                self.status_label.setText(
                    f"✓  Batch complete — {success_count} file(s) rendered"
                )
                self.status_label.setStyleSheet(
                    "color:#3fb950; font-size:13px; font-weight:700; padding:2px;"
                )
            else:
                self.status_label.setText(
                    f"Batch complete — {success_count} done, {self.error_count} error(s)"
                )
                self.status_label.setStyleSheet(
                    "color:#f85149; font-size:13px; font-weight:700; padding:2px;"
                )
                self.progress_bar.setStyleSheet(
                    "QProgressBar::chunk { background-color: #f85149; border-radius: 8px; }"
                )
            self._log(
                f"🏁  Batch complete — {success_count} rendered, "
                f"{self.error_count} error(s)", "#3fb950"
            )

        # Show summary dialog
        if was_cancelled:
            QMessageBox.information(
                self, "Batch Stopped",
                f"Processing was stopped.\n\n"
                f"  ✓  Rendered:       {success_count}\n"
                f"  ✗  Errors:           {self.error_count}\n"
                f"  ⏹  Remaining:    {remaining + cancelled_count}\n\n"
                f"You can click Render All or Render Selected\n"
                f"to continue processing the remaining files."
            )
        else:
            QMessageBox.information(
                self, "Batch Complete",
                f"Finished processing {self.total_count} file(s).\n\n"
                f"  ✓  Rendered:  {success_count}\n"
                f"  ✗  Errors:    {self.error_count}"
            )

    # ─── Processing UI State ──────────────────────────────────

    def _set_processing_ui(self, busy: bool):
        self.btn_render_all.setEnabled(not busy)
        self.btn_render_selected.setEnabled(not busy)
        self.btn_stop.setEnabled(busy)
        self.file_list_widget.setEnabled(not busy)
        # Prevent changing skip logic mid-batch
        self.chk_skip_done.setEnabled(not busy)

    # ───────────────────────────────────────────────────────────
    #  YouTube Downloader
    # ───────────────────────────────────────────────────────────

    def start_yt_download(self):
        url = self.input_yt_url.text().strip()
        if not url:
            return

        self.btn_yt_download.setEnabled(False)
        self.btn_yt_download.setText("Downloading…")
        self.yt_progress.setValue(0)
        self.lbl_yt_status.setText("Starting…")
        self._log(f"⬇  YouTube download started: {url}", "#bc8cff")

        self.download_thread = DownloadThread(url, "input")
        self.download_thread.progress_signal.connect(self.yt_progress.setValue)
        self.download_thread.status_signal.connect(self.lbl_yt_status.setText)
        self.download_thread.log_signal.connect(lambda m: self._log(m, "#8b949e"))
        self.download_thread.finished_signal.connect(self._on_yt_finished)
        self.download_thread.start()

    def _on_yt_finished(self, success: bool, output_dir: str):
        self.btn_yt_download.setEnabled(True)
        self.btn_yt_download.setText("⬇  Download Audio")

        if success:
            self.lbl_yt_status.setText("Download complete!")
            self._load_folder(output_dir)
            self._log("✓  YouTube download complete — files added to queue", "#3fb950")
        else:
            self.lbl_yt_status.setText("Download failed.")
            self._log("✗  YouTube download failed", "#f85149")

        self.download_thread = None

    # ───────────────────────────────────────────────────────────
    #  Logging
    # ───────────────────────────────────────────────────────────

    def _log(self, message: str, color: str = "#e6edf3"):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_area.append(
            f'<span style="color:#484f58;">[{ts}]</span> '
            f'<span style="color:{color};">{message}</span>'
        )
        # Auto-scroll to bottom
        sb = self.log_area.verticalScrollBar()
        sb.setValue(sb.maximum())


# ═══════════════════════════════════════════════════════════════
#  APPLICATION ENTRY POINT
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = RemixMakerApp()
    window.show()
    sys.exit(app.exec())