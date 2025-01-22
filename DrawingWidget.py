import time
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QCursor
from PyQt5.QtCore import Qt, QTimer, QPoint
from DataHandler import DataHandler

class DrawingWidget(QWidget):
    """Widget for the drawing task."""
    def __init__(self, data_handler: DataHandler):
        super().__init__()
        self.setFixedSize(800, 600)
        self.drawing = False
        self.last_point = QPoint()
        self.pen_pressure = 1.0
        self.lines = []

        # Timer for sampling cursor positions
        self.sampling_timer = QTimer(self)
        self.sampling_timer.timeout.connect(self.sample_cursor_position)

        #start data handler
        self.data_handler = data_handler
        self.data_handler.start_new_section("", True)

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
            self.sampling_timer.start(1000 // 140)  # Start sampling at 140Hz

    def mouseMoveEvent(self, event):
        """Draw line segments as the mouse/pen moves."""
        if self.drawing:
            pressure = event.pressure() if hasattr(event, 'pressure') else 1.0
            self.pen_pressure = pressure
            current_point = event.pos()
            line = {
                'color': Qt.black,
                'width': 2 * self.pen_pressure,
                'points': [self.last_point, current_point]
            }
            self.lines.append(line)
            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event):
        """Stop drawing and sampling when the mouse/pen is released."""
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.sampling_timer.stop()  # Stop sampling when drawing ends

    def sample_cursor_position(self):
        """Sample the cursor position and store it."""
        cursor_pos = self.mapFromGlobal(QCursor.pos())  # Map global to local widget coordinates
        timestamp = time.time()
        self.data_handler.write_data({"X":cursor_pos.x(), "Y":cursor_pos.y(), "Timestamp":timestamp})

    def clear_canvas(self):
        """Clear the canvas and reset sampling data."""
        self.lines = []
        self.data_handler.start_new_section("")
        self.update()

    def close_file(self):
        self.data_handler.close_file()