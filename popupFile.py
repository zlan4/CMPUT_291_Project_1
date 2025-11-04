from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

def confirm_popup(message):
    "A popup that asks the user to either confirm or cancel"
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

def info_popup(message):
    """A popup that displays a message to the user.

    Args:
        message (str): message string

    """
    dialog = QDialog()
    dialog.setWindowTitle("Info")
    layout = QVBoxLayout(dialog)
    label = QLabel(message)
    layout.addWidget(label)
    btn_layout = QHBoxLayout()
    ok_btn = QPushButton("OK")
    ok_btn.clicked.connect(dialog.accept)
    btn_layout.addWidget(ok_btn)
    layout.addLayout(btn_layout)
    result = dialog.exec()
    return result == QDialog.DialogCode.Accepted

def input_popup(message):
    "Popup that takes input string from the user and displays a message."
    dialog = QDialog()
    dialog.setWindowTitle("Input Required")
    layout = QVBoxLayout(dialog)
    label = QLabel(message)
    layout.addWidget(label)
    line_edit = QLineEdit()
    layout.addWidget(line_edit)
    # Buttons
    btn_layout = QHBoxLayout()
    confirm_btn = QPushButton("Confirm")
    cancel_btn = QPushButton("Cancel")
    confirm_btn.clicked.connect(dialog.accept)
    cancel_btn.clicked.connect(dialog.reject)
    btn_layout.addWidget(confirm_btn)
    btn_layout.addWidget(cancel_btn)
    layout.addLayout(btn_layout)
    result = dialog.exec()
    text = line_edit.text().strip()
    if result == QDialog.DialogCode.Accepted and text != "":
        return True, text
    else:
        return False, ""