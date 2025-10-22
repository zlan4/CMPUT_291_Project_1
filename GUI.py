from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6 import uic

class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('designerFile.ui', self)