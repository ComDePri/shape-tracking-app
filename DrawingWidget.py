import time
from PyQt5.QtWidgets import QWidget, QShortcut, QApplication, QLabel, QPushButton
from PyQt5.QtGui import QPainter, QPen, QKeySequence, QColor
from PyQt5.QtCore import Qt, QTimer, QPoint, QPointF, QRect
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
        self.first_shape = True
        self.shape_tuple = self.pop_random_shape()
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

        # timers
        self.drawing_duration = int(settings.get_drawing_duration() * 1000)  # Convert to milliseconds
        self.transition_duration = int(settings.get_transition_duration() * 1000)  # Convert to milliseconds

        self.drawing_timer = QTimer(self)
        self.drawing_timer.setSingleShot(True)
        self.drawing_timer.timeout.connect(self.start_transition)
        self.drawing_timer.setInterval(self.drawing_duration)

        self.transition_timer = QTimer(self)
        self.transition_timer.setSingleShot(True)
        #self.transition_timer.timeout.connect(self.clear_canvas)
        self.transition_timer.timeout.connect(self.start_visual_mask)
        self.transition_timer.setInterval(self.transition_duration)

        # next shape window

        text = """
<div dir="rtl" style="text-align: left; font-size: 18px; margin: 40px;">
    <b>דוגמה לציור שיוצג</b><br><br>

    בתמונה הקרובה תראו דוגמה לצורה: <b>אליפסה</b>.<br>
    תתבקשו לצייר אותה בקצב שמופיע על המסך – כמו <b>"קצב בינוני"</b>.<br><br>

    מטרתכם היא לחזור על הציור <b>בדיוק מירבי</b> ולמשך הזמן שיופיע על המסך.<br>
    אנא התמקדו והשתדלו לדייק ככל שניתן.
</div>
"""

        self.ready_prompt = QLabel(text, self)
        self.ready_prompt.setStyleSheet(f"color: black; font-size: 28px; background: transparent")
        self.ready_prompt.setAlignment(Qt.AlignCenter)
        self.ready_prompt.hide()

        self.ok_button = QPushButton("המשך", self)
        self.ok_button.setStyleSheet("font-size: 18px; padding: 12px;")
        self.ok_button.setFixedSize(200, 50)
        self.ok_button.clicked.connect(self._on_ready_clicked)
        self.ok_button.hide()

        self._position_ready_ui()  # <-- place inside right rectangle

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
        self.corner_template = AnimationWidget(self, scale=2.0, template=True)
        self.corner_template.hide()


        # Start the first drawing session
        QTimer.singleShot(100, self.start_transition)

        # "Saving Data" label
        self.saving_label = QLabel("סיימתם את המטלה. תודה שהשתתפתם!", self)
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

        if self.first_shape:
            choice = ("assets/shape6.svg", "medium", False)
            self.first_shape = False
            self.ready_prompt.setText("נגמר הזמן, לחצו להמשך.")
        else:
            self.shapes.remove(choice)
        return choice[0], choice[1], choice[2]  # Return the SVG file and speed

    def _drawing_rect(self):
        """Right rectangle: 2/3 width & height, vertically centered, with margins and gap."""
        w, h = self.width(), self.height()
        margin = 10
        gap = 10
        rect_h = (2 * h) // 3
        top = (h - rect_h) // 2

        left_rect_width = (w - (2 * margin) - gap) // 3
        right_left = margin + left_rect_width + gap
        right_width = w - 2 * margin - left_rect_width - gap
        return QRect(right_left, top, right_width, rect_h)

    def _paint_setup(self, painter):
        """Place settings/layout only: margins, rectangles, pens, and draw the two frames."""
        w, h = self.width(), self.height()
        margin = 10
        gap = 10
        rect_h = (2 * h) // 3
        top = (h - rect_h) // 2

        # Left (no-draw) rectangle
        left_rect_width = (w - (2 * margin) - gap) // 3
        r_left = QRect(margin, top, left_rect_width, rect_h)

        # Right (draw) rectangle
        r_right = self._drawing_rect()

        # Draw both frames
        pen = QPen(Qt.black, 3, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(r_left)
        painter.drawRect(r_right)

        return r_left, r_right

    from PyQt5.QtGui import QColor

    def _paint_lines(self, painter, clip_rect):
        """Draw only the last N user lines with gradient fading."""
        painter.save()
        painter.setClipRect(clip_rect.adjusted(2, 2, -2, -2))

        tail_len = 30
        lines_to_draw = self.lines[-tail_len:]
        n = len(lines_to_draw)

        for i, line in enumerate(lines_to_draw):
            # Fade from transparent (old) to opaque (new)
            alpha = int(255 * (i + 1) / n) if n > 0 else 255
            base_color = QColor(Qt.black)
            base_color.setAlpha(alpha)

            pen = QPen(base_color, line['width'], Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            pts = line['points']
            if len(pts) >= 2:
                painter.drawLine(pts[0], pts[1])

        painter.restore()

    def _position_ready_ui(self):
        r = self._drawing_rect()  # right 2/3 rectangle
        pad = 12  # small inner padding

        # Prompt: centered near upper third of the right rect
        self.ready_prompt.setGeometry(r.x() + pad,
                                      r.y() + r.height() // 3 - 30,
                                      r.width() - 2 * pad,
                                      60 + 100)

        # Button: centered horizontally, mid-rect vertically
        self.ok_button.move(r.x() + (r.width() - self.ok_button.width()) // 2,
                            r.y() + r.height() // 2 + 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # 1) Setup/layout (frames, pens, etc.)
        _, r_right = self._paint_setup(painter)

        # 2) Draw lines only (inside right rectangle)
        self._paint_lines(painter, r_right)

    def start_drawing(self):
        """Begin a new drawing phase."""
        self.data_handler.clear_buffer()
        self.sampling_timer.start(1)
        self.drawing_timer.start(self.drawing_duration)
        self.play = True
        self.drawing = False

    def start_transition(self):
        """Prompt the user before the next shape is shown."""
        self.play = False
        self.drawing = False
        self.sampling_timer.stop()
        self.clear_canvas()

        self.ready_prompt.show()
        self.ok_button.show()

    def start_visual_mask(self):
        self.example_widget.show_svg("assets/mask.svg", "no animation")
        self.start_drawing()

    def _on_ready_clicked(self):
        self.ready_prompt.hide()
        self.ok_button.hide()

        if not self.shape_tuple[0]:
            self.close_file()
            return

        QTimer.singleShot(self.transition_duration, self._show_example_shape)

    def _show_example_shape(self):
        shape, speed, hide_template = self.shape_tuple
        print(f"Showing shape: {shape}, speed: {speed}, hide_template: {hide_template}")
        self.example_widget.show_svg(shape, speed)

        if hide_template:
            self.corner_template.hide()
        else:
            self.corner_template.show_svg(shape, speed)


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
        self.corner_template.hide()
        self.lines = []
        self.shape_tuple = self.pop_random_shape()
        self.data_handler.start_new_section(f"{self.shape_tuple}")
        self.update()

    def resizeEvent(self, event):
        try:
            super().resizeEvent(event)
            self._position_ready_ui()
        except:
            pass

    def close_file(self):
        self.saving_label.show()  # Display the label
        self.saving_label.repaint()  # Force the label to redraw immediately
        QApplication.processEvents()  # Process any pending GUI events
        time.sleep(3)  # Wait for 1 seconds to show the label
        self.data_handler.close_file()  # Close the file
        QApplication.quit()  # Quit the application