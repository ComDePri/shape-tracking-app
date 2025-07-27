import os
import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from MenuWidget import MenuWidget
from DrawingWidget import DrawingWidget
from DataHandler import DataHandler

FILE_NAME = "_shape_tracking.json"
FOLDER = "results/"


def create_results_folder():
    """
    Creates a folder named 'results' in the current working directory.
    If the folder already exists, it does nothing.
    """
    folder_name = "results"
    try:
        os.makedirs(folder_name, exist_ok=True)
        print(f"Folder '{folder_name}' created successfully or already exists.")
    except Exception as e:
        print(f"An error occurred while creating the folder: {e}")


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.toolbar = None
        self.drawing_widget = None
        self.data_handler = None
        self.setWindowTitle("Drawing Task")
        self.showFullScreen()

        # Stacked Widget to manage multiple screens
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Add the MenuWidget
        self.menu = MenuWidget(self.start_drawing_task)
        self.stack.addWidget(self.menu)


    def start_drawing_task(self, participant_name):
        """Switch to the DrawingWidget."""

        current_time = datetime.now().strftime('%Y%m%d%H%M%S') + "_"
        self.data_handler = DataHandler(participant_name, FOLDER + current_time + participant_name + FILE_NAME)
        self.drawing_widget = DrawingWidget(self.data_handler)

        self.stack.addWidget(self.drawing_widget)
        self.stack.setCurrentWidget(self.drawing_widget)


def main():
    import sys
    import traceback

    def log_uncaught_exceptions(ex_cls, ex, tb):
        text = f"Uncaught exception:\n{''.join(traceback.format_tb(tb))}\n{ex_cls.__name__}: {ex}"
        print(text)

    sys.excepthook = log_uncaught_exceptions
    create_results_folder()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()