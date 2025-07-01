from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import QTimer, Qt, QTime, Signal, Slot
from PySide6.QtGui import QFont, QColor, QPainter, QPen
import sys
import random
import math
import time

class FluidWaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0.0
        self.active = False
        self.setMinimumHeight(90)
        self.setMaximumHeight(130)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def set_active(self, active=True):
        self.active = active

    def animate(self):
        if self.active:
            self.phase += 0.11
        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        steps = 48
        path = []
        for i in range(steps + 1):
            x = int(i * width / steps)
            t = self.phase + i * 0.22
            base = math.sin(t)
            mod = math.sin(self.phase/2 + i*0.11)
            amp = 34 if self.active else 7
            y = int(height/2 + amp * base + amp*0.25*mod)
            if self.active:
                y += int(7 * random.uniform(-1, 1))
            path.append((x, y))
        pen = QPen(QColor(178, 0, 255, 230), 5)
        qp.setPen(pen)
        prev = None
        for pt in path:
            if prev is not None:
                qp.drawLine(prev[0], prev[1], pt[0], pt[1])
            prev = pt
        pen = QPen(QColor(237, 231, 250, 64), 2)
        qp.setPen(pen)
        qp.drawEllipse(4, 4, width-8, height-8)

class RoboticFaceWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(130, 130)
        self.speaking = False
        self.phase = 0.0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(60)

    def set_speaking(self, speaking=True):
        self.speaking = speaking

    def animate(self):
        self.phase += 0.13
        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        center = w // 2, h // 2
        qp.setPen(QPen(QColor("#ede7fa"), 3))
        qp.setBrush(QColor("#fff"))
        qp.drawEllipse(center[0]-60, center[1]-60, 120, 120)
        qp.setPen(QPen(QColor("#b200ff"), 2))
        qp.setBrush(Qt.NoBrush)
        qp.drawEllipse(center[0]-48, center[1]-52, 96, 104)
        eye_color = QColor(178,0,255,180)
        qp.setBrush(eye_color)
        qp.setPen(Qt.NoPen)
        y_vari = 0
        if self.speaking:
            y_vari = int(5 * abs(math.sin(self.phase*1.5)))
        qp.drawEllipse(center[0]-27, center[1]-5-y_vari, 18, 18+2*y_vari)
        qp.drawEllipse(center[0]+9, center[1]-5-y_vari, 18, 18+2*y_vari)
        qp.setBrush(QColor(178,0,255,90))
        height_mouth = 7 + (9 if self.speaking and math.sin(self.phase*2)>0 else 0)
        qp.drawRoundedRect(center[0]-20, center[1]+32, 40, height_mouth, 8, 8)
        qp.setBrush(Qt.NoBrush)
        qp.setPen(QPen(QColor("#b200ff"), 1))
        qp.drawEllipse(center[0]-54, center[1]-54, 108, 108)

class WilliamGUI(QMainWindow):
    toggle_listen = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WILLIAM - Assistant IA")
        self.setMinimumSize(1100, 700)
        self.setStyleSheet("""
            background-color: #fff;
            color: #2d175c;
        """)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)
        self.layout.setSpacing(18)

        # --- Header stylisé ---
        header = QHBoxLayout()
        self.name_label = QLabel("⧫ WILLIAM ⧫")
        font = QFont("Segoe UI", 40, QFont.Bold)
        self.name_label.setFont(font)
        self.name_label.setStyleSheet(
            "color: #b200ff; letter-spacing: 0.12em; background: transparent; font-family: 'Segoe UI', 'Roboto', Arial, sans-serif; padding-top: 12px; padding-bottom: 10px;"
        )
        header.addWidget(self.name_label)
        header.addStretch()
        self.timestamp = QLabel("")
        self.timestamp.setFont(QFont("Consolas", 16))
        self.timestamp.setStyleSheet("color: #bdb7e4;")
        header.addWidget(self.timestamp)
        self.layout.addLayout(header)

        # --- Visage robotique stylisé ---
        self.face = RoboticFaceWidget()
        self.layout.addWidget(self.face, alignment=Qt.AlignHCenter)

        # --- Oscillateur fluide ---
        self.wave = FluidWaveformWidget()
        self.layout.addWidget(self.wave)

        # --- Generated Text (log window, overlay style) ---
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Segoe UI", 16))
        self.output_text.setStyleSheet("""
            background: #fff;
            border: 2px solid #ede7fa;
            border-radius: 22px;
            color: #2d175c;
            padding: 16px;
            box-shadow: 0 4px 34px #ede7fa;
            margin-top: 8px;
        """)
        self.layout.addWidget(self.output_text, 2)

        # --- Listen State and Controls (status strip modernisé) ---
        controls = QHBoxLayout()
        self.listen_label = QLabel("Écoute : INACTIVE")
        self.listen_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.listen_label.setStyleSheet("color: #b200ff; font-weight: bold;")
        controls.addWidget(self.listen_label)

        controls.addStretch()
        self.diagnostic_label = QLabel("Diagnostic : ⏳")
        self.diagnostic_label.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.diagnostic_label.setStyleSheet("color: #ffd700; font-weight: bold;")
        controls.addWidget(self.diagnostic_label)

        self.toggle_btn = QPushButton("🎤 ON")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(y1:0, y2:1, stop:0 #ede7fa, stop:1 #fff);
                color: #b200ff;
                font-weight: bold;
                border-radius: 18px;
                border: 2px solid #b200ff;
                padding: 12px 40px;
                margin-right: 8px;
                font-size: 21px;
            }
            QPushButton:checked {
                background: #b200ff;
                color: #fff;
                border: 2px solid #b200ff;
            }
        """)
        self.toggle_btn.clicked.connect(self._toggle_listen)
        controls.addWidget(self.toggle_btn)

        self.layout.addLayout(controls)

        # --- Timer for UI updates ---
        self.listening = False
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self.update_ui)
        self._update_timer.start(750)
        self.current_diag_state = "⏳"

    @Slot()
    def _toggle_listen(self):
        self.listening = not self.listening
        self.listen_label.setText(f"Écoute : {'ACTIVE' if self.listening else 'INACTIVE'}")
        self.wave.set_active(self.listening)
        self.face.set_speaking(self.listening)
        self.toggle_btn.setText("🎤 ON" if self.listening else "🎤 OFF")
        self.toggle_listen.emit(self.listening)

    def append_text(self, text, color="#2d175c"):
        self.output_text.append(f'<span style="color:{color}">{text}</span>')

    def show_live_transcription(self, text, color="#b200ff"):
        self.output_text.append(f'<span style="color:{color}">{text}</span>')

    def set_diagnostic(self, state):
        color = "#36e636" if state == "✅" else ("#ff5555" if state == "❌" else "#ffd700")
        self.diagnostic_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.diagnostic_label.setText(f"Diagnostic : {state}")
        self.current_diag_state = state

    def update_ui(self):
        self.timestamp.setText(QTime.currentTime().toString("HH:mm:ss"))
        if self.current_diag_state == "⏳" and int(time.time()*2)%2 == 0:
            self.diagnostic_label.setVisible(False)
        else:
            self.diagnostic_label.setVisible(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WilliamGUI()
    win.show()
    win.append_text("Bienvenue dans WILLIAM, assistant IA vocal évolutif !", "#b200ff")
    win.set_diagnostic("✅")
    sys.exit(app.exec())