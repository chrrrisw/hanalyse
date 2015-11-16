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
import uuid
import yaml
from enum import IntEnum
from PyQt5 import QtWidgets, QtGui, QtCore
from QHexEdit import QHexEdit, QHexEditData, QHexEditDataReader
from ui_mainwindow import Ui_MainWindow
from ui_tagdialog import Ui_Tag

__all__ = [
    'TagTypes',
    'TagRoles',
    'Tag',
    'MainHexEdit',
    'SlaveHexEdit',
    'MainWindow']

__version__ = 0.1
__date__ = '2015-11-13'
__updated__ = '2015-11-13'


class TagTypes(IntEnum):

    '''The type associated with a tag specifies how the data is to be read
    from the file.'''

    Char = 0
    Uint8 = 1
    Uint16 = 2
    Uint32 = 3
    Uint64 = 4
    Int8 = 5
    Int16 = 6
    Int32 = 7
    Int64 = 8
    String = 9
    Array = 10
    Unknown = 11


class TagRoles(IntEnum):
    '''The role associated with a tag specifies ....'''
    Constant = 0
    Count = 1
    Offset = 2
    Signature = 3
    Size = 4
    Data = 5
    Unknown = 6


def uchar_to_uint8(uchar):
    # 'big' or 'little'
    return (int.from_bytes(uchar, sys.byteorder, signed=False))


def uchar_to_int8(uchar):
    # 'big' or 'little'
    return (int.from_bytes(uchar, sys.byteorder, signed=True))


TYPECOLOURS = {
    TagTypes.Char: QtGui.QColor.fromHsv(0, 127, 255),
    TagTypes.Uint8: QtGui.QColor.fromHsv(30, 127, 255),
    TagTypes.Uint16: QtGui.QColor.fromHsv(60, 127, 255),
    TagTypes.Uint32: QtGui.QColor.fromHsv(90, 127, 255),
    TagTypes.Uint64: QtGui.QColor.fromHsv(120, 127, 255),
    TagTypes.Int8: QtGui.QColor.fromHsv(150, 127, 255),
    TagTypes.Int16: QtGui.QColor.fromHsv(180, 127, 255),
    TagTypes.Int32: QtGui.QColor.fromHsv(210, 127, 255),
    TagTypes.Int64: QtGui.QColor.fromHsv(240, 127, 255),
    TagTypes.String: QtGui.QColor.fromHsv(270, 127, 255),
    TagTypes.Array: QtGui.QColor.fromHsv(300, 127, 255),
}

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
    TagTypes.String: ('readString',),
    TagTypes.Array: ('readString',),
}

ROLECOLOURS = {
    TagRoles.Constant: QtGui.QColor.fromHsv(0, 127, 255),
    TagRoles.Count: QtGui.QColor.fromHsv(30, 127, 255),
    TagRoles.Offset: QtGui.QColor.fromHsv(60, 127, 255),
    TagRoles.Signature: QtGui.QColor.fromHsv(90, 127, 255),
    TagRoles.Size: QtGui.QColor.fromHsv(120, 127, 255),
    TagRoles.Data: QtGui.QColor.fromHsv(150, 127, 255),
    TagRoles.Unknown: QtGui.QColor.fromHsv(180, 127, 255),
}


class Tag(object):
    ''' The Tag object is used to hold the metadata associated with a sequence
    of bytes in the file.'''

    def __init__(self, **kwargs):
        self._identifier = uuid.uuid4()
        self._parent_tag = None

        self.name = kwargs.get('name', '')
        self.start = kwargs.get('start', 0)
        self.end = kwargs.get('end', 0)
        self.type = kwargs.get('type', TagTypes.Unknown)
        self.role = kwargs.get('role', TagRoles.Unknown)
        self.comment = kwargs.get('comment', '')

    @property
    def identifier(self):
        '''The unique identifier for the tag.'''
        return self._identifier

    @property
    def name(self):
        '''The human-readable name for a tag.'''
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def start(self):
        '''The absolute offset to the start of the tag. If set from a
        string, an attempt is made to interpret the string as a decimal
        or hexadecimal number.'''
        return self._start

    @start.setter
    def start(self, value):
        if type(value) == str:
            if value[:2].lower() == '0x':
                value = int(value, 16)
            else:
                value = int(value)
        self._start = value

    @property
    def end(self):
        '''The absolute offset to the end of the tag. If set from a
        string, an attempt is made to interpret the string as a decimal
        or hexadecimal number.'''
        return self._end

    @end.setter
    def end(self, value):
        if type(value) == str:
            if value[:2].lower() == '0x':
                value = int(value, 16)
            else:
                value = int(value)
        self._end = value

    @property
    def type(self):
        '''The type of data pointed to by the tag.'''
        return self._type

    @type.setter
    def type(self, value):
        if type(value) == str:
            value = TagTypes[value]
        self._type = value

    @property
    def role(self):
        '''The role the tag plays in the file.'''
        return self._role

    @role.setter
    def role(self, value):
        if type(value) == str:
            value = TagRoles[value]
        self._role = value

    @property
    def comment(self):
        '''A textual comment for the tag.'''
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment = value

    def __str__(self):
        return '''Tag:
\tParent: {}
\tName: {}
\tStart: {}
\tEnd: {}
\tType: {}
\tRole: {}
\tComment: {}'''.format(
            self._parent_tag,
            self._name,
            self._start,
            self._end,
            self._type.name,
            self._role.name,
            self._comment)

    # @classmethod
    # def _iter_fields(cls, as_declared=False):
    #     bases = cls.mro()[:2]
    #     if as_declared:
    #         bases.reverse()

    #     for base in bases:
    #         fields = base.__dict__.get('fields')
    #         if fields:
    #             for field in fields:
    #                 yield field['name'], field


class TagRepresenter(yaml.representer.SafeRepresenter):
    def represent_tag_object(self, data):
        # d = []
        # for name, field in data.__class__._iter_fields(True):
        #     d.append((name, getattr(data, name)))
        #     return self.represent_mapping('tag:yaml.org,2002:map', d)
        d = [
            ('name', data.name),
            ('start', data.start),
            ('end', data.end),
            ('type', data.type.name),
            ('role', data.role.name),
            ('comment', data.comment),
            ]
        return self.represent_mapping('tag:yaml.org,2002:map', d)

    def represent_tag_enum(self, data):
        return self.represent_scalar('tag:yaml.org,2002:str', data.name)

TagRepresenter.add_multi_representer(
    Tag, TagRepresenter.represent_tag_object)

TagRepresenter.add_multi_representer(
    IntEnum, TagRepresenter.represent_tag_enum)


class TagDumper(
        yaml.emitter.Emitter,
        yaml.serializer.Serializer,
        TagRepresenter,
        yaml.resolver.Resolver):

    def __init__(
            self, stream, default_style=None, default_flow_style=None,
            canonical=None, indent=None, width=None,
            allow_unicode=None, line_break=None,
            encoding=None, explicit_start=None, explicit_end=None,
            version=None, tags=None):
        yaml.emitter.Emitter.__init__(
            self, stream, canonical=canonical,
            indent=indent, width=width,
            allow_unicode=allow_unicode, line_break=line_break)
        yaml.serializer.Serializer.__init__(
            self, encoding=encoding,
            explicit_start=explicit_start, explicit_end=explicit_end,
            version=version, tags=tags)
        TagRepresenter.__init__(
            self, default_style=default_style,
            default_flow_style=default_flow_style)
        yaml.resolver.Resolver.__init__(self)


HIGHLIGHT_COLOUR = QtGui.QColor(255, 0, 0)


class MainHexEdit(QHexEdit):
    '''MainHexEdit is the widget that appears on the left hand side of the
    window. It provides the primary view of the data with all highlighing.'''

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
    '''SlaveHexEdit is the widget that appears on the right hand side of the
    window.'''

    def __init__(self, parent=None):
        super(SlaveHexEdit, self).__init__(parent)
        self.setReadOnly(True)


def create_action(parent, name, text, shortcut=None):
    new_action = QtWidgets.QAction(parent)
    new_action.setObjectName(name)
    new_action.setText(
        QtCore.QCoreApplication.translate(parent.objectName(), text))
    if shortcut is not None:
        new_action.setShortcut(
            QtCore.QCoreApplication.translate(parent.objectName(), shortcut))
    return new_action


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None, filename=None, tagfile=None):
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
        self._tagAction = create_action(
            self,
            "contextTag",
            "Tag")
        self._tagAction.triggered.connect(self.on_actionTag_triggered)

        self._absOffsetAction = create_action(
            self,
            'contextAbsOffset',
            'Show absolute offset')
        self._absOffsetAction.triggered.connect(self.show_abs_offset_cb)

        self._relOffsetAction = create_action(
            self,
            'contextRelOffset',
            'Show relative offset')
        self._relOffsetAction.triggered.connect(self.show_rel_offset_cb)

        self.hex_1.addAction(self._tagAction)
        self.hex_1.addAction(self._absOffsetAction)
        self.hex_1.addAction(self._relOffsetAction)
        self.hex_1.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # Create context menu in hex 2
        self._findOffset = create_action(
            self,
            'contextFindOffset',
            'Find offset')
        self._findOffset.triggered.connect(self.find_offset_cb)

        self._findOffsetAgain = create_action(
            self,
            'contextFindOffsetAgain',
            'Find again')
        self._findOffsetAgain.triggered.connect(self.find_offset_again_cb)

        self.hex_2.addAction(self._findOffset)
        self.hex_2.addAction(self._findOffsetAgain)
        self.hex_2.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        # Connect signals to slots
        self.hex_1.show_offset.connect(self.hex_2.setCursorPos)

        # Dialogs
        self._tag_dialog = QtWidgets.QDialog(self)
        self._tag_contents = Ui_Tag()
        self._tag_contents.setupUi(self._tag_dialog)
        for tag_type in TagTypes:
            self._tag_contents.typeComboBox.addItem('')
            self._tag_contents.typeComboBox.setItemText(
                tag_type.value,
                QtCore.QCoreApplication.translate(
                    self.objectName(), tag_type.name))
            self._tag_contents.of_combobox.addItem('')
            self._tag_contents.of_combobox.setItemText(
                tag_type.value,
                QtCore.QCoreApplication.translate(
                    self.objectName(), tag_type.name))
        for tag_role in TagRoles:
            self._tag_contents.role_combobox.addItem('')
            self._tag_contents.role_combobox.setItemText(
                tag_role.value,
                QtCore.QCoreApplication.translate(
                    self.objectName(), tag_role.name))
        self._tag_contents.typeComboBox.currentIndexChanged['QString'].connect(self.on_typeComboBox_currentIndexChanged)

        # Internal stuff
        self._hexeditdata = None
        self._hexeditdatareader = None
        self._tags = []

        if filename is not None:
            self.load_file(filename)

        if tagfile is not None:
            self.load_tags(tagfile)

    def load_file(self, filename):
        self._hexeditdata = QHexEditData.fromFile(filename)
        self._hexeditdatareader = QHexEditDataReader(
            self._hexeditdata,
            self)
        self.hex_1.setData(self._hexeditdata)
        self.hex_2.setData(self._hexeditdata)

    def load_tags(self, tagfile):
        load_file = open(tagfile)
        tags = yaml.safe_load(load_file)
        load_file.close()
        self._tags = []
        for tag in tags:
            print(tag)
            new_tag = Tag(**tag)
            print(new_tag)

            # Store it
            self._tags.append(new_tag)

            # Colour it
            self.hex_1.highlightBackground(
                new_tag.start,
                new_tag.end,
                ROLECOLOURS[new_tag.role])

            # Comment it
            self.hex_1.commentRange(
                new_tag.start,
                new_tag.end,
                new_tag.name)

    def create_tag(self, **kwargs):
        pass

    def delete_tag(self, tag):
        pass

    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        print('on_actionOpen_triggered')
        filename = QtWidgets.QFileDialog.getOpenFileName(
            parent=self,
            caption='Load File',
            directory='.',
            filter='All files (*)')
        if filename[0] != '':
            self.load_file(filename[0])
            # self._hexeditdata = QHexEditData.fromFile(filename[0])
            # self._hexeditdatareader = QHexEditDataReader(
            #     self._hexeditdata,
            #     self)
            # self.hex_1.setData(self._hexeditdata)
            # self.hex_2.setData(self._hexeditdata)

    @QtCore.pyqtSlot()
    def on_actionLoadTags_triggered(self):
        print('on_actionLoadTags_triggered')
        filename = QtWidgets.QFileDialog.getOpenFileName(
            parent=self,
            caption='Load File',
            directory='.',
            filter='YAML files (*.yaml);;All files (*)')
        if filename[0] != '':
            self.load_tags(filename[0])
            # load_file = open(filename[0])
            # tags = yaml.safe_load(load_file)
            # load_file.close()
            # self._tags = []
            # for tag in tags:
            #     print(tag)
            #     new_tag = Tag(**tag)
            #     print(new_tag)

            #     # Store it
            #     self._tags.append(new_tag)

            #     # Colour it
            #     self.hex_1.highlightBackground(
            #         new_tag.start,
            #         new_tag.end,
            #         ROLECOLOURS[new_tag.role])

            #     # Comment it
            #     self.hex_1.commentRange(
            #         new_tag.start,
            #         new_tag.end,
            #         new_tag.name)

    @QtCore.pyqtSlot()
    def on_actionSaveTags_triggered(self):
        print('on_actionSaveTags_triggered')
        filename = QtWidgets.QFileDialog.getSaveFileName(
            parent=self,
            caption='Load File',
            directory='.',
            filter='YAML files (*.yaml)')
        if filename[0] != '':
            save_file = open(filename[0], 'w')
            yaml.dump(self._tags, save_file, Dumper=TagDumper)
            save_file.close()

    @QtCore.pyqtSlot()
    def on_actionTag_triggered(self):
        if self._hexeditdatareader is not None:
            # TODO: Should we get the temp highlight instead of selection?
            self._tag_contents.extents_start_lineedit.setText(
                '0x{:08x}'.format(self.hex_1.selectionStart()))
            self._tag_contents.extents_end_lineedit.setText(
                '0x{:08x}'.format(self.hex_1.selectionEnd()))
            result = self._tag_dialog.exec_()

            if result:
                new_tag = Tag(
                    name=self._tag_contents.tag_lineedit.text(),
                    start=self._tag_contents.extents_start_lineedit.text(),
                    end=self._tag_contents.extents_end_lineedit.text(),
                    type=self._tag_contents.typeComboBox.currentText(),
                    role=self._tag_contents.role_combobox.currentText(),
                    comment=self._tag_contents.comment_textedit.toPlainText(),
                    )

                # Store it
                self._tags.append(new_tag)

                if new_tag.role == TagRoles.Count:
                    # Add it to the count combobox
                    self._tag_contents.countComboBox.addItem('')
                    self._tag_contents.countComboBox.setItemText(
                        self._tag_contents.countComboBox.count() - 1,
                        QtCore.QCoreApplication.translate(
                            self.objectName(), new_tag.name))

                # Colour it
                self.hex_1.highlightBackground(
                    new_tag.start,
                    new_tag.end,
                    ROLECOLOURS[new_tag.role])

                # Comment it
                self.hex_1.commentRange(
                    new_tag.start,
                    new_tag.end,
                    new_tag.name)

    @QtCore.pyqtSlot()
    def on_actionQuit_triggered(self):
        print('on_actionQuit_triggered')
        self.close()

    @QtCore.pyqtSlot(bool)
    def on_actionShowTags_triggered(self, checked):
        '''Called on user triggering the action, not on programmatic change.'''
        print('on_actionShowTags_triggered')

    # @QtCore.pyqtSlot(bool)
    # def on_actionShowTags_toggled(self, checked):
    #     print('on_actionShowTags_toggled')

    @QtCore.pyqtSlot(bool)
    def on_actionShowSlave_triggered(self, checked):
        '''Called on user triggering the action, not on programmatic change.'''
        print('on_actionShowSlave_triggered')

    @QtCore.pyqtSlot('QString')
    def on_typeComboBox_currentIndexChanged(self, text):
        print('on_typeComboBox_currentIndexChanged', text)
        if text == 'Array':
            self._tag_contents.of_combobox.setEnabled(True)
            self._tag_contents.of_label.setEnabled(True)
            self._tag_contents.countComboBox.setEnabled(True)
            self._tag_contents.count_label.setEnabled(True)
        else:
            self._tag_contents.of_combobox.setEnabled(False)
            self._tag_contents.of_label.setEnabled(False)
            self._tag_contents.countComboBox.setEnabled(False)
            self._tag_contents.count_label.setEnabled(False)

    def show_abs_offset_cb(self):
        if self._hexeditdatareader is not None:
            sel_start = self.hex_1.selectionStart()
            sel_length = self.hex_1.selectionLength()
            data = self._hexeditdatareader.read(sel_start, sel_length + 1)
            # print(data)
            offset = int.from_bytes(data, sys.byteorder, signed=False)
            self.hex_2.setCursorPos(offset)

    def show_rel_offset_cb(self):
        pass

    def allow_close(self):
        return True

    def find_offset_cb(self):
        if self._hexeditdatareader is not None:
            length = 4
            current_pos = self.hex_2.cursorPos().to_bytes(
                length,
                sys.byteorder,
                signed=False)
            found_pos = self._hexeditdatareader.indexOf(current_pos, 0)
            if found_pos > 0:
                self._foundPos = found_pos
                self.hex_1.show_search_result(found_pos, length)

    def find_offset_again_cb(self):
        if self._hexeditdatareader is not None:
            length = 4
            current_pos = self.hex_2.cursorPos().to_bytes(
                length,
                sys.byteorder,
                signed=False)
            found_pos = self._hexeditdatareader.indexOf(current_pos, self._foundPos)
            if found_pos > 0:
                self._foundPos = found_pos
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
            default=None,
            metavar='FILE',
            help='the input file')

        parser.add_argument(
            '-t',
            '--tag',
            dest="tagfile",
            default=None,
            metavar='FILE',
            help='the tag file')

        # process options
        args = parser.parse_args()

    except Exception as e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow(filename=args.infile, tagfile=args.tagfile)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    sys.exit(main())
