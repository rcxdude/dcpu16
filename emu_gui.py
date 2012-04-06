#!/usr/bin/env python3
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import gui.dcpu
import dasm.assembler
import dasm.lex
import gui.text
import utils
import gui.mem

class ControlPanel(QWidget):
    def __init__(self, program, *args, **kargs):
        super().__init__(*args, **kargs)
        self.program = program

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.start = QPushButton("Start")
        self.stop = QPushButton("Stop")
        self.step = QPushButton("Step")
        self.reset = QPushButton("Reset")
        self.clear = QPushButton("Clear")
        self.step.pressed.connect(self.program.step)
        self.clear.pressed.connect(self.program.clear)
        self.reset.pressed.connect(self.program.reset)
        self.assemble = QPushButton("Assemble")
        self.assemble.pressed.connect(self.program.assemble)
        self.layout.addWidget(self.start)
        self.layout.addWidget(self.stop)
        self.layout.addWidget(self.step)
        self.layout.addWidget(self.reset)
        self.layout.addWidget(self.clear)
        self.layout.addWidget(self.assemble)
        self.layout.addStretch(1)

class AsmProgram:
    def __init__(self, cpu, editor):
        self.cpu = cpu
        self.editor = editor
        self.listing = ''

    def assemble(self):
        self.listing = self.editor.getText()
        word_list, instructions = dasm.assembler.assemble_listing(self.listing)
        self.cpu.load_from_hex(word_list, 0)
        self.cpu.mem_model.reset()

    def set_listing(self, listing):
        self.listing = listing
        self.editor.setText(listing)

    def state_changed(self):
        self.cpu.mem_model.reset()
        self.cpu.registers.reset()

    def step(self):
        self.cpu.step()
        self.state_changed()

    def clear(self):
        self.cpu.load_from_hex([0] * (gui.dcpu.MEM_SIZE),0)
        self.state_changed()

    def reset(self):
        self.cpu.struct.PC = 0
        self.cpu.registers.reset()


class CPUWidget(QWidget):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.cpu = gui.dcpu.DCPU()
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.listing_editor = gui.text.AsmListingEditor(dasm.lex.Lexer(True))
        self.memory = gui.mem.CPUMemWidget(self.cpu)
        self.program = AsmProgram(self.cpu, self.listing_editor)
        self.controls = ControlPanel(self.program)
        self.layout.addWidget(self.memory)
        self.layout.addWidget(self.controls)
        self.layout.addWidget(self.listing_editor)

    def open_file(self, filename):
        ifile = open(filename, 'r')
        self.program.set_listing(ifile.read())

class EmuMainWindow(QMainWindow):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.center_view = CPUWidget()
        self.setCentralWidget(self.center_view)
        self.init_menu()
        self.statusBar().showMessage("Loaded")

    def init_menu(self):
        menubar = self.menuBar()

        exit = QAction(QIcon("exit24.png"), "&Exit", self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit Emulator')
        exit.triggered.connect(app.quit)

        open_file = QAction(QIcon("open.png"), "&Open", self)
        open_file.setShortcut('Ctrl+O')
        open_file.setStatusTip('Open Asm File')
        open_file.triggered.connect(self.open_file)

        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit)
        file_menu.addAction(open_file)

    def open_file(self):
        filename = QFileDialog.getOpenFileName(self, "Open asm file", ".",
                "DCPU16 assembler files (*.asm);;" + 
                 "DCPU16 hex files (*.hex)")
        if filename:
            self.center_view.open_file(filename)
            self.statusBar().showMessage("Loaded file " + filename)

app = QApplication(sys.argv)
main_window = EmuMainWindow()
main_window.show()
app.exec_()
