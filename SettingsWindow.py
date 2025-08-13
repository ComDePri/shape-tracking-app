import os
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QSlider, QPushButton, QGridLayout, QGroupBox
)
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import Qt


class SettingsWindow(QDialog):
    SETTINGS_FILE = "settings.txt"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(600, 600)

        self.values = self.load_settings_file()
        layout = QVBoxLayout()

        # --- Stimuli Duration ---
        self.stimuli_input = QLineEdit(str(self.values.get("stimuli_duration", 5.0)))
        self.stimuli_input.setValidator(QDoubleValidator(0.0, 9999.0, 3))
        layout.addLayout(self._labeled_row("Transition duration (s):", self.stimuli_input))

        # --- Drawing Duration ---
        self.drawing_input = QLineEdit(str(self.values.get("drawing_duration", 5.0)))
        self.drawing_input.setValidator(QDoubleValidator(0.0, 9999.0, 3))
        layout.addLayout(self._labeled_row("Drawing duration (s):", self.drawing_input))

        # # --- Corner Location ---
        # self.corner_checkboxes = {
        #     (0, 0): QCheckBox("Top-Left"),
        #     (0, 1): QCheckBox("Top-Right"),
        #     (1, 0): QCheckBox("Bottom-Left"),
        #     (1, 1): QCheckBox("Bottom-Right"),
        # }
        # corner_group = QGroupBox("Corner Location")
        # corner_layout = QGridLayout()
        # for (r, c), cb in self.corner_checkboxes.items():
        #     cb.toggled.connect(lambda checked, key=(r, c): self._exclusive_corner_selection(key))
        #     corner_layout.addWidget(cb, r, c)
        # corner_group.setLayout(corner_layout)
        # layout.addWidget(corner_group)
        #
        # current_loc = tuple(map(int, self.values.get("corner_location", "0,0").split(",")))
        # if current_loc in self.corner_checkboxes:
        #     self.corner_checkboxes[current_loc].setChecked(True)
        #
        # # --- Scale ---
        # scale_row = QHBoxLayout()
        # scale_row.setContentsMargins(0, 0, 0, 0)
        # scale_row.setSpacing(10)
        #
        # scale_label = QLabel("Template Scale:")
        # scale_label.setFixedHeight(20)
        #
        # self.scale_value_label = QLabel()
        # self.scale_value_label.setFixedWidth(40)
        # self.scale_value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        #
        # self.scale_slider = QSlider(Qt.Horizontal)
        # self.scale_slider.setMinimum(10)
        # self.scale_slider.setMaximum(200)
        # self.scale_slider.setFixedHeight(20)
        #
        # initial_scale = int(float(self.values.get("corner_scale", 1.0)) * 100)
        # self.scale_slider.setValue(initial_scale)
        # self.scale_value_label.setText(f"{initial_scale / 100:.2f}")
        # self.scale_slider.valueChanged.connect(self.update_scale_display)
        #
        # scale_row.addWidget(scale_label)
        # scale_row.addWidget(self.scale_slider)
        # scale_row.addWidget(self.scale_value_label)
        # layout.addLayout(scale_row)

        # --- Show Intro ---
        intro_group = QGroupBox()
        intro_layout = QHBoxLayout()

        self.intro_checkbox = QCheckBox("Show Intro")
        intro_layout.addWidget(self.intro_checkbox)

        intro_group.setLayout(intro_layout)
        layout.addWidget(intro_group)

        # --- Template visibility options ---
        template_group = QGroupBox("Template Visibility")
        template_layout = QHBoxLayout()
        self.template_checkboxes = {}

        all_templates = ["Show Template", "Hide Template"]
        saved_templates = self.values.get("template", "Show Template,Hide Template").split(",")

        for option in all_templates:
            cb = QCheckBox(option)
            cb.setChecked(option in saved_templates)
            template_layout.addWidget(cb)
            self.template_checkboxes[option] = cb

        template_group.setLayout(template_layout)
        layout.addWidget(template_group)

        # --- Speeds ---
        speed_group = QGroupBox("Select Speeds")
        speed_layout = QHBoxLayout()
        self.speed_checkboxes = {}

        all_speeds = ["fast", "medium", "slow", "comfort"]
        saved_speeds = self.values.get("speeds", "fast,medium,slow,comfort").split(",")

        for speed in all_speeds:
            cb = QCheckBox(speed)
            cb.setChecked(speed in saved_speeds)
            speed_layout.addWidget(cb)
            self.speed_checkboxes[speed] = cb

        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)

        # --- Shapes ---
        shape_group = QGroupBox("Shapes")
        shape_layout = QGridLayout()
        self.shape_checkboxes = []

        shape_files = [f"assets/shape{i}.svg" for i in range(1, 10)]
        selected_ids = list(map(int, self.values.get("shapes", "1,2,3,4,5,6,7,8,9").split(",")))

        for idx, path in enumerate(shape_files):
            row = idx // 3
            col = (idx % 3) * 2
            shape_id = int(path.replace("assets/shape", "").replace(".svg", ""))

            svg = QSvgWidget(path)
            svg.setFixedSize(60, 60)  # increased from 50 to avoid clipping
            svg.setStyleSheet("background-color: transparent;")  # optional: ensures no weird borders
            shape_layout.addWidget(svg, row, col)

            cb = QCheckBox(os.path.basename(path))
            cb.setChecked(shape_id in selected_ids)
            shape_layout.addWidget(cb, row, col + 1)

            self.shape_checkboxes.append((cb, shape_id))

        shape_group.setLayout(shape_layout)
        layout.addWidget(shape_group)

        # --- Buttons ---
        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.save_to_file)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def _labeled_row(self, label, widget):
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        row.addWidget(widget)
        return row

    # def update_scale_display(self, val):
    #     self.scale_value_label.setText(f"{val / 100:.2f}")
    #
    # def _exclusive_corner_selection(self, selected_key):
    #     for key, cb in self.corner_checkboxes.items():
    #         cb.blockSignals(True)
    #         cb.setChecked(key == selected_key)
    #         cb.blockSignals(False)
    #
    # def get_selected_corner(self):
    #     for key, cb in self.corner_checkboxes.items():
    #         if cb.isChecked():
    #             return f"{key[0]},{key[1]}"
    #     return "0,0"

    def load_settings_file(self):
        if not os.path.exists(self.SETTINGS_FILE):
            return {}

        values = {}
        with open(self.SETTINGS_FILE, "r") as f:
            for line in f:
                if '=' in line:
                    key, val = line.strip().split('=', 1)
                    values[key.strip()] = val.strip()
        return values

    def save_to_file(self):
        shapes = [str(shape_id) for cb, shape_id in self.shape_checkboxes if cb.isChecked()]
        selected_speeds = [s for s, cb in self.speed_checkboxes.items() if cb.isChecked()]
        template = [opt for opt, cb in self.template_checkboxes.items() if cb.isChecked()]
        if not selected_speeds:
            selected_speeds = ["fast"]  # fallback default

        lines = [
            f"stimuli_duration={self.stimuli_input.text()}",
            f"drawing_duration={self.drawing_input.text()}",
            f"template={','.join(template)}",
            f"shapes={','.join(shapes)}",
            f"speeds={','.join(selected_speeds)}",
            f"show_intro={str(self.intro_checkbox.isChecked()).lower()}"
        ]

        with open(self.SETTINGS_FILE, "w") as f:
            f.write("\n".join(lines))
        print("settings.txt updated.")
        self.accept()
