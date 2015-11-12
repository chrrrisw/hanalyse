#!/usr/bin/env python3
# encoding: utf-8
'''
hanalyse -- hex dump analyser

hanalyse is a utility to annotate hex dumps for analysis

It defines:

@author:     Chris Willoughby

@copyright:  2015 Chris Willoughby. All rights reserved.

@license:    GPL3.0

@contact:    chrrrisw@gmail.com
@deffield    updated: Updated
'''

import argparse
import os
import sys
from enum import IntEnum
from PyQt5 import QtWidgets, QtGui, QtCore
from QHexEdit import QHexEdit, QHexEditData, QHexEditDataReader
from ui_mainwindow import Ui_MainWindow
from ui_tagdialog import Ui_Tag

__all__ = []
__version__ = 0.1
__date__ = '2014-01-09'
__updated__ = '2014-01-09'


class TagTypes(IntEnum):
    Char = 1
    Uint8 = 2
    Uint16 = 3
    Uint32 = 4
    Uint64 = 5
    Int8 = 6
    Int16 = 7
    Int32 = 8
    Int64 = 9
    String = 10


def uchar_to_uint8(uchar):
    # 'big' or 'little'
    return (int.from_bytes(uchar, sys.byteorder, signed=False))


def uchar_to_int8(uchar):
    # 'big' or 'little'
    return (int.from_bytes(uchar, sys.byteorder, signed=True))


TYPEREADERS = {
    TagTypes.Char: ('at',),
    TagTypes.Uint8: ('at', uchar_to_uint8),
    TagTypes.Uint16: ('readUInt16',),
    TagTypes.Uint32: ('readUInt32',),
    TagTypes.Uint64: ('readUInt64',),
    TagTypes.Int8: ('at', uchar_to_int8),
    TagTypes.Int16: ('readInt16',),
    TagTypes.Int32: ('readInt32',),
    TagTypes.Int64: ('readInt64',),
    TagTypes.String: ('readString',)
}


class Tag(object):
    def __init__(self):
        self.parent_tag = None
        self.identifier = None
        self.tag_type = None
        self.tag

HIGHLIGHT_COLOUR = QtGui.QColor(255, 0, 0)


class MainHexEdit(QHexEdit):

    show_offset = QtCore.pyqtSignal('qint64')

    def __init__(self, parent=None):
        super(MainHexEdit, self).__init__(parent)
        self.setReadOnly(True)
        self._temp_highlight = None
        self.positionChanged.connect(self.remove_temp_highlight)

    def add_temp_highlight(self, offset, length):
        self.remove_temp_highlight(None)
        self._temp_highlight = (offset, offset + length - 1)
        self.highlightBackground(
            self._temp_highlight[0],
            self._temp_highlight[1],
            HIGHLIGHT_COLOUR)

    def remove_temp_highlight(self, offset):
        if self._temp_highlight is not None:
            self.clearHighlight(
                self._temp_highlight[0],
                self._temp_highlight[1])
            self._temp_highlight = None

    def show_search_result(self, offset, length):
        self.setCursorPos(offset)
        self.add_temp_highlight(offset, length)

    # Inherited methods

    # def contextMenuEvent(self, event):
    #     menu = QtWidgets.QMenu(self)
    #     commentAction = menu.addAction("Comment")
    #     absOffsetAction = menu.addAction("Show as absolute offset")
    #     relOffsetAction = menu.addAction("Show as relative offset")
    #     action = menu.exec_(self.mapToGlobal(event.pos()))
    #     if action == commentAction:
    #         self.add_comment()
    #     elif action == absOffsetAction:
    #         self.show_absolute_offset()
    #     elif action == relOffsetAction:
    #         self.show_relative_offset()

    # New class methods

    # def add_tag(self):
    #     print('Cursor pos'.format(self.cursorPos()))
    #     print('Selection start'.format(self.selectionStart()))
    #     self.commentRange(
    #         self.selectionStart(),
    #         self.selectionEnd(),
    #         "Foo")

    # def show_absolute_offset(self):
    #     self.show_offset.emit(10)

    # def show_relative_offset(self):
    #     self.show_offset.emit(20)


class SlaveHexEdit(QHexEdit):

    def __init__(self, parent=None):
        super(SlaveHexEdit, self).__init__(parent)
        self.setReadOnly(True)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)

        # Create a layout and hexedit widget
        layout_1 = QtWidgets.QHBoxLayout()
        self.frame_1.setLayout(layout_1)
        self.hex_1 = MainHexEdit(parent=self.frame_1)
        layout_1.addWidget(self.hex_1)

        # Create a layout and hexedit widget
        layout_2 = QtWidgets.QHBoxLayout()
        self.frame_2.setLayout(layout_2)
        self.hex_2 = SlaveHexEdit(parent=self.frame_2)
        layout_2.addWidget(self.hex_2)

        # Create context menu in hex 1
        self._tagAction = QtWidgets.QAction(
            "Tag", None)
        self._tagAction.triggered.connect(self.tag_cb)

        self._absOffsetAction = QtWidgets.QAction(
            "Show absolute offset", None)
        self._absOffsetAction.triggered.connect(self.show_abs_offset_cb)

        self._relOffsetAction = QtWidgets.QAction(
            "Show relative offset", None)
        self._relOffsetAction.triggered.connect(self.show_rel_offset_cb)

        self.hex_1.addAction(self._tagAction)
        self.hex_1.addAction(self._absOffsetAction)
        self.hex_1.addAction(self._relOffsetAction)
        self.hex_1.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # Create context menu in hex 2
        self._findOffset = QtWidgets.QAction(
            'Find offset', None)
        self._findOffset.triggered.connect(self.find_offset_cb)
        self.hex_2.addAction(self._findOffset)
        self.hex_2.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # Connect signals to slots
        self.hex_1.show_offset.connect(self.hex_2.setCursorPos)

        # Connect up the menu
        self.actionOpen.triggered.connect(self.open_cb)
        self.actionTag.triggered.connect(self.tag_cb)
        self.actionQuit.triggered.connect(self.quit_cb)

        # Dialogs
        self._tag_dialog = QtWidgets.QDialog(self)
        self._tag_contents = Ui_Tag()
        self._tag_contents.setupUi(self._tag_dialog)

        # Internal stuff
        self._hexeditdata = None
        self._hexeditdatareader = None

    # def open_file(self, filename):
    #     self.hex_1.show_file(filename[0])
    #     self.hex_2.show_file(filename[0])

    def open_cb(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Load File', '.', '*')
        if filename[0] != '':
            self._hexeditdata = QHexEditData.fromFile(filename[0])
            self._hexeditdatareader = QHexEditDataReader(
                self._hexeditdata,
                self)
            self.hex_1.setData(self._hexeditdata)
            self.hex_2.setData(self._hexeditdata)
            # self.open_file(filename[0])

    def tag_cb(self):
        # TODO: Should we get the temp highlight instead of selection?
        self._tag_contents.extents_start_lineedit.setText(
            '0x{:08x}'.format(self.hex_1.selectionStart()))
        self._tag_contents.extents_end_lineedit.setText(
            '0x{:08x}'.format(self.hex_1.selectionEnd()))
        result = self._tag_dialog.exec_()

        if result:
            pass

    def show_abs_offset_cb(self):
        sel_start = self.hex_1.selectionStart()
        sel_length = self.hex_1.selectionLength()
        data = self._hexeditdatareader.read(sel_start, sel_length + 1)
        print(data)
        offset = int.from_bytes(data, sys.byteorder, signed=False)
        self.hex_2.setCursorPos(offset)

    def show_rel_offset_cb(self):
        pass

    def quit_cb(self):
        self.close()

    def allow_close(self):
        return True

    def find_offset_cb(self):
        length = 4
        current_pos = self.hex_2.cursorPos().to_bytes(
            length,
            sys.byteorder,
            signed=False)
        found_pos = self._hexeditdatareader.indexOf(current_pos, 0)
        if found_pos > 0:
            self.hex_1.show_search_result(found_pos, length)

    def closeEvent(self, event):
        if self.allow_close:
            event.accept()
        else:
            event.ignore()


def main():
    '''Command line options.'''

    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__

    program_version_string = '%%prog %s (%s)' % (
        program_version, program_build_date)
    program_longdesc = ''''''
    program_license = '''Copyright 2014 Chris Willoughby.
Licensed under GPL v3.0.\nhttp://www.gnu.org/licenses/'''

    try:
        # setup argument parser
        parser = argparse.ArgumentParser(
            description='A file analysis tool',
            epilog=program_longdesc)

        parser.add_argument(
            '-i',
            '--in',
            dest="infile",
            metavar='FILE',
            help='the input file')

        # process options
        args = parser.parse_args()

        if args.infile:
            print("infile = %s" % args.infile)

        # MAIN BODY #

    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    sys.exit(main())
