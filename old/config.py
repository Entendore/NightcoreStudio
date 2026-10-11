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