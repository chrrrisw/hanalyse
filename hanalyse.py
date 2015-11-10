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
import struct
import sys
from PyQt5 import QtWidgets
from qhexedit import QHexEdit
from mainwindow import Ui_MainWindow

__all__ = []
__version__ = 0.1
__date__ = '2014-01-09'
__updated__ = '2014-01-09'


class HexEdit(QHexEdit):

    def __init__(self, parent=None, filename=None):
        super(HexEdit, self).__init__(parent)
        if filename is not None:
            self.show_file(filename)

    def show_file(self, filename):
        file = open(filename)
        data = file.read()
        self.setData(data)
        self.setReadOnly(True)


# class HexFile:
#     def __init__(self, name):
#         """ Opens to file being analysed, reads it all in, and closes the file.
#         """
#         f = open(name, "rb")
#         # TODO: Should I really do this? Should I read it a chunk at a time?
#         self.fileContents = f.read()
#         f.close()

#     def lineStr(self, lineNum):
#         lineOffset = lineNum * 16
#         if lineOffset > len(self.fileContents):
#             lineOffset = 0  #TODO
#         values = struct.unpack_from("<16B", self.fileContents, lineOffset)

#         returnStr = "%07x" % (lineOffset)
#         endStr = "  "
#         for num, value in enumerate(values):
#             if num % 2 == 0:
#                 returnStr += " %02x" % (value)
#             else:
#                 returnStr += "%02x" % (value)
#             if 32 <= value <= 126:
#                 endStr += chr(value)
#             else:
#                 endStr += "."

#         return returnStr + endStr

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

        hex_1 = HexEdit(parent=self.frame_1, filename='hanalyse.py')
        layout_1.addWidget(hex_1)

        layout_2 = QtWidgets.QHBoxLayout()
        self.frame_2.setLayout(layout_2)

        hex_2 = HexEdit(parent=self.frame_2, filename='hanalyse.py')
        layout_2.addWidget(hex_2)

# class MainWindow:
#     def __init__(self, hexfile, hexdescfile):
#         # curX and curY store the current location at which to put the cursor
#         self.curX = 0
#         self.curY = 0

#         # is the cursor in the file being analysed, or in the description?
#         self.inHex = True

#         # the current location (absolute offset) within the file being analysed
#         self.hexLoc = 0

#         # initialise the screen and start our event loop
#         curses.wrapper(self.WrappedFunc, hexfile, hexdescfile)

#     def ToggleWindow(self):
#         # if we're in the hex, move to the description, and vice versa
#         if self.inHex:
#             self.inHex = False
#             # save where we are
#             self.savedX = self.curX
#             self.savedY = self.curY

#             # put the cursor on the last line
#             self.curX = self.maxyx[1]
#             self.curY = self.maxyx[0]

#             # self.win.move(self.cury, self.curx)
#         else:
#             self.inHex = True

#             # restore the cursor to where we left off
#             self.curX = self.savedX
#             self.curY = self.savedY

#     def Log(self, logstr):
#         # self.win.addstr(0,0,logstr)
#         pass

#     def WrappedFunc(self, stdscr, hexfile, hexdescfile):
#         self.win = stdscr
#         self.win.scrollok(0)
#         # self.win.addstr(self.curY, self.curX, "lines %d" % (curses.LINES))

#         pad_width = 8 + 16*3 + 18 + 2 # offset + data + chars + border
#         self.hexpad = curses.newpad(curses.LINES - 3, pad_width)
#         self.hexpad.border(0)
#         self.hexpad.scrollok(1)
#         self.hexpad.leaveok(0)
#         self.hexpad.addstr(1,1, hexfile.lineStr(0))
#         self.hexpad.addstr(2,1, hexfile.lineStr(1))
#         self.hexpad.addstr(3,1, hexfile.lineStr(2))
#         self.hexpad.addstr(4,1, hexfile.lineStr(3))
#         self.win.refresh()
#         self.hexpad.refresh(0, 0, 0, 0, curses.LINES - 4, pad_width + 1)

#         self.maxyx = self.win.getmaxyx()
#         # self.win.addstr(self.curY, self.curX, "show this text")
#         while True:
#             c = self.win.getch()
#             if c == ord("q"):
#                 hexdescfile.Close()
#                 break
#             elif c == ord("\t"):
#                 self.ToggleWindow()

#             # Cursor movement
#             elif c == curses.KEY_UP:
#                 self.Log("UP")
#                 # 16 bytes per line, going up a line
#                 if self.hexLoc >= 16:
#                     self.hexLoc -= 16
#                 self.curY -= 1
#                 self.win.move(self.curY, self.curX)
#             elif c == curses.KEY_DOWN:
#                 self.Log("DOWN")
#                 # 16 bytes per line, going down a line
#                 if self.hexLoc < len(hexfile.fileContents) - 16:
#                     self.hexLoc += 16
#                 self.curY += 1
#                 self.win.move(self.curY, self.curX)
#             elif c == curses.KEY_LEFT:
#                 self.Log("LEFT")
#                 if self.hexLoc > 0:
#                     self.hexLoc -= 1
#                 self.curX -= 1
#                 self.win.move(self.curY, self.curX)
#             elif c == curses.KEY_RIGHT:
#                 self.Log("RIGHT")
#                 if self.hexLoc < len(hexfile.fileContents):
#                     self.hexLoc += 1
#                 self.curX += 1
#                 self.win.move(self.curY, self.curX)
#             # Catch everything else
#             else:
#                 self.Log(str(c))
#             self.hexpad.cursyncup()


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

    # hexfile = HexFile(args.infile)
    # hexdescfile = HexDescFile(args.outfile)
    # mainwindow = MainWindow(hexfile, hexdescfile)

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    # mainWin = HexEdit('hanalyse.py')
    # mainWin.resize(600, 400)
    # mainWin.move(300, 300)
    # mainWin.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    sys.exit(main())
