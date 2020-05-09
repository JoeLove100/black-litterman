import pandas as pd
from typing import Dict, List
from PySide2 import QtWidgets
from PySide2.QtCharts import QtCharts
from black_litterman.constants import Weights


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
                   asset_universe: List[str],
                   *args: pd.Series) -> None:

        asset_universe = [s.replace(" ", "<br>") for s in asset_universe]  # no word wrap for some reason
        bar_series = QtCharts.QBarSeries()
        for weights in args:

            bar_set = QtCharts.QBarSet(str(weights.name))
            bar_set.append(weights.mul(100).values.tolist())
            bar_series.append(bar_set)

        chart = QtCharts.QChart()
        chart.addSeries(bar_series)
        bar_series.setLabelsFormat('{:.0%}')

        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append(asset_universe)
        chart.createDefaultAxes()
        chart.setAxisX(axis_x)

        axis_y = QtCharts.QValueAxis()
        axis_y.setMax(50)
        axis_y.setMin(0)
        axis_y.setTickCount(6)
        axis_y.setLabelFormat("%.0f")
        chart.setAxisY(axis_y)
        bar_series.attachAxis(axis_y)

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
