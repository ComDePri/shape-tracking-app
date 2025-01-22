import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget
)
from PyQt5.QtCore import Qt
from MenuWidget import MenuWidget
from ToolBar import Toolbar
from DrawingWidget import DrawingWidget
from DataHandler import DataHandler

FILE_NAME = "shape-dependent-tracking-"

class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.toolbar = None
        self.drawing_widget = None
        self.data_handler = None
        self.setWindowTitle("Drawing Task")
        self.setFixedSize(800, 600)

        # Stacked Widget to manage multiple screens
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Add the MenuWidget
        self.menu = MenuWidget(self.start_drawing_task)
        self.stack.addWidget(self.menu)


    def start_drawing_task(self, participant_name):
        """Switch to the DrawingWidget."""
        self.data_handler = DataHandler(participant_name, FILE_NAME + participant_name + ".json")
        self.drawing_widget = DrawingWidget(self.data_handler)

        # Create a toolbar for the drawing widget
        self.toolbar = Toolbar(self.drawing_widget)
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)

        self.stack.addWidget(self.drawing_widget)
        self.stack.setCurrentWidget(self.drawing_widget)



def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()