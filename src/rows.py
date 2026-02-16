import sys
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QLineEdit, QPushButton, QSizePolicy, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ui.scripts.rows_ui import Ui_form


class RowsWindow(QWidget):
    def __init__(self, matrix=None):
        super().__init__()
        
        self.ui = Ui_form()
        self.ui.setupUi(self)
        
        self.matrix = matrix
        self.row_widgets = []
        self.columns_window = None
        
        # Connect buttons
        self.ui.addBtn.clicked.connect(self.add_row_widget)
        self.ui.nextBtn.clicked.connect(self.save_and_close)
        
        # Ensure button hover works by setting attribute
        self.ui.nextBtn.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.ui.addBtn.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        
        # Load existing rows if matrix has them
        if self.matrix and self.matrix.rows > 0:
            for i in range(self.matrix.rows):
                self.add_row_widget()
                item_name = self.matrix.items.get(i, "")
                if item_name:
                    self.row_widgets[i].setText(item_name)
        else:
            # Add initial 2 rows
            self.add_row_widget()
            self.add_row_widget()
        
        # Initial button state check
        self.update_next_button()
    
    def add_row_widget(self):
        """Add a new row input widget"""
        if len(self.row_widgets) >= 8:
            return
        
        # Create row frame
        row_frame = QFrame()
        row_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e1e4e8;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QHBoxLayout(row_frame)
        
        # Item name input
        item_input = QLineEdit()
        item_input.setPlaceholderText(f"Item {len(self.row_widgets) + 1}")
        item_input.setStyleSheet("""
            QLineEdit {
                background-color: #f6f8fa;
                color: #24292e;
                border: 2px solid #d1d5da;
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                selection-background-color: #4a9eff;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #00989b;
                background-color: #ffffff;
            }
        """)
        
        # Delete button
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("ui/icons/delete.png"))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                border-radius: 6px;
                min-width: 42px;
                max-width: 42px;
                min-height: 42px;
                max-height: 42px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        delete_btn.clicked.connect(lambda: self.remove_row_widget(row_frame, item_input))
        
        layout.addWidget(item_input)
        layout.addWidget(delete_btn)
        
        self.ui.itemsLayout.addWidget(row_frame)
        self.row_widgets.append(item_input)
        
        # Connect text change to update button
        item_input.textChanged.connect(self.update_next_button)
        
        self.update_next_button()
    
    def remove_row_widget(self, frame, input_widget):
        """Remove a row widget"""
        if len(self.row_widgets) <= 2:
            return
        
        self.row_widgets.remove(input_widget)
        self.ui.itemsLayout.removeWidget(frame)
        frame.deleteLater()
        
        self.update_next_button()
    
    def update_next_button(self):
        """Enable/disable next button based on valid input"""
        # Check if all rows have text
        filled_count = 0
        has_blank = False
        
        for widget in self.row_widgets:
            text = widget.text().strip()
            if text:
                filled_count += 1
            else:
                has_blank = True
        
        # Enable button only if at least 2 rows are filled and none are blank
        is_valid = filled_count >= 2 and not has_blank
        self.ui.nextBtn.setEnabled(is_valid)
    
    def save_and_close(self):
        """Save rows to matrix and open columns window"""
        if self.matrix:
            current_row_count = self.matrix.rows
            new_row_count = len([w for w in self.row_widgets if w.text().strip()])
            
            for i, widget in enumerate(self.row_widgets):
                text = widget.text().strip()
                if text:
                    if i < current_row_count:
                        # Update existing row
                        self.matrix.update_row(i + 1, text)
                    else:
                        # Insert new row
                        self.matrix.insert_row(text)
            
            # Delete extra rows if we have fewer now
            while self.matrix.rows > new_row_count:
                self.matrix.delete_row(self.matrix.rows)
        
        # Open columns window
        from columns import ColumnsWindow
        self.columns_window = ColumnsWindow(self.matrix)
        self.columns_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = RowsWindow()
    window.show()
    
    sys.exit(app.exec())