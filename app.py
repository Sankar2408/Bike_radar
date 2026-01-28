import sys
from PySide6.QtWidgets import QApplication
from backend.grid_backend import GridBackend
from frontend.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    backend = GridBackend()
    window = MainWindow(backend)

    window.resize(900, 600)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
