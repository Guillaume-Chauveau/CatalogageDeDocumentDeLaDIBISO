# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'RenduFormulaire.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPushButton, QSizePolicy,
    QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(640, 480)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.Reponce = QLabel(self.frame)
        self.Reponce.setObjectName(u"Reponce")

        self.verticalLayout.addWidget(self.Reponce)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.BoutonCopier = QPushButton(self.frame)
        self.BoutonCopier.setObjectName(u"BoutonCopier")

        self.horizontalLayout_2.addWidget(self.BoutonCopier)

        self.BoutonExporter = QPushButton(self.frame)
        self.BoutonExporter.setObjectName(u"BoutonExporter")

        self.horizontalLayout_2.addWidget(self.BoutonExporter)


        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)

        self.line = QFrame(self.frame)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.horizontalLayout_3.addWidget(self.line)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.BoutonFormulaire = QPushButton(self.frame)
        self.BoutonFormulaire.setObjectName(u"BoutonFormulaire")

        self.horizontalLayout.addWidget(self.BoutonFormulaire)

        self.BoutonHome = QPushButton(self.frame)
        self.BoutonHome.setObjectName(u"BoutonHome")

        self.horizontalLayout.addWidget(self.BoutonHome)


        self.horizontalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 640, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.Reponce.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
        self.BoutonCopier.setText(QCoreApplication.translate("MainWindow", u"Copier", None))
        self.BoutonExporter.setText(QCoreApplication.translate("MainWindow", u"Exporter", None))
        self.BoutonFormulaire.setText(QCoreApplication.translate("MainWindow", u"voir le formulaire", None))
        self.BoutonHome.setText(QCoreApplication.translate("MainWindow", u"Page d'accueil", None))
    # retranslateUi

