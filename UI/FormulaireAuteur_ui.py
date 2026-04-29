# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FormulaireAuteur.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QGridLayout,
    QLabel, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(865, 579)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(100, 40, 581, 231))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.AuteurMoins = QPushButton(self.frame)
        self.AuteurMoins.setObjectName(u"AuteurMoins")

        self.gridLayout.addWidget(self.AuteurMoins, 0, 3, 1, 1)

        self.formLayoutAuteur = QFormLayout()
        self.formLayoutAuteur.setObjectName(u"formLayoutAuteur")

        self.gridLayout.addLayout(self.formLayoutAuteur, 0, 1, 1, 1)

        self.Secondaire = QLabel(self.frame)
        self.Secondaire.setObjectName(u"Secondaire")

        self.gridLayout.addWidget(self.Secondaire, 2, 0, 1, 1)

        self.Auteur = QLabel(self.frame)
        self.Auteur.setObjectName(u"Auteur")

        self.gridLayout.addWidget(self.Auteur, 0, 0, 1, 1)

        self.CoAuteur = QLabel(self.frame)
        self.CoAuteur.setObjectName(u"CoAuteur")

        self.gridLayout.addWidget(self.CoAuteur, 1, 0, 1, 1)

        self.AuteurPlus = QPushButton(self.frame)
        self.AuteurPlus.setObjectName(u"AuteurPlus")

        self.gridLayout.addWidget(self.AuteurPlus, 0, 2, 1, 1)

        self.formLayoutCoAuteur = QFormLayout()
        self.formLayoutCoAuteur.setObjectName(u"formLayoutCoAuteur")

        self.gridLayout.addLayout(self.formLayoutCoAuteur, 1, 1, 1, 1)

        self.formLayoutAuteurSecondaire = QFormLayout()
        self.formLayoutAuteurSecondaire.setObjectName(u"formLayoutAuteurSecondaire")

        self.gridLayout.addLayout(self.formLayoutAuteurSecondaire, 2, 1, 1, 1)

        self.CoAuteurPlus = QPushButton(self.frame)
        self.CoAuteurPlus.setObjectName(u"CoAuteurPlus")

        self.gridLayout.addWidget(self.CoAuteurPlus, 1, 2, 1, 1)

        self.SecondairePlus = QPushButton(self.frame)
        self.SecondairePlus.setObjectName(u"SecondairePlus")

        self.gridLayout.addWidget(self.SecondairePlus, 2, 2, 1, 1)

        self.CoAuteurMoins = QPushButton(self.frame)
        self.CoAuteurMoins.setObjectName(u"CoAuteurMoins")

        self.gridLayout.addWidget(self.CoAuteurMoins, 1, 3, 1, 1)

        self.SecondaireMoins = QPushButton(self.frame)
        self.SecondaireMoins.setObjectName(u"SecondaireMoins")

        self.gridLayout.addWidget(self.SecondaireMoins, 2, 3, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.Validez = QPushButton(self.frame)
        self.Validez.setObjectName(u"Validez")

        self.verticalLayout.addWidget(self.Validez)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 865, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.AuteurMoins.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.Secondaire.setText(QCoreApplication.translate("MainWindow", u"Auteur secondaire", None))
        self.Auteur.setText(QCoreApplication.translate("MainWindow", u"Auteur", None))
        self.CoAuteur.setText(QCoreApplication.translate("MainWindow", u"Co-Auteur", None))
        self.AuteurPlus.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.CoAuteurPlus.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.SecondairePlus.setText(QCoreApplication.translate("MainWindow", u"+", None))
        self.CoAuteurMoins.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.SecondaireMoins.setText(QCoreApplication.translate("MainWindow", u"-", None))
        self.Validez.setText(QCoreApplication.translate("MainWindow", u"Validez", None))
    # retranslateUi

