#!/usr/bin/env python
# encoding: utf-8
'''
hanalyse -- hex dump analyser

hanalyse is a utility to annotate hex dumps for analysis

It defines classes_and_methods

@author:     Chris Willoughby
            
@copyright:  2014 Chris Willoughby. All rights reserved.
            
@license:    GPL3.0

@contact:    chrrrisw@gmail.com
@deffield    updated: Updated
'''

import struct
import sys
import os
import curses

from optparse import OptionParser

__all__ = []
__version__ = 0.1
__date__ = '2014-01-09'
__updated__ = '2014-01-09'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class HexFile:
    def __init__(self, name):
        """ Opens to file being analysed, reads it all in, and closes the file.
        """
        f = open(name, "rb")
        # TODO: Should I really do this? Should I read it a chunk at a time?
        self.fileContents = f.read()
        f.close()
        
    def lineStr(self, lineNum):
        lineOffset = lineNum * 16
        if lineOffset > len(self.fileContents):
            lineOffset = 0 #TODO
        values = struct.unpack_from("<16B", self.fileContents, lineOffset)
        
        returnStr = "%07x" % (lineOffset)
        endStr = "  "
        for num, value in enumerate(values):
            if num % 2 == 0:
                returnStr += " %02x" % (value)
            else:
                returnStr += "%02x" % (value)
            if 32 <= value <= 126:
                endStr += chr(value)
            else:
                endStr += "."
        
        return returnStr + endStr

class HexDescFile:
    """ This class handles the description file.
        A description file stores all the info related to the binary file being analysed.
    """
    
    def __init__(self, name, callback=None):
        """ Takes a filename for the description file and a callback.
            Opens the description file for appending.
            Reads in the current contents and calls the given callback passing
            file offset and type.
        """
        self.file = open(name, "a+")
        
        # TODO: Is this really the best way to do this? Should I not call readline()
        # and check for EOF == ""? That woudl be more memory efficient
        for line in self.file.readlines():
            pass
        
    def Close(self):
        """Closes the description file.
        """
        self.file.close()
        
    def MarkAs(self, location, ):
        """ Assigns a meaning to a particular location in the file being analysed.
            
        """
        
        # Arbitrary byte stream: fixed length, terminating sequence, length indication
        # Relative offset to data
        # Absolute offset to data
        # data
        # each will need an ID
        # extensible
        
        
        pass
    
class MainWindow:
    def __init__(self, hexfile, hexdescfile):
        # curX and curY store the current location at which to put the cursor
        self.curX = 0
        self.curY = 0
        
        # is the cursor in the file being analysed, or in the description?
        self.inHex = True
        
        # the current location (absolute offset) within the file being analysed
        self.hexLoc = 0
        
        # initialise the screen and start our event loop
        curses.wrapper(self.WrappedFunc, hexfile, hexdescfile)
        
    def ToggleWindow(self):
        # if we're in the hex, move to the description, and vice versa
        if self.inHex:
            self.inHex = False
            # save where we are
            self.savedX = self.curX
            self.savedY = self.curY
            
            # put the cursor on the last line
            self.curX = self.maxyx[1]
            self.curY = self.maxyx[0]
            
            #self.win.move(self.cury, self.curx)
        else:
            self.inHex = True
            
            # restore the cursor to where we left off
            self.curX = self.savedX
            self.curY = self.savedY
            
    def Log(self, logstr):
        #self.win.addstr(0,0,logstr)
        pass
        
    def WrappedFunc(self, stdscr, hexfile, hexdescfile):
        self.win = stdscr
        self.win.scrollok(0)
        #self.win.addstr(self.curY, self.curX, "lines %d" % (curses.LINES))
        
        pad_width = 8 + 16*3 + 18 + 2 # offset + data + chars + border
        self.hexpad = curses.newpad(curses.LINES - 3, pad_width)
        self.hexpad.border(0)
        self.hexpad.scrollok(1)
        self.hexpad.leaveok(0)
        self.hexpad.addstr(1,1, hexfile.lineStr(0))
        self.hexpad.addstr(2,1, hexfile.lineStr(1))
        self.hexpad.addstr(3,1, hexfile.lineStr(2))
        self.hexpad.addstr(4,1, hexfile.lineStr(3))
        self.win.refresh()
        self.hexpad.refresh(0, 0, 0, 0, curses.LINES - 4, pad_width + 1)
        
        self.maxyx = self.win.getmaxyx()
        #self.win.addstr(self.curY, self.curX, "show this text")
        while True:
            c = self.win.getch()
            if c == ord("q"):
                hexdescfile.Close()
                break
            elif c == ord("\t"):
                self.ToggleWindow()
                
            # Cursor movement
            elif c == curses.KEY_UP:
                self.Log("UP")
                # 16 bytes per line, going up a line
                if self.hexLoc >= 16:
                    self.hexLoc -= 16
                self.curY -= 1
                self.win.move(self.curY, self.curX)
            elif c == curses.KEY_DOWN:
                self.Log("DOWN")
                # 16 bytes per line, going down a line
                if self.hexLoc < len(hexfile.fileContents) - 16:
                    self.hexLoc += 16
                self.curY += 1
                self.win.move(self.curY, self.curX)
            elif c == curses.KEY_LEFT:
                self.Log("LEFT")
                if self.hexLoc > 0:
                    self.hexLoc -= 1
                self.curX -= 1
                self.win.move(self.curY, self.curX)
            elif c == curses.KEY_RIGHT:
                self.Log("RIGHT")
                if self.hexLoc < len(hexfile.fileContents):
                    self.hexLoc += 1
                self.curX += 1
                self.win.move(self.curY, self.curX)
            # Catch everything else
            else:
                self.Log(str(c))
            self.hexpad.cursyncup()

def main(argv=None):
    '''Command line options.'''
    
    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "%s" % __updated__
 
    program_version_string = '%%prog %s (%s)' % (program_version, program_build_date)
    program_longdesc = ''''''
    program_license = "Copyright 2014 Chris Willoughby.\nLicensed under GPL v3.0.\nhttp://www.gnu.org/licenses/"
 
    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=program_version_string, epilog=program_longdesc, description=program_license)
        parser.add_option("-i", "--in", dest="infile", help="set input path [default: %default]", metavar="FILE")
        parser.add_option("-o", "--out", dest="outfile", help="set output path [default: %default]", metavar="FILE")
        
        # set defaults
        parser.set_defaults(outfile="./out.txt", infile="./in.txt")
        
        # process options
        (opts, args) = parser.parse_args(argv)
        
        if opts.infile:
            print("infile = %s" % opts.infile)
        if opts.outfile:
            print("outfile = %s" % opts.outfile)
            
        # MAIN BODY #
        
    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    hexfile = HexFile(opts.infile)
    hexdescfile = HexDescFile(opts.outfile)
    mainwindow = MainWindow(hexfile, hexdescfile)
    
if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 'hanalyse_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
