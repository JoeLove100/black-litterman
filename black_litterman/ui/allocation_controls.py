from PySide2 import QtWidgets
from typing import List
from black_litterman.domain.views import ViewAllocation


class AllocationControlAbsolute(QtWidgets.QWidget):

    def __init__(self,
                 allocation: ViewAllocation,
                 asset_universe: List[str]):

        super().__init__()
        self._create_controls()
        self._initialise_controls(allocation, asset_universe)
        self._add_controls_to_layout()
        self._size_layout()

    def _create_controls(self) -> None:

        self._long_asset_combo = QtWidgets.QComboBox()
        self._long_asset_combo.setMinimumHeight(30)

    def _initialise_controls(self,
                             allocation: ViewAllocation,
                             asset_universe: List[str]) -> None:

        self._long_asset_combo.addItems(asset_universe)
        self._long_asset_combo.setCurrentText(allocation.long_asset)

    def _add_controls_to_layout(self):

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # add main controls
        self.layout.addWidget(self._long_asset_combo, 0, 1)

        # add label controls
        self.layout.addWidget(QtWidgets.QLabel("Long asset:"), 0, 0)
        self.layout.addWidget(QtWidgets.QLabel(""), 1, 0)

    def _size_layout(self):

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 10)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 10)

    def get_allocation(self):
        return ViewAllocation(self._long_asset_combo.currentText(), None)


class AllocationControlRelative(QtWidgets.QWidget):

    def __init__(self,
                 allocation: ViewAllocation,
                 asset_universe: List[str]):

        super().__init__()
        self._create_controls()
        self._initialise_controls(allocation, asset_universe)
        self._add_controls_to_layout()
        self._size_layout()

    def _create_controls(self) -> None:

        self._long_asset_combo = QtWidgets.QComboBox()
        self._long_asset_combo.setMinimumHeight(30)

        self._short_asset_combo = QtWidgets.QComboBox()
        self._short_asset_combo.setMinimumHeight(30)

    def _initialise_controls(self,
                             allocation: ViewAllocation,
                             asset_universe: List[str]) -> None:

        self._long_asset_combo.addItems(asset_universe)
        self._long_asset_combo.setCurrentText(allocation.long_asset)

        self._short_asset_combo.addItems(asset_universe)
        self._short_asset_combo.setCurrentIndex(0)

    def _add_controls_to_layout(self):

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # add main controls
        self.layout.addWidget(self._long_asset_combo, 0, 1)
        self.layout.addWidget(self._short_asset_combo, 1, 1)

        # add label controls
        self.layout.addWidget(QtWidgets.QLabel("Long asset:"), 0, 0)
        self.layout.addWidget(QtWidgets.QLabel("Short asset:"), 1, 0)
        self.layout.addWidget(QtWidgets.QLabel(""), 2, 0)

    def _size_layout(self):

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 10)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 10)

    def get_allocation(self):
        return ViewAllocation(self._long_asset_combo.currentText(),
                              self._short_asset_combo.currentText())


if __name__ == "__main__":

    import sys
    from PySide2 import QtGui

    app = QtWidgets.QApplication([])
    app.setFont(QtGui.QFont("Arial", 10))

    v = ViewAllocation("asset_1", "asset_2")
    au = ["asset_1", "asset_2", "asset_3", "asset_4"]
    widget = AllocationControlRelative(v, au)
    widget.setWindowTitle("Add new view")
    widget.resize(350, 200)
    widget.show()

    sys.exit(app.exec_())
