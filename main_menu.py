import subprocess
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os

class StarryNightMainMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Starry Night - Main Menu")
        self.setFixedSize(600, 400)

        title = QLabel("Starry Night")
        title.setFont(QFont("Times", 32, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        start_button = QPushButton("Start")
        start_button.setFont(QFont("Arial", 14))
        start_button.setFixedWidth(200)
        start_button.clicked.connect(self.start_game)

        quit_button = QPushButton("Quit")
        quit_button.setFont(QFont("Arial", 14))
        quit_button.setFixedWidth(200)
        quit_button.clicked.connect(self.quit_game)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(start_button, alignment=Qt.AlignCenter)
        layout.addWidget(quit_button, alignment=Qt.AlignCenter)
        layout.addStretch()

        self.setLayout(layout)

    def start_game(self):
        try:
            current_directory = os.path.dirname(os.path.realpath(__file__))

            game_script = os.path.join(current_directory, "combat_turn_based.py")

            if not os.path.exists(game_script):
                raise FileNotFoundError(f"Could not find {game_script}")

            subprocess.run([sys.executable, game_script], capture_output=True, text=True)

            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not launch game: {e}")

    def quit_game(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StarryNightMainMenu()
    window.show()
    sys.exit(app.exec_())
