import time
from PyQt5.QtWidgets import QWidget, QShortcut, QApplication, QLabel
from PyQt5.QtGui import QPainter, QPen, QKeySequence
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF
from PyQt5.QtSvg import QSvgRenderer
from AnimationWidget import AnimationWidget
import random
from settings_singleton import Settings
from DataHandler import DataHandler

NO_DATA = -999
settings = Settings()

class DrawingWidget(QWidget):
    """Widget for the drawing task."""
    def __init__(self, data_handler: DataHandler, show_template=True, scale=1.0):
        super().__init__()
        self.shapes = None
        self.showFullScreen()
        self.drawing = False
        self.play = False
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

        self.drawing_duration = int(settings.get_drawing_duration() * 1000)  # Convert to milliseconds
        self.transition_duration = int(settings.get_stimuli_duration() * 1000)  # Convert to milliseconds

        self.drawing_timer = QTimer(self)
        self.drawing_timer.setSingleShot(True)
        self.drawing_timer.timeout.connect(self.start_transition)
        self.drawing_timer.setInterval(self.drawing_duration)

        self.transition_timer = QTimer(self)
        self.transition_timer.setSingleShot(True)
        #self.transition_timer.timeout.connect(self.clear_canvas)
        self.transition_timer.timeout.connect(self.start_visual_mask)
        self.transition_timer.setInterval(self.transition_duration)

        # Initialize shapes from settings
        self.shapes = settings.get_selected_shapes()

        # Example shape
        self.example_widget = AnimationWidget(self, scale=2.0)
        self.example_widget.hide()
        self.example_widget.done.connect(self.start_drawing)

        # Visual mask
        self.visual_mask = AnimationWidget(self, scale=2.0)
        self.visual_mask.hide()
        self.visual_mask.done.connect(self.start_drawing)

        # Corner template
        corner_scale = settings.get_corner_scale()
        self.corner_template = AnimationWidget(self, scale=corner_scale, corner=True)
        self.corner_template.hide()

        # Start the first drawing session
        QTimer.singleShot(100, self.start_transition)

        # "Saving Data" label
        self.saving_label = QLabel("Saving Data", self)
        self.saving_label.setStyleSheet("color: black; font-size: 48px; font-weight: bold; background-color: white;")
        self.saving_label.setAlignment(Qt.AlignCenter)
        self.saving_label.setGeometry(0, 0, self.width(), self.height())
        self.saving_label.hide()  # Initially hidden

        self.set_settings()

    def set_settings(self):
        """Set the drawing and transition durations."""


    def pop_random_shape(self):
        if not self.shapes:
            return False, False, False  # or raise an exception

        choice = random.choice(list(self.shapes))
        self.shapes.remove(choice)
        return choice[0], choice[1], choice[2]  # Return the SVG file and speed


    def paintEvent(self, event):
        """Renders the lines on the widget."""
        painter = QPainter(self)

        # Draw user and example lines
        for line in self.lines:
            pen = QPen(line['color'], line['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawPolyline(*line['points'])


    def start_drawing(self):
        """Begin a new drawing phase."""
        self.data_handler.clear_buffer()
        self.sampling_timer.start(1)
        self.drawing_timer.start(self.drawing_duration)
        self.play = True
        self.drawing = False

    def start_transition(self):
        """Show the transition message and start the countdown."""
        self.play = False
        self.drawing = False
        self.sampling_timer.stop()
        self.clear_canvas()
        self.transition_timer.start(self.transition_duration)

        shape, speed, hide_template = self.pop_random_shape()
        if shape:
            self.example_widget.show_svg(shape, speed)
            self.corner_template.show_svg(shape, speed, hide_template)
        else:
            self.close_file()

    def start_visual_mask(self):
        self.example_widget.show_svg("assets/mask.svg", "no animation")
        self.start_drawing()


    def mousePressEvent(self, event):
        """Start drawing and sampling when the mouse/pen is pressed."""
        if event.button() == Qt.LeftButton and self.play:
            self.drawing = True
            self.last_point = event.pos()
            self.sampling_timer.start(1)  # Start sampling at 140Hz


    def tabletEvent(self, event):
        """Handle tablet events for capturing pen pressure."""
        if self.play:
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


    def mouseMoveEvent(self, event):
        """Draw line segments as the mouse/pen moves."""
        if self.play:
            current_point = event.pos()

            pressure = self.pen_pressure if self.pen_pressure > 0 else 0.5
            self.posX = current_point.x()
            self.posY = current_point.y()

            line = {
                'color': Qt.black,
                'width': 2 * pressure,
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

        if self.drawing:
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