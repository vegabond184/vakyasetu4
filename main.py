from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt6.QtGui import QFont, QColor
import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QComboBox, QFrame, QStackedLayout,
    QGraphicsDropShadowEffect
)
import pygame
import customtkinter as ctk
import vakyakey
import chat
import serial
import time
import pyautogui
import threading
import news
import photos

ACCENT = "#3b82f6"
BG_CARD = "#0f172a"
BG_MAIN = "#020617"

STRINGS = {
    "English": {
        "title": "VakyaSetu",
        "lang_tag": "English",
        "cards": [
            ("🎤", "Talk"),
            ("💬", "Chat"),
            ("📰", "News"),
            ("📖", "Books"),
            ("📷", "Photos")
        ]
    },

    "Hindi": {
        "title": "वाक्यसेतु",
        "lang_tag": "हिंदी",
        "cards": [
            ("🎤", "बात करें"),
            ("💬", "चैट करें"),
            ("📰", "समाचार"),
            ("📖", "किताबें"),
            ("📷", "तस्वीरें")
        ]
    }
}
pygame.mixer.init()
effect = pygame.mixer.Sound("sound.mp3")

class Card(QFrame):
    def __init__(self, icon, text, parent=None):
        super().__init__(parent)

        self.setStyleSheet(f"background:{BG_CARD}; border-radius:24px;")
        # self.setStyleSheet(f"background:#FF0000; border-radius:84px;")

        self.icon = QLabel(icon)
        self.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.text = QLabel(text)
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.addStretch()
        layout.addWidget(self.icon)
        layout.addWidget(self.text)
        layout.addStretch()

    def set_center_style(self):
        self.setStyleSheet(
            f"background:{BG_CARD}; border-radius:24px; width:200px; height:200px;"
        )
        self.icon.setFont(QFont("Segoe UI Emoji", 52))
        self.text.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(80)
        shadow.setColor(QColor(59,130,246,180))
        shadow.setOffset(0,0)
        self.setGraphicsEffect(shadow)

    def set_side_style(self):
        self.setStyleSheet(f"background:{BG_CARD}; border-radius:24px; margin:7px;")
        # self.setStyleSheet(f"width:15px;")
        self.icon.setFont(QFont("Segoe UI Emoji", 32))
        self.text.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.setGraphicsEffect(None)



class choose_lang(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background:{BG_MAIN}; color:white;")
        self.showFullScreen()

    def build_ui(self):
        page = QWidget()
        page.setFixedWidth(200) 
        layout = QVBoxLayout(self)
        # layout.setContentsMargins(40,20,40,40)

        title = QLabel("Select Language / भाषा चुनें")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("margin-top: 250px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lang_combo = QComboBox()
        self.lang_combo.setFixedWidth(200)
        self.lang_combo.setStyleSheet("""
        QComboBox {
            background-color: #1e293b;
            padding: 5px;
            margin-top: 70px;
        }
        
        
        """)
        self.lang_combo.addItems(STRINGS.keys())
        self.lang_combo.setFont(QFont("Segoe UI", 14))

        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0f172a;
                        border-radius: 8px;
                        margin-bottom: 300px;
                    }
                    QPushButton:hover {
                        background-color:rgb(59,130,246);
                    }
                    """)
        self.start_btn.setFixedWidth(200)
        self.start_btn.setFont(QFont("Segoe UI", 14))
        self.start_btn.clicked.connect(self.startboth)

        layout.addWidget(title)
        layout.addWidget(self.lang_combo,alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def start_app(self):
        selected_lang = self.lang_combo.currentText()
        # STRINGS["current"] = STRINGS[selected_lang]

        self.main_window = VakyaSetu(selected_lang)
        self.main_window.show()
        self.close()
    
    def keypress(self):
     
        ser = serial.Serial('COM11', 2400, timeout=1)

        time.sleep(2)  # wait for Arduino reset

        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                sensor1 = data.split(":")[0]
                sensor2 = data.split(":")[1]

                if int(sensor1) > 10000 and int(sensor2) > 10000:
                    print("sensors 3 triggered")
                    pyautogui.press('down')  # Simulate pressing the 'Down Arrow' key

                elif int(sensor1) > 10000:
                    print("Sensor 1 triggered")
                    pyautogui.press('delete')  # Simulate pressing the 'Delete' key
        
                elif int(sensor2) > 10000:
                    print("Sensor 2 triggered")
                    pyautogui.press('enter')  # Simulate pressing the 'Enter' key


    def startboth(self):
      self.serial_thread = threading.Thread(target=self.keypress, daemon=True)
      self.serial_thread.start()
      self.start_app()



    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.close()


class VakyaSetu(QWidget):
    def __init__(self, choose_lang):
        super().__init__()
        self.setStyleSheet(f"background:{BG_MAIN}; color:white;")
        self.showFullScreen()
        self.lang = choose_lang
        self.stack = QStackedLayout(self)
        self.build_main()

    def build_main(self):
        data = STRINGS[self.lang]
        page = QWidget()
        root = QVBoxLayout(page)
        root.setContentsMargins(40,20,40,40)

        header = QHBoxLayout()
        title = QLabel(data["title"])
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))

        header.addWidget(title)
        # header.addStretch()
        header.addWidget(QLabel(data["lang_tag"]))

        root.addLayout(header)

        self.carousel = QWidget()
        root.addWidget(self.carousel, 1)

        self.cards = []
        for icon, text in data["cards"]:
            card = Card(icon, text, self.carousel)
            card.show()
            self.cards.append(card)

        self.current = 0

        self.stack.addWidget(page)
        self.stack.setCurrentWidget(page)

        QTimer.singleShot(0, lambda: self.position_cards(False))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, "cards"):
            self.position_cards(False)

    def get_layout(self):
        w = self.carousel.width()
        h = self.carousel.height()

        center_w = int(w * 0.32)
        center_h = int(h * 0.55)

        side_w = int(center_w * 0.6)
        side_h = int(center_h * 0.6)

        small_w = int(center_w * 0.35)
        small_h = int(center_h * 0.35)

        return [
            QRect(int(w*0.5 - center_w/2), int(h*0.50 - center_h/2), center_w, center_h),
            QRect(int(w*0.75 - side_w/2), int(h*0.55 - side_h/2), side_w, side_h),
            QRect(int(w*0.90 - small_w/2), int(h*0.60 - small_h/2), small_w, small_h),
            QRect(int(w*0.10 - small_w/2), int(h*0.60 - small_h/2), small_w, small_h),
            QRect(int(w*0.25 - side_w/2), int(h*0.55 - side_h/2), side_w, side_h)
        ]

    def position_cards(self, animate=True):
        layout = self.get_layout()

        for i, card in enumerate(self.cards):
            rel = (i - self.current) % len(self.cards)
            target = layout[rel]

            if rel == 0:
                card.set_center_style()
            else:
                card.set_side_style()

            if animate:
                anim = QPropertyAnimation(card, b"geometry")
                anim.setDuration(320)
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                anim.setStartValue(card.geometry())
                anim.setEndValue(target)
                anim.start()
                card.anim = anim
            else:
                card.setGeometry(target)

            card.raise_()

    def keyPressEvent(self, e): #main menue window for selecting functions
        if e.key() == Qt.Key.Key_Delete: # moving right
            effect.play()
            effect.set_volume(0.5)
            self.move(1)

        elif e.key() == Qt.Key.Key_Return: 
            if self.current == 0: #selecting the vakyakey card
                vakyakey.main(self.lang)

            elif self.current == 1: #selecting the chat card
                chat.main(self.lang)
            
            elif self.current == 2:
                news.main()

            elif self.current == 4:
                photos.main()


        elif e.key() == Qt.Key.Key_Escape:
            self.lang_win = choose_lang()
            self.lang_win.build_ui()
            self.lang_win.show()
            self.close()

               

    def move(self, direction):
        self.current = (self.current + direction) % len(self.cards)
        self.position_cards(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # win = VakyaSetu()
    # win.show()
    chooser = choose_lang()
    chooser.build_ui()
    chooser.show()
    sys.exit(app.exec())