import sys
from PyQt6.QtWidgets import QApplication
from core.weighted_matrix import WeightedMatrix
from rows import RowsWindow


def main():
    app = QApplication(sys.argv)
    
    # Create shared matrix instance
    matrix = WeightedMatrix()
    
    # Start with rows window
    window = RowsWindow(matrix)
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
