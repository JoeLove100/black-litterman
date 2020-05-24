from PySide2 import QtGui


class FontHelper:

    @staticmethod
    def get_title_font():

        font = QtGui.QFont("Calibri", 14, QtGui.QFont.Bold)
        return font

    @staticmethod
    def get_text_font():
        font = QtGui.QFont("Calibri", 8)
        return font
