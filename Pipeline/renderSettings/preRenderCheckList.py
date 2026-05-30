from PySide6.QtWidgets import (
    QWidget, QVBoxLayout,
    QCheckBox, QLabel, QGroupBox
)
from PySide6.QtCore import Qt


class ChecklistUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Maya Render Checklist")
        self.setMinimumWidth(300)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)  # optional "post-it" behavior

        layout = QVBoxLayout()

        # Title
        title = QLabel("Pre-Render Checklist")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # --- Main Checklist ---
        main_group = QGroupBox("General")
        main_layout = QVBoxLayout()

        items = [
            "LIGHT GROUP",
            "SAMPLING",
            "DIRECTORY",
            "IMAGE NAME",
            "FRAME RANGE",
            "CAM",
            "RENDER LAYERS",
            "__Pref",
            "AVOID OVERRIDE",
            "Dx_Opener"
        ]

        for item in items:
            checkbox = QCheckBox(item)
            main_layout.addWidget(checkbox)

        main_group.setLayout(main_layout)
        layout.addWidget(main_group)

        # --- Damage Version ---
        damage_group = QGroupBox("DAMAGE VERSION")
        damage_layout = QVBoxLayout()

        damage_items = ["CHARA", "ENV"]

        for item in damage_items:
            checkbox = QCheckBox(item)
            damage_layout.addWidget(checkbox)

        damage_group.setLayout(damage_layout)
        layout.addWidget(damage_group)

        self.setLayout(layout)


# --- Safe launcher (prevents duplicates) ---
try:
    checklist_ui.close()
    checklist_ui.deleteLater()
except:
    pass

checklist_ui = ChecklistUI()
checklist_ui.show()