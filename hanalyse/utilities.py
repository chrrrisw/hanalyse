import sys
from PyQt5 import QtWidgets, QtCore

__all__ = ['create_action']


def uchar_to_uint8(uchar):
    # 'big' or 'little'
    return (int.from_bytes(uchar, sys.byteorder, signed=False))


def uchar_to_int8(uchar):
    # 'big' or 'little'
    return (int.from_bytes(uchar, sys.byteorder, signed=True))


def create_action(parent, name, text, shortcut=None):
    new_action = QtWidgets.QAction(parent)
    new_action.setObjectName(name)
    new_action.setText(
        QtCore.QCoreApplication.translate(parent.objectName(), text))
    if shortcut is not None:
        new_action.setShortcut(
            QtCore.QCoreApplication.translate(parent.objectName(), shortcut))
    return new_action
