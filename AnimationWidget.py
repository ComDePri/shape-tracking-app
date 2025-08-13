import re
import xml.etree.ElementTree as ET
from PyQt5.QtCore import Qt, QTimer, QPointF, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QPainterPath
from PyQt5.QtWidgets import QWidget, QLabel
from svgpathtools import parse_path


class AnimationWidget(QWidget):
    done = pyqtSignal()

    def __init__(self, parent=None, scale: float = 1.0, template: bool = False):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("background: transparent;")
        self.setGeometry(0, 0, parent.width(), parent.height())

        self.flip_x = True
        self.svg_size = (200, 240)
        self.scale = scale
        self.template = template

        if template:
            self.top_left = QPointF(310, 500)
        else:
            self.top_left = QPointF(1250, 500)

        self.label_top = QLabel(self)
        self.label_top.setStyleSheet(f"color: black; font-size: 28px; background: transparent")
        self.label_top.setAlignment(Qt.AlignCenter)

        #self.label_bottom = QLabel(self)
        # for lbl, size in [(self.label_top, 32), (self.label_bottom, 28)]:
        #     lbl.setAlignment(Qt.AlignCenter)
        #     lbl.setStyleSheet(f"color: black; font-size: {size}px; background: transparent")

        self.animated_path = QPainterPath()
        self.animated_points = []
        self.animated_index = 0

        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._advance_animation)
        self.hold_timer = QTimer(self)
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self._end_presentation)


    def show_svg(self, filepath: str, speed: str, hide: bool = False):

        if hide:
            self.clear()
            return

        speed_map = {
            "fast": (700, 4200, "בקצב מהיר"),
            "medium": (1400, 3500, "בקצב בינוני"),
            "comfort": (1400, 3500, "בקצב נוח"),
            "slow": (2100, 2800, "בקצב איטי")
        }
        animation_ms, pause_ms, label = speed_map.get(speed, (0, 100, ""))
        top_label = f"אנא צייר את הצורה הבאה {label}" if label else ""

        self.label_top.setText("" if self.template else top_label)
        #self.label_bottom.setText("" if self.template else label)
        pause_ms = 120000 if self.template else pause_ms
        reposition = True

        self._show_svg(filepath, animation_ms, pause_ms, self.scale, reposition)

    def _show_svg(self, filepath: str, animation_ms: int, pause_ms: int, scale: float, reposition: bool):
        self._load_svg_path(filepath, self.top_left, scale, reposition)
        if not self.animated_points:
            print("No path points loaded.")
            return

        self.animated_index = 0
        self.animated_path = QPainterPath(self.animated_points[0])

        for pt in self.animated_points[1:]:
            self.animated_path.lineTo(pt)

        # if animation_ms > 0:
        #     self.anim_timer.start(int(animation_ms / len(self.animated_points)))
        # else:
        #     for pt in self.animated_points[1:]:
        #         self.animated_path.lineTo(pt)

        self.hold_timer.start(animation_ms + pause_ms)
        self._update_label_positions()
        self.label_top.show()
        #self.label_bottom.show()
        self.show()
        self.update()

    def _load_svg_path(self, filepath: str, top_left: QPointF, scale: float, reposition: bool = True):
        try:
            root = ET.parse(filepath).getroot()

            # Optional: extract viewBox size
            if "viewBox" in root.attrib:
                _, _, w, h = map(float, root.attrib["viewBox"].split())
                self.svg_size = (w, h)

            # Defaults
            sx, sy = 1.0, 1.0  # scale factors from SVG <g>
            tx, ty = 0.0, 0.0  # translation offsets

            # Look for first <g> with a transform attribute
            for el in root.iter():
                if el.tag.endswith('g') and 'transform' in el.attrib:
                    transform = el.attrib['transform']

                    # Parse scale(x[,y])
                    match = re.search(r"scale\(([^)]+)\)", transform)
                    if match:
                        parts = list(map(float, re.split(r"[ ,]+", match.group(1).strip())))
                        if len(parts) == 1:
                            sx = sy = parts[0]
                        elif len(parts) >= 2:
                            sx, sy = parts[0], parts[1]

                    # Parse translate(x[,y])
                    match = re.search(r"translate\(([^)]+)\)", transform)
                    if match and reposition:
                        parts = list(map(float, re.split(r"[ ,]+", match.group(1).strip())))
                        if len(parts) == 1:
                            tx, ty = parts[0], 0.0
                        elif len(parts) >= 2:
                            tx, ty = parts[0], parts[1]

                    break  # only first <g> matters

            # Find the first <path> with a 'd' attribute
            path_element = next(
                (el for el in root.iter() if el.tag.endswith('path') and 'd' in el.attrib),
                None
            )
            if path_element is None:
                print("No <path> found in SVG.")
                return

            d = path_element.attrib['d']
            path = parse_path(d)
            num_points = max(int(path.length() / 2), 2)

            flip = -1 if self.flip_x else 1
            self.animated_points = [
                QPointF(
                    flip * path.point(i / num_points).real * sx * scale + tx + top_left.x(),
                    path.point(i / num_points).imag * sy * scale + ty + top_left.y()
                )
                for i in range(num_points)
            ]

        except Exception as e:
            print(f"Error loading SVG: {e}")
            self.animated_points = []

    def _advance_animation(self):

        self.anim_timer.stop()

        # if self.animated_index < len(self.animated_points):
        #     self.animated_path.lineTo(self.animated_points[self.animated_index])
        #     self.animated_index += 1
        #     self.update()
        # else:
        #     self.anim_timer.stop()

    def paintEvent(self, event):
        if not self.animated_path.isEmpty():
            painter = QPainter(self)

            if self.template:
                painter.setPen(QPen(Qt.blue, 3))
            else:
                painter.setPen(QPen(Qt.black, 3))

            painter.drawPath(self.animated_path)

    def _update_label_positions(self):
        width = self.width()
        height = self.height()

        right_third_x = int(width * 2 / 3)
        third_width = int(width / 3)

        center_y = self.top_left.y() + self.svg_size[1] * self.scale / 2

        self.label_top.setGeometry(right_third_x, int(center_y - 470), third_width, 50)
        #self.label_bottom.setGeometry(right_third_x, int(center_y + 20), third_width, 50)

    def _end_presentation(self):
        self.label_top.hide()
        #self.label_bottom.hide()
        self.done.emit()
        self.hide()

    def clear(self):
        self.anim_timer.stop()
        self.hold_timer.stop()
        self.animated_path = QPainterPath()
        self.animated_points.clear()
        self.label_top.hide()
        #self.label_bottom.hide()
        self.update()
        self.hide()
