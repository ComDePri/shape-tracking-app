from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from settings_singleton import Settings

settings = Settings()


class InstructionsWidget(QWidget):
    finished = pyqtSignal()

    def __init__(self, pages=None, btn_labels=None, parent=None):
        super().__init__(parent)

        # --- Developer-configurable content ---


        num_shapes = len(settings.get_shapes())
        drawing_duration = int(settings.get_drawing_duration())
        speeds = len(settings.get_speeds())
        show_temp = len(settings.get_temp_show_settings())
        total_time = int(drawing_duration * num_shapes * speeds * show_temp / 60)

        he = {"fast": "מהיר", "medium": "בינוני", "slow": "איטי", "comfort": "נוח"}
        lst = [he[s] for s in settings.get_speeds()]
        speed_text = ", ".join(lst[:-1]) + " ו" + lst[-1] if lst else ""

        self.pages = pages or [
            "ברוכים הבאים, לפניכם טופס אישור השתתפות במטלה. לחצו הבא כדי לעבור אליו",f"""
<div dir="rtl" style="text-align: left; font-size: 18px; margin: 40px;">
    <b>🧾 הסכמה להשתתפות במחקר</b><br><br>

    <b>למה אנחנו עושים את המחקר הזה:</b> 
    המחקר בודק כיצד אנשים מציירים צורות בקצבים שונים, כדי להבין תהליכים מוטוריים ותפיסתיים
    .<br><br>

    <b>מה תידרשו לעשות:</b> 
תציירו {num_shapes} צורות בעט דיגיטלי, בקצבים שונים ועם או בלי תבנית מוצגת. כל ציור יימשך כ־{drawing_duration} שניות, והמשימה כולה כ־{total_time} דקות.
    יינתנו הוראות לפני כל שלב, ותוכלו לקחת הפסקות קצרות לאורך הדרך.<br><br>

    <b>הטבות ופיצויים:</b> 
    איננו מצפים להטבות ישירות כתוצאה מהשתתפותכם במחקר זה.<br><br>

    <b>סיכונים אפשריים:</b> 
    ייתכן ותחוו אי־נוחות מסוימת עקב הצורך לשמור על ריכוז לאורך זמן ולעקוב אחר ההוראות. 
    תוכלו לעזוב בכל שלב ללא כל ענישה או אובדן זכויות.<br><br>

    <b>פרטיות:</b> 
    התגובות שלכם יישמרו באופן אנונימי ויאוחסנו בשרת מאובטח בסיסמה. המחקר אינו אוסף מזהים ישירים או עקיפים, 
    למעט מזהה ייחודי אקראי.<br><br>

    <b>משך:</b> 
    כ־{total_time} דקות.<br><br>

    <b>ליצירת קשר:</b> 
    יובל הרט, הפקולטה למדעי החברה, האוניברסיטה העברית בירושלים, 
    <a href="mailto:comdepri@mail.huji.ac.il">comdepri@mail.huji.ac.il</a><br><br>

    בלחיצה על כפתור <b>הבא</b>, אתם מאשרים שקראתם והבנתם את האמור לעיל ומסכימים להשתתף במחקר מרצונכם החופשי.
</div>
""",
            f"""
<div dir="rtl" style="text-align: left; font-size: 18px; margin: 40px;">
    <b>ברוכים הבאים למטלת הציורים!</b><br><br>

    במטלה זו תתבקשו לצייר צורות שיוצגו לכם על המסך, בקצבי ציור שונים: 
    <b>{speed_text}</b>.<br><br>

    כל צורה שתראו – עליכם לצייר בצורה מדויקת ככל האפשר, ולחזור על הציור 
    מספר פעמים עד שיופיע סימון עצירה לאחר <b>{drawing_duration} שניות</b>.<br><br>

    לאחר מכן תוחלף הצורה ותתחיל משימה חדשה. 
    בחלק מהמקרים הצורה תוצג גם במהלך הציור, ובחלק אחר תצטרכו לצייר מהזיכרון בלבד.<br><br>

    <b>מקווים שתהנו – תודה על ההשתתפות!</b>
</div>
"""
        ]

        self.button_labels = btn_labels or {
            "back": "הקודם",
            "next": "הבא",
            "start": "התחל"
        }

        # --- Internal state ---
        self.current_index = 0

        # --- Layout ---
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignCenter)

        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 20px;")
        self.layout().addWidget(self.label)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setDirection(QBoxLayout.RightToLeft)  # ensures buttons flow right-to-left

        self.next_btn = QPushButton(self.button_labels["next"])
        self.back_btn = QPushButton(self.button_labels["back"])

        self.back_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)

        btn_layout.addWidget(self.back_btn)
        btn_layout.addWidget(self.next_btn)
        self.layout().addLayout(btn_layout)

        self.update_ui()

    def update_ui(self):
        self.label.setText(self.pages[self.current_index])
        self.back_btn.setEnabled(self.current_index > 0)

        if self.current_index == len(self.pages) - 1:
            self.next_btn.setText(self.button_labels["start"])
        else:
            self.next_btn.setText(self.button_labels["next"])

    def next_page(self):
        if self.current_index < len(self.pages) - 1:
            self.current_index += 1
            self.update_ui()
        else:
            self.finished.emit()

    def prev_page(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_ui()
