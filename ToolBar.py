from PyQt5.QtWidgets import QToolBar, QPushButton, QApplication


class Toolbar(QToolBar):
    """Toolbar with actions for the drawing application."""
    def __init__(self, drawing_widget):
        super().__init__()
        self.drawing_widget = drawing_widget

        # Clear Button
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.drawing_widget.clear_canvas)
        self.addWidget(clear_button)

        # Exit Button
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.exit_application)
        self.addWidget(exit_button)

        # Additional space for future features
        self.addSeparator()

    def exit_application(self):
        """Exit the application."""
        self.drawing_widget.close_file()
        QApplication.quit()

