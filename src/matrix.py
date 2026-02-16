import sys

from PyQt6.QtWidgets import (
    QWidget,
    QApplication,
    QStyledItemDelegate,
    QLineEdit,
    QHeaderView,
    QTableWidgetItem,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

from ui.scripts.matrix_ui import Ui_form
from core.weighted_matrix import WeightedMatrix


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
            
            # Check if the number is valid
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
    def __init__(self, matrix=None):
        super().__init__()

        self.ui = Ui_form()
        self.ui.setupUi(self)
        
        # Use provided matrix or create new one
        self.matrix = matrix if matrix else WeightedMatrix()

        table = self.ui.matrixTable
        table.setItemDelegate(CellDoubleClickDelegate())
        
        # Configure table to stretch columns and rows equally
        self.setup_table_stretching()
        
        # Connect buttons
        self.ui.modifyBtn.clicked.connect(self.open_modify_dialog)
        self.ui.resultsBtn.clicked.connect(self.show_results)
        
        # Connect cell changes to update matrix
        table.cellChanged.connect(self.on_cell_changed)
        
        # Initialize with default data if matrix is empty
        if self.matrix.rows == 0 and self.matrix.cols == 0:
            self.initialize_default_matrix()
        else:
            # Update display with existing matrix data
            self.update_table_display()
    
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
    
    def on_cell_changed(self, row, col):
        """Update the matrix when a cell value changes"""
        table = self.ui.matrixTable
        item = table.item(row, col)
        
        if item and item.text():
            try:
                value = int(item.text())
                if 1 <= value <= 10:
                    self.matrix.update_value(value, row + 1, col + 1)
            except:
                pass
    
    def open_modify_dialog(self):
        """Open rows dialog to modify matrix"""
        from rows import RowsWindow
        rows_window = RowsWindow(self.matrix)
        rows_window.show()
        self.close()
    
    def update_table_display(self):
        """Update the table to reflect the current matrix state"""
        table = self.ui.matrixTable
        
        # Block signals to prevent triggering cellChanged
        table.blockSignals(True)
        
        # Set table dimensions
        table.setRowCount(self.matrix.rows)
        table.setColumnCount(self.matrix.cols)
        
        # Set column headers with weights
        for j, col in enumerate(self.matrix.matrix):
            header_text = f"{col.title}\n({col.weight})"
            table.setHorizontalHeaderItem(j, QTableWidgetItem(header_text))
        
        # Set row headers
        for i in range(self.matrix.rows):
            item_name = self.matrix.items.get(i, f"Item {i+1}")
            table.setVerticalHeaderItem(i, QTableWidgetItem(item_name))
        
        # Fill cells with existing values
        for j, col in enumerate(self.matrix.matrix):
            for i, value in enumerate(col.values):
                if value > 0:
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(i, j, item)
                else:
                    table.setItem(i, j, QTableWidgetItem(""))
        
        # Unblock signals
        table.blockSignals(False)
    
    def initialize_default_matrix(self):
        """Initialize matrix with default 2x2 setup"""
        # Add default rows
        self.matrix.insert_row("Option A")
        self.matrix.insert_row("Option B")
        
        # Add default columns
        self.matrix.insert_column("Criterion 1", 0.5)
        self.matrix.insert_column("Criterion 2", 0.5)
        
        # Update display
        self.update_table_display()
    
    def show_results(self):
        """Calculate and display the weighted scores"""
        try:
            scores = self.matrix.compute_scores()
            
            # Create custom styled dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Results")
            dialog.setMinimumWidth(500)
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #1a1d23;
                }
            """)
            
            layout = QVBoxLayout(dialog)
            layout.setSpacing(15)
            layout.setContentsMargins(25, 25, 25, 25)
            
            # Scores container
            scores_frame = QFrame()
            scores_frame.setStyleSheet("""
                QFrame {
                    background-color: #f5f7fa;
                    border: 1px solid #e1e4e8;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            scores_layout = QVBoxLayout(scores_frame)
            scores_layout.setSpacing(10)
            
            # Find best score
            best_idx = max(scores, key=scores.get)
            
            # Add each score
            for i in range(self.matrix.rows):
                item_name = self.matrix.items.get(i, f"Item {i+1}")
                score = scores[i]
                is_best = (i == best_idx)
                
                score_item = QFrame()
                if is_best:
                    score_item.setStyleSheet("""
                        QFrame {
                            background-color: #d4f4dd;
                            border: 2px solid #28a745;
                            border-radius: 6px;
                            padding: 12px;
                        }
                    """)
                else:
                    score_item.setStyleSheet("""
                        QFrame {
                            background-color: #ffffff;
                            border: 1px solid #d1d5da;
                            border-radius: 6px;
                            padding: 12px;
                        }
                    """)
                
                item_layout = QHBoxLayout(score_item)
                item_layout.setContentsMargins(0, 0, 0, 0)
                
                # Item name
                name_label = QLabel(item_name)
                if is_best:
                    name_label.setStyleSheet("""
                        QLabel {
                            font-size: 13pt;
                            font-weight: 600;
                            color: #1e7e34;
                        }
                    """)
                else:
                    name_label.setStyleSheet("""
                        QLabel {
                            font-size: 12pt;
                            font-weight: 500;
                            color: #24292e;
                        }
                    """)
                item_layout.addWidget(name_label)
                
                item_layout.addStretch()
                
                # Score
                score_label = QLabel(f"{score:.1f}")
                if is_best:
                    score_label.setStyleSheet("""
                        QLabel {
                            font-size: 16pt;
                            font-weight: 700;
                            color: #28a745;
                            background-color: #ffffff;
                            padding: 8px 16px;
                            border-radius: 6px;
                        }
                    """)
                else:
                    score_label.setStyleSheet("""
                        QLabel {
                            font-size: 14pt;
                            font-weight: 600;
                            color: #586069;
                            background-color: #f6f8fa;
                            padding: 6px 12px;
                            border-radius: 6px;
                        }
                    """)
                item_layout.addWidget(score_label)
                
                scores_layout.addWidget(score_item)
            
            layout.addWidget(scores_frame)
            
            # Best option label
            best_label = QLabel(f"Best option: {self.matrix.items.get(best_idx, f'Item {best_idx+1}')}")
            best_label.setStyleSheet("""
                QLabel {
                    font-size: 14pt;
                    font-weight: 600;
                    color: #28a745;
                    background-color: #f5f7fa;
                    padding: 12px;
                    border-radius: 8px;
                    border: 2px solid #28a745;
                }
            """)
            best_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(best_label)
            
            # Close button
            close_btn = QPushButton("Close")
            close_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0366d6;
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 24px;
                    font-size: 12pt;
                    font-weight: 600;
                    min-width: 120px;
                }
                QPushButton:hover {
                    background-color: #0256c5;
                }
                QPushButton:pressed {
                    background-color: #024ea4;
                }
            """)
            close_btn.clicked.connect(dialog.accept)
            
            btn_layout = QHBoxLayout()
            btn_layout.addStretch()
            btn_layout.addWidget(close_btn)
            btn_layout.addStretch()
            layout.addLayout(btn_layout)
            
            dialog.exec()
            
        except ValueError as e:
            # Create styled error dialog
            self.show_error_dialog(str(e))
        except Exception as e:
            self.show_error_dialog(f"Could not calculate results: {str(e)}")
    
    def show_error_dialog(self, message):
        """Show a styled error dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Error")
        dialog.setFixedSize(420, 280)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1a1d23;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Message frame
        message_frame = QFrame()
        message_frame.setStyleSheet("""
            QFrame {
                background-color: #2d3339;
                border: 2px solid #dc3545;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        message_layout = QVBoxLayout(message_frame)
        message_layout.setContentsMargins(0, 0, 0, 0)
        
        message_label = QLabel(message)
        message_label.setStyleSheet("""
            QLabel {
                font-size: 13pt;
                color: #f5f7fa;
                line-height: 1.6;
                background-color: transparent;
                border: none;
            }
        """)
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label)
        
        layout.addWidget(message_frame, 1)  # Stretch factor to fill space
        
        # OK button
        ok_btn = QPushButton("OK")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        ok_btn.clicked.connect(dialog.accept)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        dialog.exec()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Create a matrix with default data for standalone testing
    matrix = WeightedMatrix()
    matrix.insert_row("Option A")
    matrix.insert_row("Option B")
    matrix.insert_column("Criterion 1", 0.5)
    matrix.insert_column("Criterion 2", 0.5)

    window = MainWindow(matrix)
    window.show()

    sys.exit(app.exec())