# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'FormulaireChampsScientifique.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QFrame, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_centralwidget(object):
    def setupUi(self, centralwidget):
        if not centralwidget.objectName():
            centralwidget.setObjectName(u"centralwidget")
        centralwidget.resize(709, 473)
        self.frame = QFrame(centralwidget)
        self.frame.setObjectName(u"frame")
        self.frame.setGeometry(QRect(-10, 10, 631, 431))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.ChampsScientifiqueLayout = QHBoxLayout()
        self.ChampsScientifiqueLayout.setObjectName(u"ChampsScientifiqueLayout")
        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.ChampsScientifiqueLayout.addWidget(self.label_2)

        self.ChampsScientifiqueListe = QVBoxLayout()
        self.ChampsScientifiqueListe.setObjectName(u"ChampsScientifiqueListe")

        self.ChampsScientifiqueLayout.addLayout(self.ChampsScientifiqueListe)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.ChampsScientifiquePlus = QPushButton(self.frame)
        self.ChampsScientifiquePlus.setObjectName(u"ChampsScientifiquePlus")

        self.verticalLayout_3.addWidget(self.ChampsScientifiquePlus)

        self.ChampsScientifiqueMoins = QPushButton(self.frame)
        self.ChampsScientifiqueMoins.setObjectName(u"ChampsScientifiqueMoins")

        self.verticalLayout_3.addWidget(self.ChampsScientifiqueMoins)


        self.ChampsScientifiqueLayout.addLayout(self.verticalLayout_3)


        self.verticalLayout_4.addLayout(self.ChampsScientifiqueLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label, 0, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)

        self.NouveauChampsScientifique = QLineEdit(self.frame)
        self.NouveauChampsScientifique.setObjectName(u"NouveauChampsScientifique")

        self.verticalLayout_2.addWidget(self.NouveauChampsScientifique)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.NouveauChampsScientifiqueAnnuler = QPushButton(self.frame)
        self.NouveauChampsScientifiqueAnnuler.setObjectName(u"NouveauChampsScientifiqueAnnuler")

        self.horizontalLayout.addWidget(self.NouveauChampsScientifiqueAnnuler)

        self.NouveauChampsScientifiqueValider = QPushButton(self.frame)
        self.NouveauChampsScientifiqueValider.setObjectName(u"NouveauChampsScientifiqueValider")

        self.horizontalLayout.addWidget(self.NouveauChampsScientifiqueValider)


        self.verticalLayout_2.addLayout(self.horizontalLayout)


        self.verticalLayout_4.addLayout(self.verticalLayout_2)


        self.verticalLayout.addLayout(self.verticalLayout_4)

        self.buttonBox = QDialogButtonBox(self.frame)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(centralwidget)
        self.buttonBox.accepted.connect(centralwidget.accept)
        self.buttonBox.rejected.connect(centralwidget.reject)

        QMetaObject.connectSlotsByName(centralwidget)
    # setupUi

    def retranslateUi(self, centralwidget):
        centralwidget.setWindowTitle(QCoreApplication.translate("centralwidget", u"Dialog", None))
        self.label_2.setText(QCoreApplication.translate("centralwidget", u"liste des champs scientifique", None))
        self.ChampsScientifiquePlus.setText(QCoreApplication.translate("centralwidget", u"+", None))
        self.ChampsScientifiqueMoins.setText(QCoreApplication.translate("centralwidget", u"-", None))
        self.label.setText(QCoreApplication.translate("centralwidget", u"Cr\u00e9er un nouveau champs scientifique", None))
        self.NouveauChampsScientifiqueAnnuler.setText(QCoreApplication.translate("centralwidget", u"Annuler", None))
        self.NouveauChampsScientifiqueValider.setText(QCoreApplication.translate("centralwidget", u"Valider", None))
    # retranslateUi

