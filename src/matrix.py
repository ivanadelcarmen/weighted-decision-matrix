import sys

from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QStyledItemDelegate,
    QLineEdit,
    QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

from ui.scripts.matrix_ui import Ui_form


class CellDoubleClickDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        
        # Center align the text
        editor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Only allow numbers 1-10 with strict validation
        validator = QIntValidator(1, 10, editor)
        validator.setBottom(1)
        validator.setTop(10)
        editor.setValidator(validator)
        
        # Connect textChanged to enforce strict validation
        editor.textChanged.connect(lambda text: self.validate_input(editor, text))
        
        return editor
    
    def validate_input(self, editor, text):
        """Strictly validate input to only allow 1-10"""
        if text:
            # Remove leading zeros
            if text.startswith('0'):
                editor.setText(text.lstrip('0'))
                return
            
            # Check if number is valid
            try:
                num = int(text)
                if num > 10:
                    # If greater than 10, keep only first digit
                    editor.setText(text[0])
                elif num < 1:
                    editor.clear()
            except ValueError:
                pass
    
    def setModelData(self, editor, model, index):
        """Ensure the data is centered when saved"""
        text = editor.text()
        if text:  # Only set if there's text
            try:
                num = int(text)
                if 1 <= num <= 10:
                    model.setData(index, text, Qt.ItemDataRole.DisplayRole)
                    # Set text alignment for the cell
                    model.setData(index, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
            except ValueError:
                pass


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_form()
        self.ui.setupUi(self)

        table = self.ui.matrixTable
        table.setItemDelegate(CellDoubleClickDelegate())
        
        # Configure table to stretch columns and rows equally
        self.setup_table_stretching()
    
    def setup_table_stretching(self):
        """Configure the table to stretch columns and rows equally"""
        table = self.ui.matrixTable
        
        # Make columns stretch equally
        horizontal_header = table.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Make rows stretch equally
        vertical_header = table.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Optional: Set minimum sizes to prevent columns/rows from becoming too small
        horizontal_header.setMinimumSectionSize(100)
        vertical_header.setMinimumSectionSize(60)
        
        # Disable multi-selection - only allow single cell selection
        from PyQt6.QtWidgets import QAbstractItemView
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())