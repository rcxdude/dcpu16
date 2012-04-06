from PyQt4.QtCore import *
from PyQt4.QtGui import *
from . import dcpu
import utils
import functools

class WordSpinBox(QSpinBox):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.setRange(0, 0xffff)

    def textFromValue(self, value):
        return '0x{:0>4x}'.format(value)

    def valueFromText(self, text):
        try:
            return utils.string_to_value(text)
        except ValueError:
            return 0

class MemWordDelegate(QStyledItemDelegate):
    def __init__(self, mem_model, *args, **kargs):
        super().__init__(*args, **kargs)
        self.mem_model = mem_model

    def createEditor(self, parent, option, index):
        return WordSpinBox(parent)

    def sizeHint(self, option, index):
        return WordSpinBox().sizeHint()

class CPUMemTableModel(QAbstractTableModel):
    def __init__(self, mem, *args, **kargs):
        super().__init__(*args, **kargs)
        self.mem = mem

    def rowCount(self, parent):
        return int(dcpu.MEM_SIZE / 8)

    def columnCount(self, parent):
        return 8

    def data(self, index, role):
        if role == Qt.DisplayRole:
            word = self.mem[index.row() * 8 + index.column()]
            return '0x{:0>4x}'.format(word)
        if role == Qt.EditRole:
            word = self.mem[index.row() * 8 + index.column()]
            return word

    def setData(self, index, value, role):
        self.mem[index.row() * 8 + index.column()] = value
        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            return super().headerData(section, orientation, role)
        if role == Qt.DisplayRole:
            return '{:0>4x}'.format(section * 8)

class CPUNonZeroMemTableModel(QAbstractTableModel):
    def __init__(self, cpu, *args, **kargs):
        super().__init__(*args, **kargs)
        self.cpu = cpu
        self.get_chunks()
        self.modelAboutToBeReset.connect(self.get_chunks)

    def rowCount(self, parent):
        return self.rows

    def columnCount(self, parent):
        return 8

    def data(self, index, role):
        if not role == Qt.DisplayRole or role == Qt.EditRole:
            return
        addr = self.get_addr_for_row(index.row())
        word = self.cpu.struct.mem[addr * 8 + index.column()]
        if role == Qt.DisplayRole:
            return '0x{:0>4x}'.format(word)
        if role == Qt.EditRole:
            return word

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal:
            return super().headerData(section, orientation, role)
        if role == Qt.DisplayRole:
            addr = self.get_addr_for_row(section)
            return '{:0>4x}'.format(addr * 8)

    def get_addr_for_row(self, row):
        for chunk in self.chunks:
            if chunk[0] <= row:
                return chunk[1] + row - chunk[0]

    def get_chunks(self):
        chunks = self.cpu.get_nonzero_chunks()
        self.rows = 0
        self.chunks = []
        for chunk in chunks:
            self.chunks.append((self.rows, chunk[0], chunk[1]))
            self.rows += chunk[1] - chunk[0]
        self.chunks.reverse()

class CPUMemTableView(QTableView):
    def __init__(self, model, *args, **kargs):
        self.model = model
        super().__init__(*args, **kargs)
        width = WordSpinBox().sizeHint().width()
        height = WordSpinBox().sizeHint().height()
        self.verticalHeader().setDefaultSectionSize(height)
        self.horizontalHeader().setDefaultSectionSize(width)
        self.delegate = MemWordDelegate(self.model)
        self.setItemDelegate(self.delegate)
        self.setModel(self.model)
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def sizeHint(self):
        size = super().sizeHint()
        return QSize(self.horizontalHeader().length() +
                self.verticalHeader().width() + 30 ,size.height())

    def edit(self, index, trigger, event):
        ret = super().edit(index, trigger, event)
        if ret:
            self.resizeColumnToContents(index.column())
        return ret

class RegistersWidget(QWidget):
    def __init__(self, cpu, *args, **kargs):
        super().__init__(*args, **kargs)
        self.cpu = cpu
        self.cpu.registers = self
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.top_row = ["A", "B", "C", "X", "Y", "Z"]
        self.bottom_row = ["I", "J", "O", "PC", "SP"]
        self.labels = []
        self.spinboxes = []
        self.init_row(self.top_row,0)
        self.init_row(self.bottom_row,1)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def init_row(self, registers, row):
        for col,register in enumerate(registers):
            label = QLabel(register)
            spinbox = WordSpinBox()
            spinbox.__register = register
            spinbox.editingFinished.connect(functools.partial(self.value_changed, spinbox))
            self.labels.append(label)
            self.spinboxes.append(spinbox)
            self.layout.addWidget(label, row, col*2)
            self.layout.addWidget(spinbox, row, col*2 + 1)

    def reset(self):
        for spinbox in self.spinboxes:
            spinbox.setValue(getattr(self.cpu.struct,spinbox.__register))

    def value_changed(self, spinbox):
        setattr(self.cpu.struct, spinbox.__register, spinbox.value())

class CPUMemWidget(QWidget):
    def __init__(self, cpu, *args, **kargs):
        super().__init__(*args, **kargs)
        self.cpu = cpu
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.non_zero_mem_model = CPUNonZeroMemTableModel(self.cpu)
        self.mem_model = CPUMemTableModel(self.cpu.struct.mem)
        self.cpu.mem_model = self.non_zero_mem_model
        self.mem_table = CPUMemTableView(self.non_zero_mem_model)
        self.show_empty = QCheckBox("Show Empty memory regions")
        self.show_empty.stateChanged.connect(self.change_mem_model)

        self.registers = RegistersWidget(self.cpu)
        self.layout.addWidget(self.registers)
        self.layout.addWidget(self.mem_table)
        self.layout.addWidget(self.show_empty)

    def change_mem_model(self, state):
        if state == Qt.Checked:
            self.cpu.mem_model = self.mem_model
        else:
            self.cpu.mem_model = self.non_zero_mem_model
        self.mem_table.setModel(self.cpu.mem_model)
        self.cpu.mem_model.reset()

