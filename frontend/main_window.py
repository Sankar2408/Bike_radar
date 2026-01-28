from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QRadioButton, QGroupBox,
    QLabel, QDoubleSpinBox
)
import pyqtgraph as pg


class MainWindow(QWidget):
    def __init__(self, backend):
        super().__init__()

        self.backend = backend
        self.setWindowTitle("Bike Radar Grid Setup")

        self._build_ui()

        # Backend → frontend
        self.backend.grid_ready.connect(self.update_grid)

    # -------------------------------------------------
    # UI BUILD
    # -------------------------------------------------
    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(6)

        # ========== MODE ==========
        mode_box = QGroupBox("Mode")
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(20)

        self.auto_btn = QRadioButton("Auto")
        self.manual_btn = QRadioButton("Manual")
        self.manual_btn.setChecked(True)

        mode_layout.addWidget(self.auto_btn)
        mode_layout.addWidget(self.manual_btn)
        mode_layout.addStretch(1)

        mode_box.setLayout(mode_layout)
        main_layout.addWidget(mode_box, stretch=0)

        # ========== GRID PARAMETERS ==========
        self.param_box = QGroupBox("Grid Parameters (Manual)")
        param_layout = QVBoxLayout()
        param_layout.setSpacing(4)

        self.xmin = self._spin("X Min (deg)", param_layout, -11.0)
        self.xmax = self._spin("X Max (deg)", param_layout, 11.0)
        self.ymin = self._spin("Y Min (m)", param_layout, 0.0)
        self.ymax = self._spin("Y Max (m)", param_layout, 120.0)
        self.dx   = self._spin("Cell Size X (deg)", param_layout, 1.0)
        self.dy   = self._spin("Cell Size Y (m)", param_layout, 5.0)

        self.param_box.setLayout(param_layout)
        main_layout.addWidget(self.param_box, stretch=0)

        self.manual_btn.toggled.connect(self.param_box.setEnabled)

        # ========== CREATE GRID ==========
        self.create_btn = QPushButton("Create Grid")
        self.create_btn.setFixedHeight(28)
        self.create_btn.clicked.connect(self.on_create_grid)
        main_layout.addWidget(self.create_btn, stretch=0)

        # ========== PLOT ==========
        self.plot = pg.PlotWidget()
        self.plot.setBackground('k')
        self.plot.setAspectLocked(False)
        self.plot.showGrid(x=True, y=True, alpha=0.3)

        # 🔒 Disable auto scaling & mouse interaction
        self.plot.enableAutoRange(x=False, y=False)
        self.plot.setMouseEnabled(x=False, y=False)

        # Remove margins → bigger plot
        self.plot.getPlotItem().layout.setContentsMargins(0, 0, 0, 0)

        self.image = pg.ImageItem()
        self.plot.addItem(self.image)

        self.plot.setLabel("bottom", "Angle (deg)")
        self.plot.setLabel("left", "Range (m)")

        main_layout.addWidget(self.plot, stretch=1)

    # -------------------------------------------------
    # SPIN BOX HELPER
    # -------------------------------------------------
    def _spin(self, label, layout, default):
        row = QHBoxLayout()
        row.setSpacing(10)

        row.addWidget(QLabel(label))

        spin = QDoubleSpinBox()
        spin.setDecimals(2)
        spin.setRange(-1000.0, 1000.0)
        spin.setValue(default)
        spin.setFixedWidth(120)

        row.addStretch(1)
        row.addWidget(spin)

        layout.addLayout(row)
        return spin

    # -------------------------------------------------
    # BUTTON HANDLER
    # -------------------------------------------------
    def on_create_grid(self):
        cfg = {
            "x_min": self.xmin.value(),
            "x_max": self.xmax.value(),
            "y_min": self.ymin.value(),
            "y_max": self.ymax.value(),
            "dx": self.dx.value(),
            "dy": self.dy.value(),
            "mode": "manual" if self.manual_btn.isChecked() else "auto"
        }

        self.backend.create_grid(cfg)

    # -------------------------------------------------
    # UPDATE PLOT (AXIS LOCKED)
    # -------------------------------------------------
    def update_grid(self, grid):
        if grid is None or grid.size == 0:
            return

        x_min = self.xmin.value()
        x_max = self.xmax.value()
        y_min = self.ymin.value()
        y_max = self.ymax.value()

        # Update image
        self.image.setImage(grid.T, autoLevels=True)

        # Map grid → real-world
        self.image.setRect(
            x_min,
            y_min,
            x_max - x_min,
            y_max - y_min
        )

        # 🔒 FIX AXIS RANGE PERMANENTLY
        self.plot.setXRange(x_min, x_max, padding=0)
        self.plot.setYRange(y_min, y_max, padding=0)
