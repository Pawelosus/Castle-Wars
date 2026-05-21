import resources.resources_ui  # Loads in all resource files into UI
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class CreditsView(QFrame):
    def __init__(self, parent, back_callback) -> None:
        super().__init__(parent)

        self.setStyleSheet("background-color: rgb(0, 50, 100);")

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(0)

        title = QLabel("Credits")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white; font-family: Gabriola; font-size: 52px;")
        layout.addWidget(title)

        layout.addSpacing(12)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(255,255,255,60);")
        layout.addWidget(separator)

        layout.addSpacing(36)

        self._add_text(layout, "Original game: <b>Castle Wars</b> by m0rkeulv")
        layout.addSpacing(4)
        self._add_link(layout,
                       "https://cdn.m0rkeulv.net/games/html5/cwo/normal.html",
                       "cdn.m0rkeulv.net/games/html5/cwo/normal.html")

        layout.addSpacing(24)

        self._add_text(layout, "Fan remake written in Python / PyQt6")
        layout.addSpacing(4)
        self._add_link(layout,
                       "https://github.com/Pawelosus/Castle-Wars",
                       "github.com/Pawelosus/Castle-Wars")

        layout.addSpacing(44)

        back_button = QPushButton("← Back")
        back_button.setFixedSize(120, 36)
        back_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255,255,255,25);
                color: white;
                border: 1px solid rgba(255,255,255,90);
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(255,255,255,55); }
        """)
        back_button.clicked.connect(back_callback)
        layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def _add_text(self, layout, text: str) -> None:
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: rgba(255,255,255,210); font-size: 14px;")
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)

    def _add_link(self, layout, url: str, display: str) -> None:
        label = QLabel(f'<a href="{url}" style="color: rgba(140,190,255,220);">{display}</a>')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setOpenExternalLinks(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse)
        layout.addWidget(label)
