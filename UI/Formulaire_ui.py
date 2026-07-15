# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Formulaire.ui'
##
## Created by: Qt User Interface Compiler version 6.11.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QGraphicsView, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QMenuBar, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(952, 668)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(0, 10, 921, 521))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_22 = QLabel(self.frame)
        self.label_22.setObjectName(u"label_22")

        self.gridLayout.addWidget(self.label_22, 18, 1, 1, 1)

        self.label_30 = QLabel(self.frame)
        self.label_30.setObjectName(u"label_30")

        self.gridLayout.addWidget(self.label_30, 12, 4, 1, 1)

        self.label_8 = QLabel(self.frame)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 3, 4, 1, 1)

        self.lineEdit_4 = QLineEdit(self.frame)
        self.lineEdit_4.setObjectName(u"lineEdit_4")

        self.gridLayout.addWidget(self.lineEdit_4, 7, 2, 1, 1)

        self.label_5 = QLabel(self.frame)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 5, 1, 1, 1)

        self.lineEdit_5 = QLineEdit(self.frame)
        self.lineEdit_5.setObjectName(u"lineEdit_5")

        self.gridLayout.addWidget(self.lineEdit_5, 8, 2, 1, 1)

        self.label_18 = QLabel(self.frame)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout.addWidget(self.label_18, 13, 1, 1, 1)

        self.lineEdit_8 = QLineEdit(self.frame)
        self.lineEdit_8.setObjectName(u"lineEdit_8")

        self.gridLayout.addWidget(self.lineEdit_8, 11, 2, 1, 1)

        self.lineEdit_6 = QLineEdit(self.frame)
        self.lineEdit_6.setObjectName(u"lineEdit_6")

        self.gridLayout.addWidget(self.lineEdit_6, 9, 2, 1, 1)

        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)

        self.progressBar_7 = QProgressBar(self.frame)
        self.progressBar_7.setObjectName(u"progressBar_7")
        self.progressBar_7.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_7.setValue(24)
        self.progressBar_7.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_7, 6, 3, 1, 1)

        self.progressBar_4 = QProgressBar(self.frame)
        self.progressBar_4.setObjectName(u"progressBar_4")
        self.progressBar_4.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_4.setValue(24)

        self.gridLayout.addWidget(self.progressBar_4, 3, 3, 1, 1)

        self.lineEdit_16 = QLineEdit(self.frame)
        self.lineEdit_16.setObjectName(u"lineEdit_16")

        self.gridLayout.addWidget(self.lineEdit_16, 3, 2, 1, 1)

        self.label_20 = QLabel(self.frame)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout.addWidget(self.label_20, 15, 1, 1, 1)

        self.label_13 = QLabel(self.frame)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout.addWidget(self.label_13, 8, 1, 1, 1)

        self.label_6 = QLabel(self.frame)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 0, 4, 1, 1)

        self.progressBar_14 = QProgressBar(self.frame)
        self.progressBar_14.setObjectName(u"progressBar_14")
        self.progressBar_14.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_14.setValue(24)
        self.progressBar_14.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_14, 13, 3, 1, 1)

        self.label_32 = QLabel(self.frame)
        self.label_32.setObjectName(u"label_32")

        self.gridLayout.addWidget(self.label_32, 14, 4, 1, 1)

        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 4, 1, 1, 1)

        self.label_16 = QLabel(self.frame)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout.addWidget(self.label_16, 11, 1, 1, 1)

        self.label_7 = QLabel(self.frame)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 2, 4, 1, 1)

        self.label_24 = QLabel(self.frame)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout.addWidget(self.label_24, 6, 4, 1, 1)

        self.lineEdit_17 = QLineEdit(self.frame)
        self.lineEdit_17.setObjectName(u"lineEdit_17")

        self.gridLayout.addWidget(self.lineEdit_17, 4, 2, 1, 1)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 2, 1, 1, 1)

        self.progressBar_19 = QProgressBar(self.frame)
        self.progressBar_19.setObjectName(u"progressBar_19")
        self.progressBar_19.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_19.setValue(24)
        self.progressBar_19.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_19, 19, 3, 1, 1)

        self.lineEdit_18 = QLineEdit(self.frame)
        self.lineEdit_18.setObjectName(u"lineEdit_18")

        self.gridLayout.addWidget(self.lineEdit_18, 5, 2, 1, 1)

        self.progressBar_15 = QProgressBar(self.frame)
        self.progressBar_15.setObjectName(u"progressBar_15")
        self.progressBar_15.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_15.setValue(24)
        self.progressBar_15.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_15, 14, 3, 1, 1)

        self.lineEdit = QLineEdit(self.frame)
        self.lineEdit.setObjectName(u"lineEdit")

        self.gridLayout.addWidget(self.lineEdit, 2, 2, 1, 1)

        self.label_21 = QLabel(self.frame)
        self.label_21.setObjectName(u"label_21")

        self.gridLayout.addWidget(self.label_21, 16, 1, 1, 1)

        self.progressBar_8 = QProgressBar(self.frame)
        self.progressBar_8.setObjectName(u"progressBar_8")
        self.progressBar_8.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_8.setValue(24)
        self.progressBar_8.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_8, 7, 3, 1, 1)

        self.progressBar_16 = QProgressBar(self.frame)
        self.progressBar_16.setObjectName(u"progressBar_16")
        self.progressBar_16.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_16.setValue(24)
        self.progressBar_16.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_16, 15, 3, 1, 1)

        self.label_35 = QLabel(self.frame)
        self.label_35.setObjectName(u"label_35")

        self.gridLayout.addWidget(self.label_35, 18, 4, 1, 1)

        self.label_17 = QLabel(self.frame)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout.addWidget(self.label_17, 12, 1, 1, 1)

        self.label_19 = QLabel(self.frame)
        self.label_19.setObjectName(u"label_19")

        self.gridLayout.addWidget(self.label_19, 14, 1, 1, 1)

        self.lineEdit_12 = QLineEdit(self.frame)
        self.lineEdit_12.setObjectName(u"lineEdit_12")

        self.gridLayout.addWidget(self.lineEdit_12, 15, 2, 1, 1)

        self.lineEdit_2 = QLineEdit(self.frame)
        self.lineEdit_2.setObjectName(u"lineEdit_2")

        self.gridLayout.addWidget(self.lineEdit_2, 0, 2, 1, 1)

        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 3, 1, 1, 1)

        self.lineEdit_15 = QLineEdit(self.frame)
        self.lineEdit_15.setObjectName(u"lineEdit_15")

        self.gridLayout.addWidget(self.lineEdit_15, 19, 2, 1, 1)

        self.progressBar_10 = QProgressBar(self.frame)
        self.progressBar_10.setObjectName(u"progressBar_10")
        self.progressBar_10.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_10.setValue(24)
        self.progressBar_10.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_10, 9, 3, 1, 1)

        self.progressBar_13 = QProgressBar(self.frame)
        self.progressBar_13.setObjectName(u"progressBar_13")
        self.progressBar_13.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_13.setValue(24)
        self.progressBar_13.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_13, 12, 3, 1, 1)

        self.label_9 = QLabel(self.frame)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 4, 4, 1, 1)

        self.progressBar_17 = QProgressBar(self.frame)
        self.progressBar_17.setObjectName(u"progressBar_17")
        self.progressBar_17.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_17.setValue(24)
        self.progressBar_17.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_17, 16, 3, 1, 1)

        self.progressBar_9 = QProgressBar(self.frame)
        self.progressBar_9.setObjectName(u"progressBar_9")
        self.progressBar_9.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_9.setValue(24)
        self.progressBar_9.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_9, 8, 3, 1, 1)

        self.progressBar_2 = QProgressBar(self.frame)
        self.progressBar_2.setObjectName(u"progressBar_2")
        self.progressBar_2.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_2.setValue(24)

        self.gridLayout.addWidget(self.progressBar_2, 2, 3, 1, 1)

        self.progressBar_18 = QProgressBar(self.frame)
        self.progressBar_18.setObjectName(u"progressBar_18")
        self.progressBar_18.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_18.setValue(24)
        self.progressBar_18.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_18, 18, 3, 1, 1)

        self.label_23 = QLabel(self.frame)
        self.label_23.setObjectName(u"label_23")

        self.gridLayout.addWidget(self.label_23, 19, 1, 1, 1)

        self.lineEdit_11 = QLineEdit(self.frame)
        self.lineEdit_11.setObjectName(u"lineEdit_11")

        self.gridLayout.addWidget(self.lineEdit_11, 14, 2, 1, 1)

        self.progressBar_3 = QProgressBar(self.frame)
        self.progressBar_3.setObjectName(u"progressBar_3")
        self.progressBar_3.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_3.setValue(24)
        self.progressBar_3.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_3, 0, 3, 1, 1)

        self.label_33 = QLabel(self.frame)
        self.label_33.setObjectName(u"label_33")

        self.gridLayout.addWidget(self.label_33, 15, 4, 1, 1)

        self.lineEdit_9 = QLineEdit(self.frame)
        self.lineEdit_9.setObjectName(u"lineEdit_9")

        self.gridLayout.addWidget(self.lineEdit_9, 12, 2, 1, 1)

        self.label_29 = QLabel(self.frame)
        self.label_29.setObjectName(u"label_29")

        self.gridLayout.addWidget(self.label_29, 11, 4, 1, 1)

        self.lineEdit_3 = QLineEdit(self.frame)
        self.lineEdit_3.setObjectName(u"lineEdit_3")

        self.gridLayout.addWidget(self.lineEdit_3, 6, 2, 1, 1)

        self.label_28 = QLabel(self.frame)
        self.label_28.setObjectName(u"label_28")

        self.gridLayout.addWidget(self.label_28, 10, 4, 1, 1)

        self.label_27 = QLabel(self.frame)
        self.label_27.setObjectName(u"label_27")

        self.gridLayout.addWidget(self.label_27, 9, 4, 1, 1)

        self.label_12 = QLabel(self.frame)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout.addWidget(self.label_12, 7, 1, 1, 1)

        self.lineEdit_10 = QLineEdit(self.frame)
        self.lineEdit_10.setObjectName(u"lineEdit_10")

        self.gridLayout.addWidget(self.lineEdit_10, 13, 2, 1, 1)

        self.label_14 = QLabel(self.frame)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout.addWidget(self.label_14, 9, 1, 1, 1)

        self.progressBar_11 = QProgressBar(self.frame)
        self.progressBar_11.setObjectName(u"progressBar_11")
        self.progressBar_11.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_11.setValue(24)
        self.progressBar_11.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_11, 10, 3, 1, 1)

        self.label_10 = QLabel(self.frame)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 5, 4, 1, 1)

        self.lineEdit_7 = QLineEdit(self.frame)
        self.lineEdit_7.setObjectName(u"lineEdit_7")

        self.gridLayout.addWidget(self.lineEdit_7, 10, 2, 1, 1)

        self.lineEdit_14 = QLineEdit(self.frame)
        self.lineEdit_14.setObjectName(u"lineEdit_14")

        self.gridLayout.addWidget(self.lineEdit_14, 18, 2, 1, 1)

        self.label_36 = QLabel(self.frame)
        self.label_36.setObjectName(u"label_36")

        self.gridLayout.addWidget(self.label_36, 19, 4, 1, 1)

        self.label_25 = QLabel(self.frame)
        self.label_25.setObjectName(u"label_25")

        self.gridLayout.addWidget(self.label_25, 7, 4, 1, 1)

        self.progressBar_6 = QProgressBar(self.frame)
        self.progressBar_6.setObjectName(u"progressBar_6")
        self.progressBar_6.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_6.setValue(24)

        self.gridLayout.addWidget(self.progressBar_6, 5, 3, 1, 1)

        self.progressBar_12 = QProgressBar(self.frame)
        self.progressBar_12.setObjectName(u"progressBar_12")
        self.progressBar_12.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_12.setValue(24)
        self.progressBar_12.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_12, 11, 3, 1, 1)

        self.lineEdit_13 = QLineEdit(self.frame)
        self.lineEdit_13.setObjectName(u"lineEdit_13")

        self.gridLayout.addWidget(self.lineEdit_13, 16, 2, 1, 1)

        self.label_26 = QLabel(self.frame)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout.addWidget(self.label_26, 8, 4, 1, 1)

        self.progressBar_5 = QProgressBar(self.frame)
        self.progressBar_5.setObjectName(u"progressBar_5")
        self.progressBar_5.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_5.setValue(24)

        self.gridLayout.addWidget(self.progressBar_5, 4, 3, 1, 1)

        self.label_15 = QLabel(self.frame)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout.addWidget(self.label_15, 10, 1, 1, 1)

        self.label_11 = QLabel(self.frame)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 6, 1, 1, 1)

        self.label_31 = QLabel(self.frame)
        self.label_31.setObjectName(u"label_31")

        self.gridLayout.addWidget(self.label_31, 13, 4, 1, 1)

        self.label_34 = QLabel(self.frame)
        self.label_34.setObjectName(u"label_34")

        self.gridLayout.addWidget(self.label_34, 16, 4, 1, 1)

        self.label_37 = QLabel(self.frame)
        self.label_37.setObjectName(u"label_37")

        self.gridLayout.addWidget(self.label_37, 17, 1, 1, 1)

        self.lineEdit_19 = QLineEdit(self.frame)
        self.lineEdit_19.setObjectName(u"lineEdit_19")

        self.gridLayout.addWidget(self.lineEdit_19, 17, 2, 1, 1)

        self.progressBar_20 = QProgressBar(self.frame)
        self.progressBar_20.setObjectName(u"progressBar_20")
        self.progressBar_20.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.progressBar_20.setValue(24)
        self.progressBar_20.setOrientation(Qt.Orientation.Horizontal)

        self.gridLayout.addWidget(self.progressBar_20, 17, 3, 1, 1)

        self.label_38 = QLabel(self.frame)
        self.label_38.setObjectName(u"label_38")

        self.gridLayout.addWidget(self.label_38, 17, 4, 1, 1)


        self.horizontalLayout.addLayout(self.gridLayout)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.graphicsView = QGraphicsView(self.frame)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setInteractive(True)

        self.horizontalLayout_3.addWidget(self.graphicsView)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.zoomInButton = QPushButton(self.frame)
        self.zoomInButton.setObjectName(u"zoomInButton")

        self.verticalLayout_2.addWidget(self.zoomInButton)

        self.zoomZero = QPushButton(self.frame)
        self.zoomZero.setObjectName(u"zoomZero")

        self.verticalLayout_2.addWidget(self.zoomZero)

        self.zoomOutButton = QPushButton(self.frame)
        self.zoomOutButton.setObjectName(u"zoomOutButton")

        self.verticalLayout_2.addWidget(self.zoomOutButton)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout_3.addLayout(self.verticalLayout_2)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.BarCentrale = QProgressBar(self.frame)
        self.BarCentrale.setObjectName(u"BarCentrale")
        self.BarCentrale.setStyleSheet(u"QProgressBar {\n"
"    border: 2px solid grey;\n"
"    border-radius: 5px;\n"
"    text-align: center;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #05B8CC;\n"
"    width: 20px;\n"
"}")
        self.BarCentrale.setValue(24)

        self.verticalLayout.addWidget(self.BarCentrale)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.Validation = QPushButton(self.frame)
        self.Validation.setObjectName(u"Validation")

        self.horizontalLayout_4.addWidget(self.Validation)

        self.Reset = QPushButton(self.frame)
        self.Reset.setObjectName(u"Reset")

        self.horizontalLayout_4.addWidget(self.Reset)

        self.Restart = QPushButton(self.frame)
        self.Restart.setObjectName(u"Restart")

        self.horizontalLayout_4.addWidget(self.Restart)

        self.Sauvgarde = QPushButton(self.frame)
        self.Sauvgarde.setObjectName(u"Sauvgarde")

        self.horizontalLayout_4.addWidget(self.Sauvgarde)

        self.Quiter = QPushButton(self.frame)
        self.Quiter.setObjectName(u"Quiter")

        self.horizontalLayout_4.addWidget(self.Quiter)


        self.verticalLayout.addLayout(self.horizontalLayout_4)


        self.horizontalLayout_2.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 952, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Nom de la Collectivite", None))
        self.label_30.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Numero du volume", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Co-Auteur", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Article", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Role CoAuteur", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Annee", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_32.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Complement du titre", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Indexation Rameau", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Titre", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Auteur Secondaire", None))
        self.label_35.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Premier Auteur", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Role Auteur", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Auteur", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"Role de la Collectivite", None))
        self.label_33.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_29.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_28.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_27.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Editeur", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Illustration", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_36.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_25.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Dimension", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Ville", None))
        self.label_31.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_34.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_37.setText(QCoreApplication.translate("MainWindow", u"Role Auteur Secondaire", None))
        self.label_38.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.zoomInButton.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.zoomZero.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.zoomOutButton.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.Validation.setText(QCoreApplication.translate("MainWindow", u"Fini", None))
        self.Reset.setText(QCoreApplication.translate("MainWindow", u"R\u00e9initialiser", None))
        self.Restart.setText(QCoreApplication.translate("MainWindow", u"Recommencer", None))
        self.Sauvgarde.setText(QCoreApplication.translate("MainWindow", u"Sauvegarder", None))
        self.Quiter.setText(QCoreApplication.translate("MainWindow", u"Quitter", None))
    # retranslateUi

