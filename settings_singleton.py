# settings_singleton.py

import os

class Settings:
    _instance = None
    _initialized = False
    SETTINGS_FILE = "settings.txt"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.reset()
            self.load_from_file()

    def reset(self):
        self.stimuli_duration = 5.0
        self.drawing_duration = 5.0
        self.corner_location = [0, 0]
        self.corner_scale = 1.0
        self.shapes = list(range(1, 10))
        self.speeds = ["fast", "medium", "slow", "comfort"]
        self.update_selected_shapes()

    def update_selected_shapes(self):
        self.selected_shapes = [
            (f"assets/shape{i}.svg", speed, template)
            for i in self.shapes
            for speed in self.speeds
            for template in (False, True)
        ]

    def set(self, stimuli_duration=None, drawing_duration=None,
            corner_location=None, corner_scale=None,
            shapes=None, speeds=None):
        if stimuli_duration is not None:
            self.stimuli_duration = float(stimuli_duration)
        if drawing_duration is not None:
            self.drawing_duration = float(drawing_duration)
        if corner_location is not None:
            self.corner_location = corner_location
        if corner_scale is not None:
            self.corner_scale = float(corner_scale)
        if shapes is not None:
            self.shapes = shapes
        if speeds is not None:
            self.speeds = speeds

        self.update_selected_shapes()

    def load_from_file(self):
        if not os.path.exists(self.SETTINGS_FILE):
            print("⚠ settings.txt not found. Using defaults.")
            return

        try:
            with open(self.SETTINGS_FILE, 'r') as f:
                for line in f:
                    if '=' not in line:
                        continue
                    key, val = line.strip().split('=', 1)
                    key = key.strip()
                    val = val.strip()

                    if key == "stimuli_duration":
                        self.stimuli_duration = float(val)
                    elif key == "drawing_duration":
                        self.drawing_duration = float(val)
                    elif key == "corner_location":
                        parts = val.split(',')
                        self.corner_location = [int(parts[0]), int(parts[1])]
                    elif key == "corner_scale":
                        self.corner_scale = float(val)
                    elif key == "shapes":
                        self.shapes = [int(s.strip()) for s in val.split(',') if s.strip().isdigit()]
                    elif key == "speeds":
                        self.speeds = [s.strip() for s in val.split(',') if s.strip()]
            self.update_selected_shapes()
            print("Loaded settings from file.")
        except Exception as e:
            print(f"Error reading settings.txt: {e}")

    # --- Getters (optional) ---
    def get_stimuli_duration(self):
        return self.stimuli_duration

    def get_drawing_duration(self):
        return self.drawing_duration

    def get_corner_location(self):
        return self.corner_location

    def get_corner_scale(self):
        return self.corner_scale

    def get_shapes(self):
        return self.shapes

    def get_speeds(self):
        return self.speeds

    def get_selected_shapes(self):
        return self.selected_shapes
