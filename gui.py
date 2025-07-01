from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import QTimer, Qt, QTime, Signal, Slot
from PySide6.QtGui import QFont, QColor, QPainter, QPen
import sys
import random
import time

class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wave_data = [0]*32
        self.active = False
        self.setMinimumHeight(50)
        self.setMaximumHeight(100)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def set_active(self, active=True):
        self.active = active

    def animate(self):
        if self.active:
            self.wave_data = [
                random.randint(10, 40) for _ in self.wave_data
            ]
        else:
            self.wave_data = [15]*len(self.wave_data)
        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        bar_width = self.width() / len(self.wave_data)
        color = QColor(180, 0, 255)
        pen = QPen(color, 2)
        qp.setPen(pen)
        for i, val in enumerate(self.wave_data):
            x = int(i * bar_width)
            y = int(self.height() / 2)
            qp.drawLine(
                x, y - val,
                x, y + val
            )

class WilliamGUI(QMainWindow):
    toggle_listen = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("WILLIAM - Assistant IA")
        self.setMinimumSize(800, 500)
        self.setStyleSheet("""
            background-color: #1a0023;
            color: #e0d0ff;
        """)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QVBoxLayout(self.central)

        # --- Header ---
        header = QHBoxLayout()
        self.name_label = QLabel("⧫ WILLIAM ⧫")
        font = QFont("Orbitron", 32, QFont.Bold)
        self.name_label.setFont(font)
        self.name_label.setStyleSheet("color: #b200ff; letter-spacing: 0.2em;")
        header.addWidget(self.name_label)
        header.addStretch()

        self.timestamp = QLabel("")
        self.timestamp.setFont(QFont("Consolas", 14))
        self.timestamp.setStyleSheet("color: #ccc;")
        header.addWidget(self.timestamp)
        self.layout.addLayout(header)

        # --- Waveform ---
        self.wave = WaveformWidget()
        self.layout.addWidget(self.wave)

        # --- Generated Text ---
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Fira Mono", 14))
        self.output_text.setStyleSheet("""
            background: #2a0040; border: 2px solid #b200ff; border-radius: 9px;
            color: #fff; padding: 8px;
        """)
        self.layout.addWidget(self.output_text, 2)

        # --- Listen State and Controls ---
        controls = QHBoxLayout()
        self.listen_label = QLabel("Écoute : INACTIVE")
        self.listen_label.setFont(QFont("Fira Mono", 13))
        self.listen_label.setStyleSheet("color: #b200ff;")
        controls.addWidget(self.listen_label)

        controls.addStretch()
        self.diagnostic_label = QLabel("Diagnostic : ⏳")
        self.diagnostic_label.setFont(QFont("Fira Mono", 13))
        self.diagnostic_label.setStyleSheet("color: #ffd700;")
        controls.addWidget(self.diagnostic_label)

        self.toggle_btn = QPushButton("🎤 ON")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setFont(QFont("Fira Mono", 16))
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(y1:0, y2:1, stop:0 #b200ff, stop:1 #3d005b);
                color: #fff;
                font-weight: bold;
                border-radius: 7px;
                border: 2px solid #b200ff;
                padding: 7px 24px;
            }
            QPushButton:checked {
                background: #3d005b;
                color: #ffd700;
            }
        """)
        self.toggle_btn.clicked.connect(self._toggle_listen)
        controls.addWidget(self.toggle_btn)

        self.layout.addLayout(controls)

        # --- Timer for UI updates ---
        self.listening = False
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self.update_ui)
        self._update_timer.start(800)
        self.current_diag_state = "⏳"

    @Slot()
    def _toggle_listen(self):
        self.listening = not self.listening
        self.listen_label.setText(f"Écoute : {'ACTIVE' if self.listening else 'INACTIVE'}")
        self.wave.set_active(self.listening)
        self.toggle_btn.setText("🎤 ON" if self.listening else "🎤 OFF")
        self.toggle_listen.emit(self.listening)

    def append_text(self, text, color="#fff"):
        self.output_text.append(f'<span style="color:{color}">{text}</span>')

    def show_live_transcription(self, text, color="#ffd700"):
        # Ajoute la transcription live en bas
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