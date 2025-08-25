from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QApplication, QShortcut
from PyQt5.QtWidgets import QPushButton
from SettingsWindow import SettingsWindow
from settings_singleton import Settings

settings = Settings()

class MenuWidget(QWidget):
    """Menu interface for starting the drawing task."""
    def __init__(self, switch_to_drawing):
        super().__init__()
        self.switch_to_drawing = switch_to_drawing
        self.participant_name = ""

        # Layout for the menu
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # Headline
        headline = QLabel("Drawing Task")
        headline.setAlignment(Qt.AlignCenter)
        headline.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(headline)

        # Participant Name Input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter ID...")
        self.name_input.setFixedSize(300, 50)  # Set button size (width: 150px, height: 50px)
        self.name_input.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.name_input)

        # Start Button
        start_button = QPushButton("Start")
        start_button.setStyleSheet("font-size: 16px; padding: 10px;")
        start_button.setFixedSize(300, 50)  # Set button size (width: 150px, height: 50px)
        start_button.clicked.connect(self.start_task)
        layout.addWidget(start_button)

        # Settings Button
        self.settings_button = QPushButton("⚙ Settings")
        self.settings_button.setStyleSheet("font-size: 16px; padding: 10px;")
        self.settings_button.setFixedSize(300, 50)
        self.settings_button.clicked.connect(self.open_settings_window)
        self.settings_window = SettingsWindow(self)  # initialize once
        layout.addWidget(self.settings_button)

        # Exit Button
        exit_button = QPushButton("Exit")
        exit_button.setStyleSheet("font-size: 16px; padding: 10px;")
        exit_button.setFixedSize(300, 50)  # Set button size (width: 150px, height: 50px)
        exit_button.clicked.connect(self.exit_application)
        layout.addWidget(exit_button)

        # Shortcuts
        self.next_shortcut = QShortcut(QKeySequence("Return"), self)  # Enter key
        self.next_shortcut.activated.connect(start_button.click)

        self.exit_shortcut = QShortcut(QKeySequence("Escape"), self)  # Escape key
        self.exit_shortcut.activated.connect(exit_button.click)

        self.setLayout(layout)

    # MenuWidget.py — inside class SettingsWindow(QDialog):
    def start_task(self):
        """Start the drawing task and pass the participant name."""
        # Fullscreen the top-level window (QMainWindow), not the stacked widget
        win = self.window()
        if settings.get_full_screen():
            win.showFullScreen()
        else:
            win.showNormal()
        win.raise_()
        win.activateWindow()

        self.participant_name = self.name_input.text().strip()
        if self.participant_name:
            self.switch_to_drawing(self.participant_name)
        else:
            self.name_input.setStyleSheet("border: 2px solid red; font-size: 16px;")

    def open_settings_window(self):
        if self.settings_window.exec_():
            settings.load_from_file()

    def exit_application(self):
        """Exit the application."""
        self.close()
        QApplication.quit()
