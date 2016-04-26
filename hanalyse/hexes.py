from PyQt5 import QtGui, QtCore
from QHexEdit import QHexEdit

from .utilities import create_menu, create_action

__all__ = ['MainHexEdit', 'SlaveHexEdit']

HIGHLIGHT_COLOUR = QtGui.QColor(255, 0, 0)


class MainHexEdit(QHexEdit):
    '''MainHexEdit is the widget that appears on the left hand side of the
    window. It provides the primary view of the data with all highlighing.'''

    show_offset = QtCore.pyqtSignal('qint64')
    createTag = QtCore.pyqtSignal('qint64', 'qint64')
    absoluteOffset = QtCore.pyqtSignal('qint64', 'qint64', 'qint64')
    relativeOffset = QtCore.pyqtSignal('qint64', 'qint64', 'qint64')

    def __init__(
            self,
            parent=None):
        '''Make readonly, connect positionChanged to remove_temp_highlight.'''

        super(MainHexEdit, self).__init__(parent)
        self.setReadOnly(True)
        self._temp_highlight = None
        self.positionChanged.connect(self.remove_temp_highlight)

        self._data_reader = None

        # Create context menu
        self._tagAction = create_action(
            parent=self,
            name="contextTag",
            text="Tag",
            triggered=self._on_tag)

        self._absMenu = create_menu(self, 'absMenu', 'Show absolute offset')

        self._absLittle = create_action(
            parent=self._absMenu,
            name='absLittle',
            text='Little endian',
            triggered=self._on_abs_offset)
        self._absBig = create_action(
            parent=self._absMenu,
            name='absBig',
            text='Big endian',
            triggered=self._on_abs_offset)

        self._relMenu = create_menu(self, 'relMenu', 'Show relative offset')

        self._relLittle = create_action(
            parent=self._relMenu,
            name='relLittle',
            text='Little endian',
            triggered=self._on_rel_offset)
        self._relBig = create_action(
            parent=self._relMenu,
            name='relBig',
            text='Big endian',
            triggered=self._on_rel_offset)

        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

    def add_temp_highlight(self, offset, length):
        '''Remove existing temporary highlight and create a new one.'''
        self.remove_temp_highlight(None)
        self._temp_highlight = (offset, offset + length - 1)
        self.highlightBackground(
            self._temp_highlight[0],
            self._temp_highlight[1],
            HIGHLIGHT_COLOUR)

    def remove_temp_highlight(self, offset):
        '''Remove the temporary highlight.'''
        if self._temp_highlight is not None:
            self.clearHighlight(
                self._temp_highlight[0],
                self._temp_highlight[1])
            self._temp_highlight = None

    def show_search_result(self, offset, length):
        self.setCursorPos(offset)
        self.add_temp_highlight(offset, length)

    def set_data_reader(self, reader):
        self._data_reader = reader

    @QtCore.pyqtSlot()
    def _on_tag(self):
        '''Emit the createTag signal, containing the start and end of selection.'''
        self.createTag.emit(
            self.selectionStart(),
            self.selectionEnd())

    @QtCore.pyqtSlot()
    def _on_abs_offset(self):
        '''Emit the absoluteOffset signal, containing the start and length of selection.'''
        start = self.selectionStart()
        length = self.selectionLength()
        offset = 0
        if self._data_reader is not None:
            data = self._data_reader.read(start, length + 1)
            if self.sender() == self._absLittle:
                offset = int.from_bytes(data, 'little', signed=False)
            else:
                offset = int.from_bytes(data, 'big', signed=False)

        self.absoluteOffset.emit(
            start,
            length,
            offset)

    @QtCore.pyqtSlot()
    def _on_rel_offset(self):
        '''Emit the relativeOffset signal, containing the start and length of selection.'''
        start = self.selectionStart()
        length = self.selectionLength()
        offset = 0
        if self._data_reader is not None:
            data = self._data_reader.read(start, length + 1)
            if self.sender() == self._relLittle:
                offset = int.from_bytes(data, 'little', signed=False)
            else:
                offset = int.from_bytes(data, 'big', signed=False)

        # TODO: Add current position to signal
        self.relativeOffset.emit(
            start,
            length,
            offset)

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

    def __init__(
            self,
            parent=None,
            on_find=None,
            on_find_again=None):

        super(SlaveHexEdit, self).__init__(parent)
        self.setReadOnly(True)

        self._data_reader = None

        # Create context menu
        self._findOffset = create_action(
            parent=self,
            name='contextFindOffset',
            text='Find offset')
        if on_find is not None:
            self._findOffset.triggered.connect(on_find)

        self._findOffsetAgain = create_action(
            parent=self,
            name='contextFindOffsetAgain',
            text='Find again')
        if on_find_again is not None:
            self._findOffsetAgain.triggered.connect(on_find_again)

        self.addAction(self._findOffset)
        self.addAction(self._findOffsetAgain)
        self.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

    def set_data_reader(self, reader):
        self._data_reader = reader
