import sys
from PyQt6.QtWidgets import QApplication, QWidget
from ui.scripts.rows_ui import Ui_form


class RowsWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_form()
        self.ui.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = RowsWindow()
    window.show()
    
    sys.exit(app.exec())