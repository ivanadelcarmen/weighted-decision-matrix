import sys
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ui.scripts.columns_ui import Ui_form


class ColumnsWindow(QWidget):
    def __init__(self, matrix=None):
        super().__init__()
        
        self.ui = Ui_form()
        self.ui.setupUi(self)
        
        self.matrix = matrix
        self.column_widgets = []
        self.matrix_window = None
        
        # Connect buttons
        self.ui.addBtn.clicked.connect(self.add_column_widget)
        self.ui.nextBtn.clicked.connect(self.save_and_close)
        self.ui.backBtn.clicked.connect(self.go_back)
        
        # Ensure button hover works by setting attribute
        self.ui.nextBtn.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.ui.backBtn.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.ui.addBtn.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        
        # Load existing columns if matrix has them
        if self.matrix and self.matrix.cols > 0:
            for col in self.matrix.matrix:
                self.add_column_widget()
                idx = len(self.column_widgets) - 1
                self.column_widgets[idx][0].setText(col.title)

                weight_str = f"{round(col.weight, 2)}" # Format weight as "0.XX"
                self.column_widgets[idx][1].setText(weight_str)
        else:
            # Add initial 2 columns
            self.add_column_widget()
            self.add_column_widget()
        
        # Initial button state check
        self.update_next_button()
    
    def add_column_widget(self):
        """Add a new column input widget"""
        if len(self.column_widgets) >= 8:
            return
        
        # Create column frame
        col_frame = QFrame()
        col_frame.setStyleSheet("""
            QFrame {
                background-color: #FAFAF7;
                border-radius: 6px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(col_frame)
        
        # Criterion name input
        name_input = QLineEdit()
        name_input.setPlaceholderText(f"Criterion {len(self.column_widgets) + 1}")
        name_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #2A3133;
                border: 2px solid #89b3af;
                border-radius: 4px;
                padding: 8px;
                font-size: 12pt;
                selection-background-color: #7dd3c0;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #00989b;
            }
        """)
        
        # Weight label
        weight_label = QLabel("Weight:")
        weight_label.setStyleSheet("color: #2A3133; font-size: 11pt;")
        
        # Weight input (QLineEdit with "0." prefix)
        weight_input = QLineEdit()
        weight_input.setText("0.50")
        weight_input.setMaxLength(4)  # "0.XX" format
        weight_input.setStyleSheet("""
            QLineEdit {
                background-color: #ffffff;
                color: #2A3133;
                border: 2px solid #89b3af;
                border-radius: 4px;
                padding: 8px;
                font-size: 12pt;
                min-width: 80px;
                selection-background-color: #7dd3c0;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #00989b;
            }
        """)
        
        # Connect text change to validate and update
        weight_input.textChanged.connect(lambda: self.validate_weight_input(weight_input))
        weight_input.textChanged.connect(self.update_next_button)
        
        # Delete button
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("ui/icons/delete.png"))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                border-radius: 4px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }
            QPushButton:hover {
                background-color: #e57373;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
        """)
        delete_btn.clicked.connect(lambda: self.remove_column_widget(col_frame, name_input, weight_input))
        
        layout.addWidget(name_input, 3)
        layout.addWidget(weight_label)
        layout.addWidget(weight_input, 1)
        layout.addWidget(delete_btn)
        
        self.ui.criteriaLayout.addWidget(col_frame)
        self.column_widgets.append((name_input, weight_input))
        
        # Connect text change to update button
        name_input.textChanged.connect(self.update_next_button)
        
        self.update_next_button()
    
    def remove_column_widget(self, frame, name_input, weight_input):
        """Remove a column widget"""
        if len(self.column_widgets) <= 2:
            return
        
        self.column_widgets.remove((name_input, weight_input))
        self.ui.criteriaLayout.removeWidget(frame)
        frame.deleteLater()
        
        self.update_next_button()
    
    def validate_weight_input(self, weight_input):
        """Ensure weight input always starts with '0.' and contains valid decimals"""
        text = weight_input.text()
        cursor_pos = weight_input.cursorPosition()
        
        # If text is empty or doesn't start with "0.", fix it
        if not text:
            weight_input.setText("0.")
            weight_input.setCursorPosition(2)
            return
        
        if not text.startswith("0."):
            weight_input.setText("0.")
            weight_input.setCursorPosition(2)
            return
        
        # Remove "0." prefix to check the rest
        decimal_part = text[2:]
        
        # Only allow digits in decimal part
        if decimal_part and not decimal_part.isdigit():
            # Remove non-digit characters
            decimal_part = ''.join(c for c in decimal_part if c.isdigit())
            weight_input.setText("0." + decimal_part)
            weight_input.setCursorPosition(min(cursor_pos, len(weight_input.text())))
            return
        
        # Limit to 2 decimal places
        if len(decimal_part) > 2:
            weight_input.setText("0." + decimal_part[:2])
            weight_input.setCursorPosition(4)
    
    def get_weight_value(self, weight_input):
        """Get float value from weight input"""
        try:
            text = weight_input.text()
            if text.startswith("0."):
                return float(text)
            return 0.0
        except:
            return 0.0
    
    def update_next_button(self):
        """Enable/disable next button based on valid input"""
        # Check if all columns have text
        filled_count = 0
        has_blank = False
        
        for name, weight in self.column_widgets:
            text = name.text().strip()
            if text:
                filled_count += 1
            else:
                has_blank = True
        
        total_weight = sum(self.get_weight_value(weight) for _, weight in self.column_widgets)
        
        # Enable if at least 2 valid columns, none are blank, and weights sum to 1.0
        is_valid = filled_count >= 2 and not has_blank and abs(total_weight - 1.0) < 0.01
        self.ui.nextBtn.setEnabled(is_valid)
        
        # Update instruction label to show current weight sum
        self.ui.instructionLabel.setText(
            f"Add criteria with weights that sum to 1.0 (minimum 2, maximum 8)\n"
            f"Current total: {round(total_weight, 2)}"
        )
    
    def save_and_close(self):
        """Save columns to matrix and open matrix window"""
        if self.matrix:
            current_col_count = self.matrix.cols
            new_col_count = len([w for w, _ in self.column_widgets if w.text().strip()])
            
            # Update existing columns
            for i, (name_input, weight_input) in enumerate(self.column_widgets):
                text = name_input.text().strip()
                weight = self.get_weight_value(weight_input)
                if text:
                    if i < current_col_count:
                        # Update existing column
                        self.matrix.update_column_attr(i + 1, text)
                        self.matrix.update_column_weight(i + 1, weight)
                    else:
                        # Insert new column
                        self.matrix.insert_column(text, weight)
            
            # Delete extra columns if we have fewer now
            while self.matrix.cols > new_col_count:
                self.matrix.delete_column(self.matrix.cols)
        
        # Open matrix window
        from matrix import MainWindow
        self.matrix_window = MainWindow(self.matrix)
        self.matrix_window.show()
        self.close()
    
    def go_back(self):
        """Go back to rows window"""
        from rows import RowsWindow
        rows_window = RowsWindow(self.matrix)
        rows_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = ColumnsWindow()
    window.show()
    
    sys.exit(app.exec())