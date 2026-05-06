# ui.py
import os

from PySide6.QtCore import Qt, QThreadPool, QEvent
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFileDialog, QSlider, QGroupBox, 
                               QRadioButton, QProgressBar, QMessageBox, QCheckBox, 
                               QSpinBox, QListWidget, QAbstractItemView, QSizePolicy)

import config
from workers import FileWorker

class RemixMakerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pro Studio v6.0 (Modular)")
        self.resize(1000, 800)
        self.setStyleSheet(config.DARK_STYLE)
        
        # State
        self.file_list = []
        self.output_folder = ""
        self.thread_pool = QThreadPool()
        
        # Batch Processing Counters
        self.completed_count = 0
        self.total_count = 0
        
        self.setup_ui()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- LEFT PANEL: Queue & Folders ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setFixedWidth(380)

        # Input Group
        input_group = QGroupBox("Input Source")
        input_layout = QVBoxLayout()
        self.lbl_input_path = QLabel("Folder: None")
        self.lbl_input_path.setStyleSheet("color: #aaa;")
        input_layout.addWidget(self.lbl_input_path)
        
        input_btn_layout = QHBoxLayout()
        btn_cwd = QPushButton("Use CWD")
        btn_select_input = QPushButton("Select Folder")
        btn_cwd.clicked.connect(self.use_cwd_as_input)
        btn_select_input.clicked.connect(self.select_input_folder)
        input_btn_layout.addWidget(btn_cwd)
        input_btn_layout.addWidget(btn_select_input)
        input_layout.addLayout(input_btn_layout)
        
        self.drop_zone = QLabel(" Drop Files Here")
        self.drop_zone.setObjectName("DropZone")
        self.drop_zone.setAlignment(Qt.AlignCenter)
        self.drop_zone.setMinimumHeight(60)
        self.drop_zone.setAcceptDrops(True)
        self.drop_zone.installEventFilter(self)
        input_layout.addWidget(self.drop_zone)
        input_group.setLayout(input_layout)
        left_layout.addWidget(input_group)

        # File List
        self.file_list_widget = QListWidget()
        left_layout.addWidget(self.file_list_widget)

        queue_btn_layout = QHBoxLayout()
        btn_add = QPushButton("Add")
        btn_remove = QPushButton("Remove")
        btn_clear = QPushButton("Clear")
        btn_add.clicked.connect(self.browse_files)
        btn_remove.clicked.connect(self.remove_selected_files)
        btn_clear.clicked.connect(self.clear_file_list)
        queue_btn_layout.addWidget(btn_add)
        queue_btn_layout.addWidget(btn_remove)
        queue_btn_layout.addWidget(btn_clear)
        left_layout.addLayout(queue_btn_layout)

        # Output Group
        output_group = QGroupBox("Output Destination")
        output_layout = QVBoxLayout()
        self.chk_same_as_input = QCheckBox("Same as Input Folder")
        self.chk_same_as_input.setChecked(True)
        self.chk_same_as_input.toggled.connect(self.toggle_output_controls)
        output_layout.addWidget(self.chk_same_as_input)

        self.lbl_output_path = QLabel("Folder: (Same as Input)")
        self.lbl_output_path.setStyleSheet("color: #00ff00;")
        output_layout.addWidget(self.lbl_output_path)

        self.btn_select_output = QPushButton("Select Custom Output Folder")
        self.btn_select_output.setEnabled(False)
        self.btn_select_output.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.btn_select_output)
        output_group.setLayout(output_layout)
        left_layout.addWidget(output_group)

        main_layout.addWidget(left_panel)

        # --- RIGHT PANEL: Settings ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Presets
        preset_group = QGroupBox("Presets")
        preset_layout = QHBoxLayout()
        self.radio_nightcore = QRadioButton("Nightcore")
        self.radio_nightstep = QRadioButton("Nightstep")
        self.radio_slowed = QRadioButton("Slowed")
        self.radio_custom = QRadioButton("Custom")
        self.radio_nightcore.setChecked(True)
        
        self.radio_nightcore.toggled.connect(self.update_preset_mode)
        self.radio_nightstep.toggled.connect(self.update_preset_mode)
        self.radio_slowed.toggled.connect(self.update_preset_mode)
        self.radio_custom.toggled.connect(self.update_preset_mode)

        preset_layout.addWidget(self.radio_nightcore)
        preset_layout.addWidget(self.radio_nightstep)
        preset_layout.addWidget(self.radio_slowed)
        preset_layout.addWidget(self.radio_custom)
        preset_group.setLayout(preset_layout)
        right_layout.addWidget(preset_group)

        # Audio Controls
        controls_group = QGroupBox("Audio Controls")
        controls_layout = QVBoxLayout()
        controls_layout.addLayout(self.create_slider_row("Speed:", 50, 200, 130, "%"))
        controls_layout.addLayout(self.create_slider_row("Pitch:", -12, 12, 0, " st"))
        controls_layout.addLayout(self.create_slider_row("Reverb:", 0, 100, 0, "%"))
        
        # Fade Controls
        fade_layout = QHBoxLayout()
        fade_layout.addWidget(QLabel("Fade In:"))
        self.spin_fade_in = QSlider(Qt.Horizontal)
        self.spin_fade_in.setRange(0, 15)
        fade_layout.addWidget(self.spin_fade_in)
        self.lbl_fade_in = QLabel("0s")
        self.spin_fade_in.valueChanged.connect(lambda v: self.lbl_fade_in.setText(f"{v}s"))
        fade_layout.addWidget(self.lbl_fade_in)
        
        fade_layout.addWidget(QLabel("Out:"))
        self.spin_fade_out = QSlider(Qt.Horizontal)
        self.spin_fade_out.setRange(0, 15)
        fade_layout.addWidget(self.spin_fade_out)
        self.lbl_fade_out = QLabel("0s")
        self.spin_fade_out.valueChanged.connect(lambda v: self.lbl_fade_out.setText(f"{v}s"))
        fade_layout.addWidget(self.lbl_fade_out)
        controls_layout.addLayout(fade_layout)

        self.chk_bass = QPushButton("Bass Boost")
        self.chk_bass.setCheckable(True)
        controls_layout.addWidget(self.chk_bass)
        controls_group.setLayout(controls_layout)
        right_layout.addWidget(controls_group)

        # Performance
        perf_group = QGroupBox("Performance (Parallel)")
        perf_layout = QHBoxLayout()
        perf_layout.addWidget(QLabel("Simultaneous Files:"))
        self.spin_threads = QSpinBox()
        self.spin_threads.setRange(1, 10)
        self.spin_threads.setValue(4) # 4-10 files at once
        perf_layout.addWidget(self.spin_threads)
        perf_layout.addStretch()
        perf_group.setLayout(perf_layout)
        right_layout.addWidget(perf_group)

        # Process Button
        self.btn_process = QPushButton("START BATCH PROCESSING")
        self.btn_process.setObjectName("processBtn")
        right_layout.addWidget(self.btn_process)
        self.btn_process.clicked.connect(self.start_processing)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        right_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold; color: #aaa;")
        right_layout.addWidget(self.status_label)
        
        right_layout.addStretch()
        main_layout.addWidget(right_panel)

        # Initial UI State
        self.update_preset_mode()
        self.toggle_output_controls(self.chk_same_as_input.isChecked())

    def create_slider_row(self, label, min_val, max_val, default_val, suffix):
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label))
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_val, max_val)
        slider.setValue(default_val)
        label_display = QLabel(f"{default_val}{suffix}")
        label_display.setMinimumWidth(50)
        slider.valueChanged.connect(lambda v: label_display.setText(f"{v}{suffix}"))
        
        # Store references dynamically
        name = label.split(":")[0].lower()
        setattr(self, f"slider_{name}", slider)
        setattr(self, f"lbl_{name}", label_display)
        
        layout.addWidget(slider)
        layout.addWidget(label_display)
        return layout

    # --- Logic Methods ---
    def update_preset_mode(self):
        if self.radio_nightcore.isChecked():
            self.slider_speed.setValue(130); self.slider_pitch.setValue(0); self.slider_reverb.setValue(0); self.chk_bass.setChecked(False)
            self.coupled_mode = True
        elif self.radio_nightstep.isChecked():
            self.slider_speed.setValue(125); self.slider_pitch.setValue(0); self.slider_reverb.setValue(40); self.chk_bass.setChecked(True)
            self.coupled_mode = True
        elif self.radio_slowed.isChecked():
            self.slider_speed.setValue(85); self.slider_pitch.setValue(0); self.slider_reverb.setValue(60); self.chk_bass.setChecked(False)
            self.coupled_mode = True
        elif self.radio_custom.isChecked():
            self.coupled_mode = False

    def toggle_output_controls(self, checked):
        if checked:
            self.btn_select_output.setEnabled(False)
            self.lbl_output_path.setText("Folder: (Same as Input)")
        else:
            self.btn_select_output.setEnabled(True)
            if not self.output_folder: self.lbl_output_path.setText("Folder: Not Set")

    def use_cwd_as_input(self):
        cwd = os.getcwd()
        self.load_folder_to_list(cwd)
        self.lbl_input_path.setText(f"Folder: {cwd}")
        self.lbl_input_path.setStyleSheet("color: #00aaff;")

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.load_folder_to_list(folder)
            self.lbl_input_path.setText(f"Folder: {folder}")
            self.lbl_input_path.setStyleSheet("color: #00aaff;")

    def load_folder_to_list(self, folder_path):
        self.file_list = []
        self.file_list_widget.clear()
        found_files = False
        for root, dirs, files in os.walk(folder_path):
            for f in files:
                if f.lower().endswith(config.VALID_EXTENSIONS):
                    self.add_file(os.path.join(root, f))
                    found_files = True
        if found_files: self.status_label.setText(f"Loaded {len(self.file_list)} files.")

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_folder = folder
            self.lbl_output_path.setText(f"Folder: {folder}")
            self.lbl_output_path.setStyleSheet("color: #00ff00;")

    # Event Filter for Drag and Drop
    def eventFilter(self, obj, event):
        if obj == self.drop_zone:
            # CORRECTED: Use QEvent.Type.DragEnter and QEvent.Type.Drop
            if event.type() == QEvent.Type.DragEnter:
                event.acceptProposedAction()
                self.drop_zone.setProperty("active", "true")
                self.drop_zone.setStyleSheet(config.DARK_STYLE)
                return True
            elif event.type() == QEvent.Type.Drop:
                mime_data = event.mimeData()
                if mime_data.hasUrls():
                    for url in mime_data.urls():
                        path = url.toLocalFile()
                        if os.path.isdir(path): self.load_folder_to_list(path)
                        else: self.add_file(path)
                self.drop_zone.setProperty("active", "false")
                self.drop_zone.setStyleSheet(config.DARK_STYLE)
                return True
        return super().eventFilter(obj, event)

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Audio Files", "", f"Audio (*{' *'.join(config.VALID_EXTENSIONS)})")
        for f in files: self.add_file(f)

    def add_file(self, path):
        if path not in self.file_list:
            self.file_list.append(path)
            self.file_list_widget.addItem(os.path.basename(path))

    def remove_selected_files(self):
        for item in self.file_list_widget.selectedItems():
            row = self.file_list_widget.row(item)
            self.file_list_widget.takeItem(row)
            del self.file_list[row]

    def clear_file_list(self):
        self.file_list = []
        self.file_list_widget.clear()

    # --- Processing Logic ---
    def start_processing(self):
        if not self.file_list:
            QMessageBox.warning(self, "Empty Queue", "Please add files.")
            return

        target_output = ""
        if self.chk_same_as_input.isChecked():
            target_output = "" 
        else:
            if not self.output_folder:
                QMessageBox.warning(self, "No Output", "Select output folder.")
                return
            target_output = self.output_folder

        # Reset Counters
        self.completed_count = 0
        self.total_count = len(self.file_list)
        self.progress_bar.setValue(0)
        self.btn_process.setEnabled(False)
        self.status_label.setText("Initializing parallel processing...")

        # Set Thread Pool Concurrency
        max_threads = self.spin_threads.value()
        self.thread_pool.setMaxThreadCount(max_threads)
        
        # Determine Settings
        mode_suffix = "_remix"
        if self.radio_nightcore.isChecked(): mode_suffix = "_Nightcore"
        elif self.radio_nightstep.isChecked(): mode_suffix = "_Nightstep"
        elif self.radio_slowed.isChecked(): mode_suffix = "_Slowed"

        settings = {
            'speed': self.slider_speed.value(),
            'pitch': self.slider_pitch.value(),
            'bass_boost': self.chk_bass.isChecked(),
            'reverb': self.slider_reverb.value(),
            'fade_in': self.spin_fade_in.value(),
            'fade_out': self.spin_fade_out.value(),
            'coupled': self.coupled_mode,
            'mode_suffix': mode_suffix
        }

        # Launch Workers
        for input_path in self.file_list:
            worker = FileWorker(input_path, target_output, settings)
            worker.signals.finished.connect(self.on_file_finished)
            worker.signals.error.connect(self.on_file_error)
            self.thread_pool.start(worker)

    def on_file_finished(self, output_path):
        self.completed_count += 1
        self.update_batch_progress()
        
    def on_file_error(self, filename, msg):
        print(f"Error processing {filename}: {msg}") # Log to console
        self.completed_count += 1
        self.update_batch_progress()

    def update_batch_progress(self):
        perc = int((self.completed_count / self.total_count) * 100)
        self.progress_bar.setValue(perc)
        self.status_label.setText(f"Processing... {self.completed_count}/{self.total_count}")
        
        if self.completed_count == self.total_count:
            self.batch_complete()

    def batch_complete(self):
        self.btn_process.setEnabled(True)
        self.status_label.setText("Batch Complete!")
        QMessageBox.information(self, "Done", f"Batch Finished!\nProcessed {self.total_count} files.")