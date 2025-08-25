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
        self.drawing_duration = 40.0
        self.corner_location = [0, 0]
        self.corner_scale = 1.0
        self.shapes = list(range(1, 10))
        self.speeds = ["fast", "medium", "slow", "comfort"]
        self.templates = [True, False]  # Show Template, Hide Template
        self.show_intro = True
        # --- NEW: fullscreen option (for a checkbox in UI) ---
        self.full_screen = False
        # -----------------------------------------------------
        self.update_selected_shapes()

    def update_selected_shapes(self):
        self.selected_shapes = [
            (f"assets/shape{i}.svg", speed, template)
            for i in self.shapes
            for speed in self.speeds
            for template in self.templates
        ]

    def _to_bool(self, v):
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            return v.strip().lower() in {"1", "true", "yes", "y", "on"}
        return False

    def set(self, stimuli_duration=None, drawing_duration=None,
            corner_location=None, corner_scale=None,
            shapes=None, speeds=None, templates=None,
            # --- NEW: setter input for fullscreen ---
            full_screen=None,
            # ---------------------------------------
            save=True):
        if stimuli_duration is not None:
            self.stimuli_duration = float(stimuli_duration)
        if drawing_duration is not None:
            self.drawing_duration = float(drawing_duration)
        # if corner_location is not None:
        #     self.corner_location = corner_location
        # if corner_scale is not None:
        #     self.corner_scale = float(corner_scale)
        if templates is not None:
            self.templates = templates
        if shapes is not None:
            self.shapes = shapes
        if speeds is not None:
            self.speeds = speeds
        # --- NEW: apply fullscreen flag ---
        if full_screen is not None:
            self.full_screen = self._to_bool(full_screen)
        # ----------------------------------

        self.update_selected_shapes()
        if save:
            self.save_to_file()

    # --- NEW: persist settings to settings.txt including full_screen ---
    def save_to_file(self):
        try:
            with open(self.SETTINGS_FILE, "w", encoding="utf-8") as f:
                f.write(f"stimuli_duration={self.stimuli_duration}\n")
                f.write(f"drawing_duration={self.drawing_duration}\n")
                f.write(f"corner_location={self.corner_location[0]},{self.corner_location[1]}\n")
                f.write(f"corner_scale={self.corner_scale}\n")
                f.write("shapes=" + ",".join(str(s) for s in self.shapes) + "\n")
                f.write("speeds=" + ",".join(self.speeds) + "\n")
                # Preserve existing 'template' line semantics
                # We encode to the same textual representation the loader expects.
                # "Show Template" appears when templates[0] is False (see loader logic)
                # "Hide Template" appears when templates[1] is True
                template_tokens = []
                # Mirror existing (somewhat unusual) parsing logic:
                # saved_templates = ["Show Template" not in saved_templates, "Hide Template" in saved_templates]
                # To round-trip with minimal disruption, we emit tokens that re-create current flags:
                if not self.templates[0]:
                    template_tokens.append("Show Template")
                if self.templates[1]:
                    template_tokens.append("Hide Template")
                f.write("template=" + ",".join(template_tokens) + "\n")
                f.write(f"show_intro={'true' if self.show_intro else 'false'}\n")
                # --- NEW line for fullscreen ---
                f.write(f"full_screen={'true' if self.full_screen else 'false'}\n")
                # --------------------------------
            print("Saved settings to file.")
        except Exception as e:
            print(f"Error writing settings.txt: {e}")

    def load_from_file(self):
        if not os.path.exists(self.SETTINGS_FILE):
            print("⚠ settings.txt not found. Using defaults.")
            return

        try:
            with open(self.SETTINGS_FILE, 'r', encoding="utf-8") as f:
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
                    elif key == "template":
                        saved_templates = [t.strip() for t in val.split(',') if t.strip()]
                        saved_templates = [
                            "Show Template" not in saved_templates,
                            "Hide Template" in saved_templates
                        ]
                        self.templates = list(set(saved_templates))
                    elif key == "show_intro":
                        self.show_intro = val.lower() == "true"
                    # --- NEW: read fullscreen flag ---
                    elif key == "full_screen":
                        self.full_screen = val.lower() == "true"
                    # --------------------------------

            self.update_selected_shapes()
            print("Loaded settings from file.")
        except Exception as e:
            print(f"Error reading settings.txt: {e}")

    # --- Getters (optional) ---
    def get_transition_duration(self):
        return self.stimuli_duration

    def get_drawing_duration(self):
        return self.drawing_duration

    def get_corner_location(self):
        return self.corner_location

    def get_corner_scale(self):
        return self.corner_scale

    def get_temp_show_settings(self):
        return self.templates

    def get_shapes(self):
        return self.shapes

    def get_speeds(self):
        return self.speeds

    def get_selected_shapes(self):
        return self.selected_shapes

    def get_show_intro(self):
        return self.show_intro

    # --- NEW: getter for fullscreen ---
    def get_full_screen(self):
        return self.full_screen
