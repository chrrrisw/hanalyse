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
from PyQt5 import QtWidgets, QtGui
from QHexEdit import QHexEdit, QHexEditData
from ui_mainwindow import Ui_MainWindow

__all__ = []
__version__ = 0.1
__date__ = '2014-01-09'
__updated__ = '2014-01-09'


class HexEdit(QHexEdit):

    def __init__(self, parent=None, filename=None):
        super(HexEdit, self).__init__(parent)
        if filename is not None:
            self.show_file(filename)

    # Inherited methods

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        commentAction = menu.addAction("Comment")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == commentAction:
            self.add_comment()

    # New class methods

    def add_comment(self):
        self.commentRange(
            self.selectionStart(),
            self.selectionEnd(),
            "Foo")

# class HexDescFile:
#     """ This class handles the description file.
#         A description file stores all the info related to the binary file being analysed.
#     """

#     def __init__(self, name, callback=None):
#         """ Takes a filename for the description file and a callback.
#             Opens the description file for appending.
#             Reads in the current contents and calls the given callback passing
#             file offset and type.
#         """
#         self.file = open(name, "a+")

#         # TODO: Is this really the best way to do this? Should I not call readline()
#         # and check for EOF == ""? That woudl be more memory efficient
#         for line in self.file.readlines():
#             pass

#     def Close(self):
#         """Closes the description file.
#         """
#         self.file.close()

#     def MarkAs(self, location, ):
#         """ Assigns a meaning to a particular location in the file being analysed.

#         """

#         # Arbitrary byte stream: fixed length, terminating sequence, length indication
#         # Relative offset to data
#         # Absolute offset to data
#         # data
#         # each will need an ID
#         # extensible

#         pass


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.setupUi(self)

        layout_1 = QtWidgets.QHBoxLayout()
        self.frame_1.setLayout(layout_1)

        self.hex_1 = HexEdit(parent=self.frame_1)
        layout_1.addWidget(self.hex_1)

        layout_2 = QtWidgets.QHBoxLayout()
        self.frame_2.setLayout(layout_2)

        self.hex_2 = HexEdit(parent=self.frame_2)
        layout_2.addWidget(self.hex_2)

        self.actionOpen.triggered.connect(self.open_cb)
        self.actionQuit.triggered.connect(self.quit_cb)

    def quit_cb(self):
        print('Quit pressed')
        self.close()

    def open_file(self, filename):
        self.hex_1.show_file(filename[0])
        self.hex_2.show_file(filename[0])

    def open_cb(self):
        print('Open pressed')
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Load File', '.', '*')
        if filename[0] != '':
            hexeditdata = QHexEditData.fromFile(filename[0])
            self.hex_1.setData(hexeditdata)
            self.hex_2.setData(hexeditdata)
            # self.open_file(filename[0])

    def allow_close(self):
        return True

    def closeEvent(self, event):
        print('closeEvent')
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
