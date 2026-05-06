# config.py

DARK_STYLE = """
QMainWindow { background-color: #1e1e1e; }
QWidget { background-color: #2b2b2b; color: #e0e0e0; font-family: 'Segoe UI', Arial; }
QLabel { color: #cccccc; }
QGroupBox { 
    border: 1px solid #3d3d3d; 
    border-radius: 5px; 
    margin-top: 20px; 
    font-weight: bold;
    padding-top: 10px;
}
QGroupBox::title { 
    subcontrol-origin: margin; 
    left: 10px; 
    padding: 0 3px; 
    color: #00aaff; 
}
QPushButton { 
    background-color: #3d3d3d; 
    border: 1px solid #555; 
    border-radius: 4px; 
    padding: 8px; 
    color: white; 
}
QPushButton:hover { background-color: #4d4d4d; }
QPushButton:pressed { background-color: #0055aa; }
QPushButton:disabled { background-color: #2a2a2a; color: #555; }
QPushButton#processBtn { background-color: #0078d4; font-weight: bold; font-size: 14px; padding: 12px; }
QPushButton#processBtn:hover { background-color: #1084d8; }
QPushButton#processBtn:disabled { background-color: #333; }
QSlider::groove:horizontal { border: 1px solid #333; height: 8px; background: #1e1e1e; border-radius: 4px; }
QSlider::handle:horizontal { background: #0078d4; border: 1px solid #0055aa; width: 18px; margin: -5px 0; border-radius: 9px; }
QSlider::sub-page:horizontal { background: #0078d4; border-radius: 4px; }
QRadioButton::indicator { width: 13px; height: 13px; }
QRadioButton::indicator:checked { background-color: #0078d4; border: 2px solid #333; border-radius: 7px; }
QProgressBar { border: 1px solid #333; border-radius: 4px; text-align: center; background-color: #1e1e1e; color: white; }
QProgressBar::chunk { background-color: #0078d4; border-radius: 3px; }
QListWidget { 
    background-color: #1e1e1e; 
    border: 1px solid #3d3d3d; 
    border-radius: 5px; 
    padding: 5px; 
}
QListWidget::item { padding: 5px; }
QListWidget::item:selected { background-color: #0078d4; color: white; }
QSpinBox { background-color: #1e1e1e; border: 1px solid #555; border-radius: 3px; padding: 3px; }
#DropZone { 
    border: 2px dashed #555; 
    border-radius: 10px; 
    background-color: #252525; 
    font-size: 16px; 
    color: #777;
}
#DropZone[active="true"] { border-color: #0078d4; background-color: #2a3a4a; color: #fff; }
"""

VALID_EXTENSIONS = ('.mp3', '.wav', '.ogg', '.flac', '.m4a')