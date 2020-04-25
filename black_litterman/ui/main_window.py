from PySide2 import QtWidgets, QtCharts
from black_litterman.ui.view_manager import ViewManager
from black_litterman.ui.portfolio_chart import PortfolioChart


class BlackLittermanApp(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self._create_controls()
        self._initialise_controls()
        self._add_controls_to_layout()
        self._size_layout()

    def _create_controls(self):

        self._main_chart = PortfolioChart()
        self._view_manager = ViewManager({}, ["asset_1", "asset_2", "asset_3", "asset_4"])

    def _initialise_controls(self):

        self._main_chart.draw_chart({"Government Bonds": 0.4, "World Equity": 0.6})

    def _add_controls_to_layout(self):

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self._main_chart, 0, 0, 1, 1)
        layout.addWidget(self._view_manager, 0, 1, 1, 1)

        self.layout = layout
        self.setLayout(self.layout)

    def _size_layout(self):

        self.layout.setColumnStretch(0, 9)
        self.layout.setColumnStretch(0, 1)


if __name__ == "__main__":

    import sys

    app = QtWidgets.QApplication([])
    blw = BlackLittermanApp()
    blw.setWindowTitle("Black Litterman Portfolio Tool")
    blw.resize(750, 500)
    blw.show()
    sys.exit(app.exec_())
