# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_gearthview.ui'
#
# Created: Mon Sep 30 13:54:19 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_gearthview(object):
    def setupUi(self, gearthview):
        gearthview.setObjectName(_fromUtf8("gearthview"))
        gearthview.resize(392, 153)
        self.buttonBox = QtGui.QDialogButtonBox(gearthview)
        self.buttonBox.setGeometry(QtCore.QRect(30, 100, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(gearthview)
        self.label.setGeometry(QtCore.QRect(30, 10, 121, 21))
        font = QtGui.QFont()
        font.setPointSize(15)
        font.setBold(True)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(gearthview)
        self.label_2.setGeometry(QtCore.QRect(40, 70, 161, 20))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(gearthview)
        self.label_3.setGeometry(QtCore.QRect(40, 40, 251, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_3.setFont(font)
        self.label_3.setObjectName(_fromUtf8("label_3"))

        self.retranslateUi(gearthview)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), gearthview.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), gearthview.reject)
        QtCore.QMetaObject.connectSlotsByName(gearthview)

    def retranslateUi(self, gearthview):
        gearthview.setWindowTitle(_translate("gearthview", "gearthview", None))
        self.label.setText(_translate("gearthview", "GEarthView", None))
        self.label_2.setText(_translate("gearthview", "geodrinx@gmail.com ", None))
        self.label_3.setText(_translate("gearthview", "displays QGis view into Google Earth", None))

