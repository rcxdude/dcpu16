from PyQt4.QtCore import *
from PyQt4.QtGui import *
import collections
from .linenumber import LNTextEdit

class AsmSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, lexer, *args, **kargs):
        super().__init__(*args, **kargs)
        self.lexer = lexer.clone()
        self.formats = collections.defaultdict(QTextCharFormat)
        self.formats['ADDR'].setForeground(Qt.darkMagenta)
        self.formats['INSTR'].setForeground(Qt.cyan)
        self.formats['INSTR'].setFontWeight(QFont.Bold)
        self.formats['COMMENT'].setForeground(Qt.green)
        self.formats['NUMBER'].setForeground(Qt.blue)
        self.formats['LABEL'].setForeground(Qt.darkRed)
        self.formats['NAME'].setFontWeight(QFont.Bold)
        self.formats['UNEXPECTED'].setFontUnderline(True)
        self.formats['UNEXPECTED'].setForeground(Qt.red)
        self.formats['STRING'].setForeground(Qt.cyan)

    def highlightBlock(self, string):
        lexer = self.lexer.clone()
        lexer.input(string)
        for tok in lexer:
            self.setFormat(tok.lexpos, len(tok.value), self.formats[tok.type])


class AsmListingEditor(LNTextEdit):
    def __init__(self, lexer = None, *args, **kargs):
        super().__init__(*args, **kargs)
        self.edit.font().setFamily("monospace")
        font = self.edit.font()
        font.setFamily("monospace")
        self.edit.setFont(font)

        if lexer is not None:
            self.highlighter = AsmSyntaxHighlighter(lexer, self.edit.document())
