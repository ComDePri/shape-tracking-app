from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QApplication, QShortcut


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
        self.name_input.setPlaceholderText("Enter your name...")
        self.name_input.setFixedSize(300, 50)  # Set button size (width: 150px, height: 50px)
        self.name_input.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.name_input)

        # Start Button
        start_button = QPushButton("Start")
        start_button.setStyleSheet("font-size: 16px; padding: 10px;")
        start_button.setFixedSize(300, 50)  # Set button size (width: 150px, height: 50px)
        start_button.clicked.connect(self.start_task)
        layout.addWidget(start_button)

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

    def start_task(self):
        """Start the drawing task and pass the participant name."""
        self.participant_name = self.name_input.text().strip()
        if self.participant_name:  # Ensure a name is provided
            self.switch_to_drawing(self.participant_name)
        else:
            # Highlight the input field if empty
            self.name_input.setStyleSheet("border: 2px solid red; font-size: 16px;")

    def exit_application(self):
        """Exit the application."""
        self.close()
        QApplication.quit()
