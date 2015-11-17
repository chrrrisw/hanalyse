from enum import IntEnum
import uuid
import yaml
from PyQt5 import QtCore


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


class TagModel(QtCore.QAbstractTableModel):

    def __init__(self, parent, orientation, label_order):
        super(TagModel, self).__init__(parent)
        self._orientation = orientation
        self._label_order = label_order
        self._tags = []

    @property
    def orientation(self):
        return self._orientation

    @property
    def label_order(self):
        return self._label_order

    @property
    def tags(self):
        return self._tags

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            if self._orientation == QtCore.Qt.Horizontal:
                return len(self._tags)
            else:
                return len(self._label_order)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        else:
            if self._orientation == QtCore.Qt.Horizontal:
                return len(self._label_order)
            else:
                return len(self._tags)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        elif not 0 <= index.row() < self.rowCount():
            return None
        elif not 0 <= index.column() < self.columnCount():
            return None
        elif not (
                (role == QtCore.Qt.DisplayRole) or
                (role == QtCore.Qt.EditRole)):
            return None

        if self._orientation == QtCore.Qt.Horizontal:
            # Row is item, column is key
            item_number = index.row()
            key = self._label_order[index.column()][1]
        else:
            # Row is key, column is item
            item_number = index.column()
            key = self._label_order[index.row()][1]

        attr_val = getattr(self._tags[item_number], key, None)
        if ((type(attr_val) == TagTypes) or (type(attr_val) == TagRoles)):
            attr_val = attr_val.name
        return attr_val

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return None
        if orientation != self._orientation:
            return None
        return self._label_order[section][0]

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if not index.isValid():
            return False
        elif not 0 <= index.row() < self.rowCount():
            return False
        elif not 0 <= index.column() < self.columnCount():
            return False
        elif role != QtCore.Qt.EditRole:
            return False

        if self._orientation == QtCore.Qt.Horizontal:
            # row is item, column is key
            item_number = index.row()
            key = self._label_order[index.column()][1]
        else:
            # row is key, column is item
            item_number = index.column()
            key = self._label_order[index.row()][1]

        setattr(self._tags[item_number], key, value)
        self.dataChanged.emit(index, index)
        return True

    # def setHeaderData(
    #         self,
    #         section,
    #         orientation,
    #         value,
    #         role=QtCore.Qt.EditRole):
    #     pass

    def flags(self, index):
        return QtCore.Qt.ItemIsSelectable | \
            QtCore.Qt.ItemIsEditable | \
            QtCore.Qt.ItemIsEnabled

    def insertRows(self, row, count=1, parent=QtCore.QModelIndex()):
        success = False
        if self._orientation == QtCore.Qt.Horizontal:
            # Adding new items
            if 0 <= row <= len(self._tags):
                self.beginInsertRows(parent, row, row + count - 1)
                for c in range(count):
                    self._tags.insert(row + c, None)
                self.endInsertRows()
                success = True
        else:
            # Adding new labels
            if 0 <= row <= len(self._label_order):
                self.beginInsertRows(parent, row, row + count - 1)
                self.endInsertRows()
                success = True
        return success

    def removeRows(self, row, count=1, parent=QtCore.QModelIndex()):
        success = False
        if self._orientation == QtCore.Qt.Horizontal:
            # Removing items
            if row + count <= len(self._tags):
                self.beginRemoveRows(parent, row, row + count - 1)
                del self._tags[row:row + count]
                self.endRemoveRows()
                success = True
        else:
            # Removing labels
            if row + count <= len(self._label_order):
                self.beginRemoveRows(parent, row, row + count - 1)
                self.endRemoveRows()
                success = True
        return success

    def insertColumns(self, column, count=1, parent=QtCore.QModelIndex()):
        success = False
        if self._orientation == QtCore.Qt.Horizontal:
            # Adding new labels
            if 0 <= column <= len(self._label_order):
                self.beginInsertColumns(parent, column, column + count - 1)
                self.endInsertColumns()
                success = True
        else:
            # Adding new items
            if 0 <= column <= len(self._tags):
                self.beginInsertColumns(parent, column, column + count - 1)
                for c in range(count):
                    self._tags.insert(column + c, None)
                self.endInsertColumns()
                success = True
        return success

    def removeColumns(self, column, count=1, parent=QtCore.QModelIndex()):
        success = False
        if self._orientation == QtCore.Qt.Horizontal:
            # Removing labels
            if column + count <= len(self._label_order):
                self.beginRemoveColumns(parent, column, column + count - 1)
                self.endRemoveColumns()
                success = True
        else:
            # Removing items
            if column + count <= len(self._tags):
                self.beginRemoveColumns(parent, column, column + count - 1)
                del self._tags[column:column + count]
                self.endRemoveColumns()
                success = True
        return success

    def clear_rows(self):
        self.removeRows(0, self.rowCount())

    def clear_columns(self):
        self.removeColumns(0, self.columnCount())

    def append_tag(self, tag):
        try:
            if self._orientation == QtCore.Qt.Horizontal:
                position = self.rowCount()
                self.insertRows(position)
                top_left = self.index(position, 0, QtCore.QModelIndex())
                bottom_right = self.index(
                    position,
                    len(self._label_order) - 1,
                    QtCore.QModelIndex())
            else:
                position = self.columnCount()
                self.insertColumns(position)
                top_left = self.index(0, position, QtCore.QModelIndex())
                bottom_right = self.index(
                    len(self._label_order) - 1,
                    position,
                    QtCore.QModelIndex())

            # self._tags[position].update(tag)
            self._tags[position] = tag
            self.dataChanged.emit(top_left, bottom_right)

        except Exception as err:
            raise err

    def read_from_file(self, filename):
        '''Clears the current model and reads tags from a YAML file.'''
        load_file = open(filename, 'r')
        tags = yaml.safe_load(load_file)
        load_file.close()

        self.clear_rows()

        for tag in tags:
            # Create it
            new_tag = Tag(**tag)

            # Store it
            self.append_tag(new_tag)

    def write_to_file(self, filename):
        '''Writes all tags to a YAML file. Sorts them by tag start offset.'''

        def tag_start(tag):
            return tag.start

        save_file = open(filename, 'w')
        # yaml.dump(self._tags, save_file, Dumper=TagDumper)
        yaml.dump(
            sorted(self._tags, key=tag_start),
            save_file,
            Dumper=TagDumper)
        save_file.close()
