# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'changementDePage.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QHBoxLayout,
    QLabel, QListWidget, QListWidgetItem, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(708, 445)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(80, 110, 369, 248))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.Reactualiser = QPushButton(self.frame)
        self.Reactualiser.setObjectName(u"Reactualiser")

        self.verticalLayout_2.addWidget(self.Reactualiser)

        self.Statistique = QPushButton(self.frame)
        self.Statistique.setObjectName(u"Statistique")

        self.verticalLayout_2.addWidget(self.Statistique)

        self.Parametre = QPushButton(self.frame)
        self.Parametre.setObjectName(u"Parametre")

        self.verticalLayout_2.addWidget(self.Parametre)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.VoirFini = QCheckBox(self.frame)
        self.VoirFini.setObjectName(u"VoirFini")

        self.horizontalLayout_2.addWidget(self.VoirFini)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.listWidget = QListWidget(self.frame)
        self.listWidget.setObjectName(u"listWidget")

        self.verticalLayout.addWidget(self.listWidget)


        self.horizontalLayout.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 708, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Reactualiser.setText(QCoreApplication.translate("MainWindow", u"Reactualiser", None))
        self.Statistique.setText(QCoreApplication.translate("MainWindow", u"Statistique", None))
        self.Parametre.setText(QCoreApplication.translate("MainWindow", u"Parametre", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"changez de page", None))
        self.VoirFini.setText(QCoreApplication.translate("MainWindow", u"Voir les fiche d\u00e9ja trait\u00e9", None))
    # retranslateUi

