from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from GUI import UI
import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    UI_OBJECT = UI() 
    UI_OBJECT.show()
    app.exec() 