import sys
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from ui.scripts.columns_ui import Ui_form
from utils import resource_path


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

        # Add the icon of "addBtn" using resource_path
        self.ui.addBtn.setIcon(QIcon(resource_path("ui/icons/add.png")))
        self.ui.addBtn.setIconSize(QSize(25, 25))
        
        # Load existing columns if matrix has them
        if self.matrix and self.matrix.cols > 0:
            for col in self.matrix.matrix:
                self.add_column_widget()
                idx = len(self.column_widgets) - 1
                # Only set text if it's not a default "Criterion X" name
                if not col.title.startswith("Criterion "):
                    self.column_widgets[idx][0].setText(col.title)
                weight_str = f"{round(col.weight, 2)}"
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
                background-color: #fff;
                border: none;
                border-radius: 8px;
                padding: 12px;
                margin: 2px 0px 2px 0
            }
        """)
        
        layout = QHBoxLayout(col_frame)
        
        # Criterion name input
        name_input = QLineEdit()
        name_input.setPlaceholderText(f"Criterion {len(self.column_widgets) + 1}")
        name_input.setStyleSheet("""
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
        
        # Weight label
        weight_label = QLabel("Weight")
        weight_label.setStyleSheet("""
            QLabel {
                color: #24292e;
                font-size: 11pt;
                font-weight: 600;
                padding: 0 10 0 10;
                background-color: #fff;
                border: 3px solid #e1e4e8;
                margin: 0;
            }
        """)
        weight_label.setFixedHeight(50)
        weight_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Weight input (QLineEdit with "0." prefix)
        weight_input = QLineEdit()
        weight_input.setText("0.50")
        weight_input.setMaxLength(4)  # "0.XX" format
        weight_input.setStyleSheet("""
            QLineEdit {
                background-color: #f6f8fa;
                color: #24292e;
                border: 2px solid #d1d5da;
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                min-width: 90px;
                selection-background-color: #4a9eff;
                selection-color: #ffffff;
            }
            QLineEdit:focus {
                border: 2px solid #00989b;
                background-color: #ffffff;
            }
        """)
        
        # Connect text change to validate and update
        weight_input.textChanged.connect(lambda: self.validate_weight_input(weight_input))
        weight_input.textChanged.connect(self.update_next_button)
        
        # Delete button
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(resource_path("ui/icons/delete.png")))
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                border-radius: 6px;
                min-width: 42px;
                max-width: 42px;
                min-height: 42px;
                max-height: 42px;
                margin-left: 10px
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
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
        
        # Check the rest
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
        # Check if all columns have actual text
        filled_count = 0
        has_blank = False
        
        for name, _ in self.column_widgets:
            text = name.text().strip()
            # Only count if user actually entered text
            if text:
                filled_count += 1
            else:
                has_blank = True
        
        total_weight = sum(self.get_weight_value(weight) for _, weight in self.column_widgets)
        
        # Enable if at least 2 columns with actual text, none are blank, and weights sum to 1.0
        is_valid = filled_count >= 2 and not has_blank and abs(total_weight - 1.0) < 0.01
        self.ui.nextBtn.setEnabled(is_valid)
        
        # Update weight label color based on correctness
        if abs(total_weight - 1.0) < 0.01:
            weight_color = "#51e14c"
        else:
            weight_color = "#e24646"
        
        # Update the weightLabel with current total
        self.ui.weightLabel.setText(f"Current total: {round(total_weight, 2)}")
        self.ui.weightLabel.setStyleSheet(f"""
            QLabel {{
                color: {weight_color};
                font-size: 14pt;
                font-weight: 700;
            }}
        """)
    
    def save_and_close(self):
        """Save columns to matrix and open matrix window"""
        if self.matrix:
            current_col_count = self.matrix.cols
            new_col_count = len([w for w, _ in self.column_widgets if w.text().strip()])
            
            # Update existing columns
            for i, (name_input, weight_input) in enumerate(self.column_widgets):
                text = name_input.text().strip()
                weight = self.get_weight_value(weight_input)
                if text:  # Only save if there's actual text
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