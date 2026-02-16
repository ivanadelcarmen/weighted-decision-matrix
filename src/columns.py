import sys
from PyQt6.QtWidgets import QApplication, QWidget
from ui.scripts.columns_ui import Ui_form


class ColumnsWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.ui = Ui_form()
        self.ui.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    window = ColumnsWindow()
    window.show()
    
    sys.exit(app.exec())