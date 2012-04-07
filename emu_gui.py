#!/usr/bin/env python3
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys
import functools
import math

import gui.dcpu
import dasm.assembler
import dasm.lex
import gui.text
import gui.mem
import utils

class HertzSpinBox(QSpinBox):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.setSuffix("Hz")

    def textFromValue(self, value):
        if value >= 1000:
            value = value / 1000
            return '{}k'.format(value)
        else:
            return '{}'.format(value)

    def validate(self, text, pos):
        try:
            self.valueFromText(text)
            state = QValidator.Acceptable
        except ValueError:
            state = QValidator.Intermediate
        return (state, text, pos)

    def valueFromText(self, text):
        text = text.replace("Hz","")
        if text.endswith("k"):
            return float(text[:-1]) * 1000
        else:
            return float(text)

    def stepBy(self, steps):
        min_step = 10**(int(math.log10(self.value())) - 1)
        if min_step < 1:
            min_step = 1
        self.setValue(self.value() + steps * min_step)


class SpeedControl(QWidget):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.value = 1

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(100)
        self.slider.valueChanged.connect(self.update_spinbox)

        self.spinbox = HertzSpinBox()
        self.spinbox.setMinimum(1)
        self.spinbox.setMaximum(2e5)
        self.spinbox.valueChanged.connect(self.update_slider)

        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.spinbox)

    def update_spinbox(self, value):
        self.value = self.slider_to_actual(self.slider.value())
        self.spinbox.valueChanged.disconnect(self.update_slider)
        self.spinbox.setValue(self.value)
        self.spinbox.valueChanged.connect(self.update_slider)

    def update_slider(self, value):
        self.value = value
        value = self.actual_to_slider(value)
        self.slider.valueChanged.disconnect(self.update_spinbox)
        self.slider.setValue(value)
        self.slider.valueChanged.connect(self.update_spinbox)

    def actual_to_slider(self, actual):
        return int((math.log(actual / 2e5, 1e5) + 1) * 100)

    def slider_to_actual(self, sliderval):
        return int(1e5**(sliderval/100 - 1) * 2e5)

    def get_value(self):
        return self.value

class ControlPanel(QWidget):
    def __init__(self, program, *args, **kargs):
        super().__init__(*args, **kargs)
        self.program = program

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.startstop = QPushButton("Start")
        self.step = QPushButton("Step")
        self.reset = QPushButton("Reset")
        self.clear = QPushButton("Clear")
        self.step.pressed.connect(self.program.step)
        self.clear.pressed.connect(self.program.clear)
        self.reset.pressed.connect(self.program.reset)
        self.startstop.pressed.connect(self.start_stop)
        self.assemble = QPushButton("Assemble")
        self.assemble.pressed.connect(self.program.assemble)
        self.speed = SpeedControl()
        self.speed.slider.valueChanged.connect(functools.partial(program.set_speed, self.speed))
        self.speed.spinbox.valueChanged.connect(functools.partial(program.set_speed, self.speed))
        self.layout.addWidget(self.startstop)
        self.layout.addWidget(self.step)
        self.layout.addWidget(self.reset)
        self.layout.addWidget(self.clear)
        self.layout.addWidget(self.assemble)
        self.layout.addWidget(self.speed)
        self.layout.addStretch(1)

        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def start_stop(self):
        if self.startstop.text() == "Start":
            self.program.start()
            self.startstop.setText("Stop")
        else:
            self.program.stop()
            self.startstop.setText("Start")

class AsmProgram:
    def __init__(self, cpu, editor):
        self.cpu = cpu
        self.editor = editor
        self.listing = ''
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_step)
        self.run_speed = 1
        self.n_steps = 1
        self.timer.setInterval(1000/self.run_speed)

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

    def set_speed(self, slider, value):
        self.run_speed = slider.get_value()
        timestep = 1000/self.run_speed
        if timestep < 100:
            self.n_steps = int(100 / timestep)
        self.timer.setInterval(timestep * self.n_steps)

    def reset(self):
        self.cpu.struct.PC = 0
        self.cpu.struct.stopped = 0
        self.state_changed()

    def timer_step(self):
        self.cpu.step(self.n_steps)
        self.state_changed()
        if self.cpu.struct.stopped:
            self.stop()

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()


class CPUScreen(QLabel):
    def __init__(self, cpu, *args, **kargs):
        super().__init__(*args, **kargs)
        self.cpu = cpu
        self.start = 0x8000
        self.width = 32
        self.height = 16
        font = self.font()
        font.setFamily("monospace")
        self.setFont(font)
        self.cpu.mem_model.modelReset.connect(self.refresh)
        self.cpu.mem_model.dataChanged.connect(self.refresh)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.refresh()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def refresh(self, dummy = None, dummy2 = None):
        lines = []
        for i in range(self.height):
            start = self.start + i * self.width
            end = start + self.width
            words = (x & 0x7f for x in self.cpu.struct.mem[start:end])
            words = bytes((x if x > 0x1f else 0x20 for x in words))
            lines.append(str(words, encoding='ascii').rstrip())
        self.setText('\n'.join(lines))

class CPUWidget(QWidget):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.cpu = gui.dcpu.DCPU()
        self.layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.listing_editor = gui.text.AsmListingEditor(dasm.lex.Lexer(True))
        self.memory = gui.mem.CPUMemWidget(self.cpu)
        self.program = AsmProgram(self.cpu, self.listing_editor)
        self.screen = CPUScreen(self.cpu)
        self.controls = ControlPanel(self.program)
        self.layout.addLayout(self.left_layout)
        self.left_layout.addWidget(self.controls)
        self.left_layout.addWidget(self.memory)
        self.left_layout.addWidget(self.screen)
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
                "DCPU16 assembler files (*.asm *.dasm *.dasm16);;" + 
                 "DCPU16 hex files (*.hex)")
        if filename:
            self.center_view.open_file(filename)
            self.statusBar().showMessage("Loaded file " + filename)

app = QApplication(sys.argv)
main_window = EmuMainWindow()
main_window.show()
app.exec_()
