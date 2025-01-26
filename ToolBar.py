from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QToolBar, QPushButton, QApplication, QShortcut, QVBoxLayout, QLabel


class Toolbar(QToolBar):
    """Toolbar with actions for the drawing application."""
    def __init__(self, drawing_widget):
        super().__init__()
        self.drawing_widget = drawing_widget

        # Layout for the menu
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # QLabel to display text
        self.label = QLabel("")
        self.label.setStyleSheet("font-size: 18px; color: black;")  # Optional styling
        layout.addWidget(self.label)

        # Clear Button
        clear_button = QPushButton("Next")
        clear_button.clicked.connect(self.drawing_widget.clear_canvas)
        self.addWidget(clear_button)

        # Exit Button
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.exit_application)
        self.addWidget(exit_button)

        # Shortcuts
        self.next_shortcut = QShortcut(QKeySequence("Return"), self)  # Enter key
        self.next_shortcut.activated.connect(clear_button.click)

        self.exit_shortcut = QShortcut(QKeySequence("Escape"), self)  # Escape key
        self.exit_shortcut.activated.connect(exit_button.click)

        # Additional space for future features
        self.addSeparator()

    def exit_application(self):
        """Exit the application."""
        self.label.setStyleSheet("font-size: 18px; color: black;")
        self.label.setText("Saving Data")
        self.drawing_widget.close_file()
        QApplication.quit()

