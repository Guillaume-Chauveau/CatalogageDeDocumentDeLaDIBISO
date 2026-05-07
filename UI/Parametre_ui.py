# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Parametre.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFrame, QGridLayout,
    QHBoxLayout, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(784, 508)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(80, 60, 691, 401))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayoutWidget = QWidget(self.frame)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(0, -1, 691, 391))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.ParametreCommun = QCheckBox(self.verticalLayoutWidget)
        self.ParametreCommun.setObjectName(u"ParametreCommun")

        self.horizontalLayout.addWidget(self.ParametreCommun)

        self.ParametreClassique = QCheckBox(self.verticalLayoutWidget)
        self.ParametreClassique.setObjectName(u"ParametreClassique")

        self.horizontalLayout.addWidget(self.ParametreClassique)

        self.ParametreHebdomadaire = QCheckBox(self.verticalLayoutWidget)
        self.ParametreHebdomadaire.setObjectName(u"ParametreHebdomadaire")

        self.horizontalLayout.addWidget(self.ParametreHebdomadaire)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.ListeParametre = QGridLayout()
        self.ListeParametre.setObjectName(u"ListeParametre")

        self.verticalLayout.addLayout(self.ListeParametre)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.ToutVrai = QCheckBox(self.verticalLayoutWidget)
        self.ToutVrai.setObjectName(u"ToutVrai")

        self.horizontalLayout_2.addWidget(self.ToutVrai)

        self.ToutFaux = QCheckBox(self.verticalLayoutWidget)
        self.ToutFaux.setObjectName(u"ToutFaux")

        self.horizontalLayout_2.addWidget(self.ToutFaux)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.Annuler = QPushButton(self.verticalLayoutWidget)
        self.Annuler.setObjectName(u"Annuler")

        self.horizontalLayout_3.addWidget(self.Annuler)

        self.Valider = QPushButton(self.verticalLayoutWidget)
        self.Valider.setObjectName(u"Valider")

        self.horizontalLayout_3.addWidget(self.Valider)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 784, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.ParametreCommun.setText(QCoreApplication.translate("MainWindow", u"Param\u00e8tres Commun", None))
        self.ParametreClassique.setText(QCoreApplication.translate("MainWindow", u"Param\u00e8tres Classique", None))
        self.ParametreHebdomadaire.setText(QCoreApplication.translate("MainWindow", u"Param\u00e8tres Hebdomadaire", None))
        self.ToutVrai.setText(QCoreApplication.translate("MainWindow", u"Tout Vrai", None))
        self.ToutFaux.setText(QCoreApplication.translate("MainWindow", u"Tout Faux", None))
        self.Annuler.setText(QCoreApplication.translate("MainWindow", u"Annuler", None))
        self.Valider.setText(QCoreApplication.translate("MainWindow", u"Valider", None))
    # retranslateUi

