# vor Release alle comments mit !!release: beachten
# Qt.AlignLeft oä
# Character_sex fehlt nach random Char als update function
# manyToMany relationship wird mittels einer joint table dargestellt, wo jede Beziehung einzelnd dargestellt wird


import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt, QTimer, QEvent, QLineF
from PyQt5.QtGui import QFont, QPainter, QBrush, QImage, QPixmap, QColor, QPicture, QTransform, QPen
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QPushButton, QHBoxLayout, QGridLayout, QLineEdit, QMessageBox, \
    QVBoxLayout, \
    QStackedWidget, QFileDialog, QTabWidget, QFormLayout, QTextEdit, QScrollArea, QDialog, QComboBox, QDialogButtonBox, \
    QFrame,QGraphicsScene, QGraphicsView, QGraphicsTextItem

from datetime import datetime, timedelta

import Executable as ex
import DataHandler as dh
import random


class MyWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        scene=QGraphicsScene(0,0,400,400)
        graphicsView=QGraphicsView(scene)

        self.setCentralWidget(graphicsView)

        scene.setBackgroundBrush(QBrush(Qt.black,Qt.SolidPattern))
        graphicsView.setRenderHint(QPainter.Antialiasing)


        x=0
        y=0
        x1=400
        y1=400
        line=QLineF(x,y,x1,y1)

        colorlist=[(Qt.darkYellow, 3),(Qt.yellow, 2),(Qt.white, 1)]


        numberlist = []
        for i in range(100):
            numberlist.append(random.randint(0, 4)*6)

        for color in colorlist:

            pattern=[x/color[1] for x in numberlist]
            pen=QPen(*color)
            pen.setDashPattern(pattern)
            scene.addLine(line, pen)





# region Main program execution



App = QtWidgets.QApplication(sys.argv)
win = MyWindow()
win.show()
App.exec_()
sys.exit()

# endregion