from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

def confirm_popup(message):
    dialog = QDialog()
    dialog.setWindowTitle("Confirm")

    layout = QVBoxLayout(dialog)

    label = QLabel(message)
    layout.addWidget(label)

    btn_layout = QHBoxLayout()
    ok_btn = QPushButton("OK")
    cancel_btn = QPushButton("Cancel")

    ok_btn.clicked.connect(dialog.accept)
    cancel_btn.clicked.connect(dialog.reject)

    btn_layout.addWidget(ok_btn)
    btn_layout.addWidget(cancel_btn)

    layout.addLayout(btn_layout)

    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted
