"""Syntax highlighter for diagnostic output."""

from PyQt5.QtCore import QRegularExpression
from PyQt5.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat


class LogHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        rules = (
            (r"\[OK\]|completed\.$", "#34d399"),
            (r"\[WARNING\]|warning|timed out", "#fbbf24"),
            (r"\[ERROR\]|failed|could not|critical", "#f87171"),
            (r"^={10,}$|^> ", "#60a5fa"),
        )
        self.rules = []
        for pattern, color in rules:
            expression = QRegularExpression(pattern)
            expression.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
            text_format = QTextCharFormat()
            text_format.setForeground(QColor(color))
            self.rules.append((expression, text_format))

    def highlightBlock(self, text):
        for expression, text_format in self.rules:
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(), match.capturedLength(), text_format
                )
