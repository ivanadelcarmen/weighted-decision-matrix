import sys
import os


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.
    When frozen, PyInstaller creates a temp folder and stores path in _MEIPASS.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # In development, use the src directory as base
        base_path = os.path.dirname(__file__)
    
    full_path = os.path.join(base_path, relative_path)
    return full_path
