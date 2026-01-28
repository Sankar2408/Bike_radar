import numpy as np
from PySide6.QtCore import QObject, Signal, Slot


class GridBackend(QObject):
    # MUST be object, not np.ndarray
    grid_ready = Signal(object)

    @Slot(dict)
    def create_grid(self, cfg):
        try:
            x_min = cfg["x_min"]
            x_max = cfg["x_max"]
            y_min = cfg["y_min"]
            y_max = cfg["y_max"]
            dx = cfg["dx"]
            dy = cfg["dy"]

            # Validation
            if dx <= 0 or dy <= 0:
                print("Invalid cell size")
                return
            if x_max <= x_min or y_max <= y_min:
                print("Invalid range")
                return

            nx = int((x_max - x_min) / dx)
            ny = int((y_max - y_min) / dy)

            if nx <= 0 or ny <= 0:
                print("Invalid grid size")
                return

            # Y rows, X columns
            grid = np.zeros((ny, nx), dtype=np.float32)

            self.grid_ready.emit(grid)

        except Exception as e:
            print("Backend error:", e)
