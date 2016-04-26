import sys
from PyQt5 import QtWidgets, QtCore

__all__ = ['create_action']


def uchar_to_uint8(uchar):
    # 'big' or 'little'
    return (int.from_bytes(uchar, sys.byteorder, signed=False))


def uchar_to_int8(uchar):
    # 'big' or 'little'
    return (int.from_bytes(uchar, sys.byteorder, signed=True))


def create_menu(parent, name, title):
    menu = QtWidgets.QMenu(parent)
    menu.setObjectName(name)
    parent.addAction(menu.menuAction())
    menu.setTitle(
        QtCore.QCoreApplication.translate(parent.objectName(), title))
    return menu


def create_action(parent, name, text, shortcut=None, triggered=None):
    new_action = QtWidgets.QAction(parent)
    new_action.setObjectName(name)
    new_action.setText(
        QtCore.QCoreApplication.translate(parent.objectName(), text))
    if shortcut is not None:
        new_action.setShortcut(
            QtCore.QCoreApplication.translate(parent.objectName(), shortcut))
    if triggered is not None:
        new_action.triggered.connect(triggered)
    parent.addAction(new_action)

    return new_action
