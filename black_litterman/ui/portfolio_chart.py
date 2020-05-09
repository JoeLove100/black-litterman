from typing import Dict, List
from PySide2 import QtWidgets
from PySide2.QtCharts import QtCharts


class PortfolioChart(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()
        self._create_controls()
        self._add_controls_to_layout()

    def _create_controls(self) -> None:

        self._chart_view = QtCharts.QChartView()

    def _add_controls_to_layout(self) -> None:

        self._layout = QtWidgets.QGridLayout()
        self._layout.addWidget(self._chart_view)
        self.setLayout(self._layout)

    def draw_chart(self,
                   all_weights: Dict[str, Dict[str, float]],
                   asset_universe: List[str]) -> None:

        bar_series = QtCharts.QBarSeries()
        for name, weights in all_weights.items():

            bar_set = QtCharts.QBarSet(name)
            bar_set.append(weights.values())
            bar_series.append(bar_set)

        chart = QtCharts.QChart()
        chart.addSeries(bar_series)

        axis = QtCharts.QBarCategoryAxis()
        axis.append(asset_universe)
        chart.createDefaultAxes()
        chart.setAxisX(axis)

        chart.legend().setVisible(True)

        self._chart_view.setChart(chart)


if __name__ == "__main__":

    from PySide2 import QtGui
    import sys

    app = QtWidgets.QApplication([])
    app.setFont(QtGui.QFont("Arial", 10))

    c = PortfolioChart()
    c.draw_chart({"market weights": {"Government Bonds": 0.4, "World Equity": 0.6}})
    c.show()

    sys.exit(app.exec_())
