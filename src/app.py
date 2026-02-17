import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtGui import QIcon

from core.weighted_matrix import WeightedMatrix
from rows import RowsWindow
from columns import ColumnsWindow
from matrix import MainWindow as MatrixWindow

BASE_DIR = os.path.dirname(__file__)


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Weighted Decision Matrix")
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "ui", "icons", "grid.png")))
        self.resize(1100, 750)
        
        # Create shared matrix instance
        self.matrix = WeightedMatrix()
        
        # Create stacked widget to hold all screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create all three screens
        self.rows_screen = RowsWindow(self.matrix)
        self.columns_screen = ColumnsWindow(self.matrix)
        self.matrix_screen = MatrixWindow(self.matrix)
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.rows_screen)
        self.stacked_widget.addWidget(self.columns_screen)
        self.stacked_widget.addWidget(self.matrix_screen)
        
        # Connect navigation signals
        self.setup_navigation()
        
        # Start with rows screen
        self.show_rows()
        
        # Center the window on screen
        self.center_on_screen()
    
    def setup_navigation(self):
        """Setup navigation between screens"""
        # Rows -> Columns
        self.rows_screen.ui.nextBtn.clicked.disconnect()
        self.rows_screen.ui.nextBtn.clicked.connect(self.rows_to_columns)
        
        # Columns -> Matrix
        self.columns_screen.ui.nextBtn.clicked.disconnect()
        self.columns_screen.ui.nextBtn.clicked.connect(self.columns_to_matrix)
        
        # Columns -> Rows (back button)
        self.columns_screen.ui.backBtn.clicked.disconnect()
        self.columns_screen.ui.backBtn.clicked.connect(self.columns_to_rows)
        
        # Matrix -> Rows (modify button)
        self.matrix_screen.ui.modifyBtn.clicked.disconnect()
        self.matrix_screen.ui.modifyBtn.clicked.connect(self.matrix_to_rows)
    
    def center_on_screen(self):
        """Center the window on the screen"""
        screen = self.screen().availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def show_rows(self):
        """Show rows screen"""
        self.stacked_widget.setCurrentWidget(self.rows_screen)
    
    def show_columns(self):
        """Show columns screen"""
        self.stacked_widget.setCurrentWidget(self.columns_screen)
    
    def show_matrix(self):
        """Show matrix screen"""
        self.stacked_widget.setCurrentWidget(self.matrix_screen)
    
    def rows_to_columns(self):
        """Navigate from rows to columns"""
        # Save rows data
        self.rows_screen.save_and_close = self.save_rows_and_continue
        self.rows_screen.save_and_close()
    
    def save_rows_and_continue(self):
        """Save rows and navigate to columns"""
        current_row_count = self.matrix.rows
        new_row_count = len([w for w in self.rows_screen.row_widgets if w.text().strip()])
        
        # Update existing rows
        for i, widget in enumerate(self.rows_screen.row_widgets):
            text = widget.text().strip()
            if text:
                if i < current_row_count:
                    self.matrix.update_row(i + 1, text)
                else:
                    self.matrix.insert_row(text)
        
        # Delete extra rows if we have fewer now
        while self.matrix.rows > new_row_count:
            self.matrix.delete_row(self.matrix.rows)
        
        # Reload columns screen with updated data
        self.reload_columns_screen()
        self.show_columns()
    
    def columns_to_rows(self):
        """Navigate from columns back to rows"""
        self.reload_rows_screen()
        self.show_rows()
    
    def columns_to_matrix(self):
        """Navigate from columns to matrix"""
        # Save columns data
        self.columns_screen.save_and_close = self.save_columns_and_continue
        self.columns_screen.save_and_close()
    
    def save_columns_and_continue(self):
        """Save columns and navigate to matrix"""
        current_col_count = self.matrix.cols
        new_col_count = len([w for w, _ in self.columns_screen.column_widgets if w.text().strip()])
        
        # Update existing columns
        for i, (name_input, weight_input) in enumerate(self.columns_screen.column_widgets):
            text = name_input.text().strip()
            # Use placeholder if no text entered
            if not text:
                text = name_input.placeholderText()
            weight = self.columns_screen.get_weight_value(weight_input)
            if text:
                if i < current_col_count:
                    self.matrix.update_column_attr(i + 1, text)
                    self.matrix.update_column_weight(i + 1, weight)
                else:
                    self.matrix.insert_column(text, weight)
        
        # Delete extra columns if we have fewer now
        while self.matrix.cols > new_col_count:
            self.matrix.delete_column(self.matrix.cols)
        
        # Update matrix display
        self.matrix_screen.update_table_display()
        self.show_matrix()
    
    def matrix_to_rows(self):
        """Navigate from matrix back to rows"""
        self.reload_rows_screen()
        self.show_rows()
    
    def reload_rows_screen(self):
        """Reload rows screen with current matrix data"""
        # Clear existing widgets
        for widget in self.rows_screen.row_widgets[:]:
            self.rows_screen.row_widgets.remove(widget)
            # Find and remove the frame containing this widget
            for i in range(self.rows_screen.ui.itemsLayout.count()):
                item = self.rows_screen.ui.itemsLayout.itemAt(i)
                if item and item.widget():
                    item.widget().deleteLater()
        
        # Add rows from matrix
        if self.matrix.rows > 0:
            for i in range(self.matrix.rows):
                self.rows_screen.add_row_widget()
                item_name = self.matrix.items.get(i, "")
                if item_name:
                    self.rows_screen.row_widgets[i].setText(item_name)
        else:
            # Add default 2 rows
            self.rows_screen.add_row_widget()
            self.rows_screen.add_row_widget()
    
    def reload_columns_screen(self):
        """Reload columns screen with current matrix data"""
        # Clear existing widgets
        for name_input, weight_input in self.columns_screen.column_widgets[:]:
            self.columns_screen.column_widgets.remove((name_input, weight_input))
            # Find and remove the frame
            for i in range(self.columns_screen.ui.criteriaLayout.count()):
                item = self.columns_screen.ui.criteriaLayout.itemAt(i)
                if item and item.widget():
                    item.widget().deleteLater()
        
        # Add columns from matrix
        if self.matrix.cols > 0:
            for col in self.matrix.matrix:
                self.columns_screen.add_column_widget()
                idx = len(self.columns_screen.column_widgets) - 1
                # Only set text if it's not a default "Criterion X" name
                if not col.title.startswith("Criterion "):
                    self.columns_screen.column_widgets[idx][0].setText(col.title)
                weight_str = f"{col.weight:.2f}"
                self.columns_screen.column_widgets[idx][1].setText(weight_str)
        else:
            # Add default 2 columns
            self.columns_screen.add_column_widget()
            self.columns_screen.add_column_widget()


def main():
    app = QApplication(sys.argv)
    
    window = MainApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
