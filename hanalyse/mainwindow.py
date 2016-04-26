import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from QHexEdit import QHexEditData, QHexEditDataReader

# Generated code
from ui_mainwindow import Ui_MainWindow
from ui_tagdialog import Ui_Tag

from .hexes import MainHexEdit, SlaveHexEdit
from .utilities import create_action
from .tags import TagTypes, TagRoles, Tag, TagModel

# TODO: Indicate on hex_2 when offset selected on hex_1

TAG_LABEL_ORDER = {
    0: ('Name', 'name'),
    1: ('Start', 'start'),
    2: ('End', 'end'),
    3: ('Type', 'type'),
    4: ('Role', 'role'),
    5: ('Comment', 'comment'),
}

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

# TYPEREADERS = {
#     TagTypes.Char: ('at',),
#     TagTypes.Uint8: ('at', uchar_to_uint8),
#     TagTypes.Uint16: ('readUInt16',),
#     TagTypes.Uint32: ('readUInt32',),
#     TagTypes.Uint64: ('readUInt64',),
#     TagTypes.Int8: ('at', uchar_to_int8),
#     TagTypes.Int16: ('readInt16',),
#     TagTypes.Int32: ('readInt32',),
#     TagTypes.Int64: ('readInt64',),
#     TagTypes.String: ('readString',),
#     TagTypes.Array: ('readString',),
# }

ROLECOLOURS = {
    TagRoles.Constant: QtGui.QColor.fromHsv(0, 127, 255),
    TagRoles.Count: QtGui.QColor.fromHsv(30, 127, 255),
    TagRoles.Offset: QtGui.QColor.fromHsv(60, 127, 255),
    TagRoles.Signature: QtGui.QColor.fromHsv(90, 127, 255),
    TagRoles.Size: QtGui.QColor.fromHsv(120, 127, 255),
    TagRoles.Data: QtGui.QColor.fromHsv(150, 127, 255),
    TagRoles.Unknown: QtGui.QColor.fromHsv(180, 127, 255),
}


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
        self.hex_1.positionChanged.connect(self.hex_1_position_changed)
        self.hex_1.selectionChanged.connect(self.hex_1_selection_changed)

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
        self._tag_contents.typeComboBox.currentIndexChanged['QString'].connect(
            self.on_typeComboBox_currentIndexChanged)

        # Tag Model
        self._tag_model = TagModel(
            parent=self,
            orientation=QtCore.Qt.Horizontal,
            label_order=TAG_LABEL_ORDER)
        # self._tag_model.entrySelected.connect(self.tag_selected)
        # self._tag_model.dataChanged.connect(self.tag_edited)

        self.tagTableView.setModel(self._tag_model)
        self.tagTableView.resizeColumnsToContents()
        self.tagTableView.setSelectionMode(
            QtWidgets.QTableView.SingleSelection)
        self.tagTableView.setSelectionBehavior(
            QtWidgets.QTableView.SelectRows)

        self._tag_selection = self.tagTableView.selectionModel()
        self._tag_selection.selectionChanged.connect(
            self.tag_model_selection_changed)
        # self._tag_selection.currentChanged.connect(
        #     self.tag_model_current_changed)

        # Internal stuff
        self.programmatic_change = False
        self._hexeditdata = None
        self._hexeditdatareader = None
        # self._tags = []

        if filename is not None:
            self.load_file(filename)

        if tagfile is not None:
            self.load_tags(tagfile)

    def tag_model_current_changed(self, current, previous):
        '''Called on _tag_selection currentChanged signal'''
        if not self.programmatic_change:
            current_tag = self._tag_model.tags[current.row()]
            # print(current_tag.name)
            self.hex_1.setSelection(current_tag.start, current_tag.end)

    def tag_model_selection_changed(self, selected, deselected):
        '''Called on _tag_selection selectionChanged signal'''
        if not self.programmatic_change:
            # Hopefully not more than one.
            for sel in selected.indexes():
                current_tag = self._tag_model.tags[sel.row()]
                self.hex_1.setSelection(current_tag.start, current_tag.end)

    def hex_1_position_changed(self, offset):
        # TODO: Can we expose this through the hexedit widget?
        found = False
        row = 0
        for tag in self._tag_model.tags:
            if offset in range(tag.start, tag.end + 1):
                found = True
                self.programmatic_change = True
                # self._tag_selection.setCurrentIndex(
                #     self._tag_model.index(row, 0),
                #     QtCore.QItemSelectionModel.ClearAndSelect |
                #     QtCore.QItemSelectionModel.Rows)
                self._tag_selection.select(
                    self._tag_model.index(row, 0),
                    QtCore.QItemSelectionModel.Clear |
                    QtCore.QItemSelectionModel.Current |
                    QtCore.QItemSelectionModel.Select |
                    QtCore.QItemSelectionModel.Rows)
                self.programmatic_change = False
                self.tagTableView.scrollTo(self._tag_model.index(row, 0))
            row += 1

        if not found:
            # Clear selection
            self.programmatic_change = True
            self._tag_selection.clearSelection()
            self.programmatic_change = False

    def hex_1_selection_changed(self, length):
        pass

    def load_file(self, filename):
        self._hexeditdata = QHexEditData.fromFile(filename)
        self._hexeditdatareader = QHexEditDataReader(
            self._hexeditdata,
            self)
        self.hex_1.setData(self._hexeditdata)
        self.hex_2.setData(self._hexeditdata)

    def load_tags(self, tagfile):

        self._tag_model.read_from_file(tagfile)

        for tag in self._tag_model.tags:

            # Colour it
            self.hex_1.highlightBackground(
                tag.start,
                tag.end,
                ROLECOLOURS[tag.role])

            # Comment it
            self.hex_1.commentRange(
                tag.start,
                tag.end,
                tag.name)

    def create_tag(self, **kwargs):
        pass

    def delete_tag(self, tag):
        pass

    @QtCore.pyqtSlot()
    def on_actionOpen_triggered(self):
        # print('on_actionOpen_triggered')
        filename = QtWidgets.QFileDialog.getOpenFileName(
            parent=self,
            caption='Load File',
            directory='.',
            filter='All files (*)')
        if filename[0] != '':
            self.load_file(filename[0])

    @QtCore.pyqtSlot()
    def on_actionLoadTags_triggered(self):
        # print('on_actionLoadTags_triggered')
        filename = QtWidgets.QFileDialog.getOpenFileName(
            parent=self,
            caption='Load File',
            directory='.',
            filter='YAML files (*.yaml);;All files (*)')
        if filename[0] != '':
            self.load_tags(filename[0])

    @QtCore.pyqtSlot()
    def on_actionSaveTags_triggered(self):
        # print('on_actionSaveTags_triggered')
        filename = QtWidgets.QFileDialog.getSaveFileName(
            parent=self,
            caption='Load File',
            directory='.',
            filter='YAML files (*.yaml)')
        if filename[0] != '':
            self._tag_model.write_to_file(filename[0])

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
                # self._tags.append(new_tag)
                self._tag_model.append_tag(new_tag)

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
        # print('on_actionQuit_triggered')
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
        # print('on_typeComboBox_currentIndexChanged', text)
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
            found_pos = self._hexeditdatareader.indexOf(
                current_pos, self._foundPos)
            if found_pos > 0:
                self._foundPos = found_pos
                self.hex_1.show_search_result(found_pos, length)

    def closeEvent(self, event):
        if self.allow_close:
            event.accept()
        else:
            event.ignore()


