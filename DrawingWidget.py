import time
from PyQt5.QtWidgets import QWidget, QShortcut, QApplication, QLabel
from PyQt5.QtGui import QPainter, QPen, QCursor, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QPoint
from DataHandler import DataHandler

NO_DATA = -99999

class DrawingWidget(QWidget):
    """Widget for the drawing task."""
    def __init__(self, data_handler: DataHandler):
        super().__init__()
        self.showFullScreen()
        self.drawing = False
        self.last_point = QPoint()
        self.lines = []

        #mesures
        self.posX = NO_DATA
        self.posY = NO_DATA
        self.pen_tiltX = NO_DATA
        self.pen_tiltY = NO_DATA
        self.pen_pressure = NO_DATA
        self.time_stamp = NO_DATA

        # Timer for sampling cursor positions
        self.sampling_timer = QTimer(self)
        self.sampling_timer.timeout.connect(self.sample_cursor_position)

        #start data handler
        self.data_handler = data_handler
        self.data_handler.start_new_section("", True)

        # Shortcuts
        self.next_shortcut = QShortcut(QKeySequence("Return"), self)  # Enter key
        self.next_shortcut.activated.connect(self.clear_canvas)

        self.exit_shortcut = QShortcut(QKeySequence("Escape"), self)  # Escape key
        self.exit_shortcut.activated.connect(self.close_file)

        # "Saving Data" label
        self.saving_label = QLabel("Saving Data", self)
        self.saving_label.setStyleSheet("color: black; font-size: 48px; font-weight: bold; background-color: white;")
        self.saving_label.setAlignment(Qt.AlignCenter)
        self.saving_label.setGeometry(0, 0, self.width(), self.height())
        self.saving_label.hide()  # Initially hidden

    def paintEvent(self, event):
        """Renders the lines on the widget."""
        painter = QPainter(self)
        for line in self.lines:
            pen = QPen(line['color'], line['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawPolyline(*line['points'])

    def mousePressEvent(self, event):
        """Start drawing and sampling when the mouse/pen is pressed."""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()
            self.sampling_timer.start(1)  # Start sampling at 140Hz

    def tabletEvent(self, event):
        """Handle tablet events for capturing pen pressure."""
        if self.drawing:
            self.pen_pressure = event.pressure()
            self.pen_tiltX = event.xTilt()
            self.pen_tiltY = event.yTilt()
            self.posX = event.pos().x()
            self.posY = event.pos().y()

            current_point = event.pos()
            line = {
                'color': Qt.black,
                'width': 4 * self.pen_pressure,
                'points': [self.last_point, current_point]
            }

            self.lines.append(line)
            self.last_point = current_point
            self.update()

    # def mouseMoveEvent(self, event):
    #     """Draw line segments as the mouse/pen moves."""
    #     if self.drawing:
    #         current_point = event.pos()
    #         line = {
    #             'color': Qt.black,
    #             'width': 2 * self.pen_pressure,
    #             'points': [self.last_point, current_point]
    #         }
    #
    #         self.lines.append(line)
    #         self.last_point = current_point
    #         self.update()

    def mouseReleaseEvent(self, event):
        """Stop drawing and sampling when the mouse/pen is released."""
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.sampling_timer.stop()  # Stop sampling when drawing ends

    def sample_cursor_position(self):
        """Sample the cursor position and store it."""

        timestamp = time.time()
        self.data_handler.write_data({"posX": self.posX,
                                      "posY": self.posY,
                                      "tiltX": self.pen_tiltX,
                                      "tiltY": self.pen_tiltY,
                                      "pressure": self.pen_pressure,
                                      "Timestamp":timestamp
                                      })

    def clear_canvas(self):
        """Clear the canvas and reset sampling data."""
        self.lines = []
        self.data_handler.start_new_section("")
        self.update()

    def close_file(self):
        self.saving_label.show()  # Display the label
        self.saving_label.repaint()  # Force the label to redraw immediately
        QApplication.processEvents()  # Process any pending GUI events
        time.sleep(1)  # Wait for 1 seconds to show the label
        self.data_handler.close_file()  # Close the file
        QApplication.quit()  # Quit the application