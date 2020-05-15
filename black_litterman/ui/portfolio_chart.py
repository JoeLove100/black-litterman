import math
import pandas as pd
from typing import List
from PySide2 import QtWidgets, QtCore, QtGui
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
                   asset_universe: List[str],
                   *args: pd.Series) -> None:

        asset_universe = [s.replace(" ", "<br>") for s in asset_universe]  # no word wrap for some reason
        bar_series = QtCharts.QBarSeries()
        y_min = 0
        y_max = 0

        for weights in args:

            y_min = min(weights.min() * 100, y_min)
            y_max = max(weights.max() * 100, y_max)

            bar_set = QtCharts.QBarSet(str(weights.name))
            bar_set.append(weights.mul(100).values.tolist())
            bar_series.append(bar_set)

        # configure basic chart
        chart = QtCharts.QChart()
        chart.setTitle("Black-Litterman Asset Allocation")
        title_font = QtGui.QFont()
        title_font.setBold(True)
        chart.setFont(title_font)
        chart.addSeries(bar_series)

        # configure the x axis
        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append(asset_universe)
        chart.createDefaultAxes()
        chart.setAxisX(axis_x)

        # configure the y axis
        axis_y = QtCharts.QValueAxis()
        self._set_y_axis_limits(y_max, y_min, axis_y)
        axis_y.setLabelFormat("%.0f")
        axis_y.setTitleText("Suggested Allocation (%)")
        chart.setAxisY(axis_y)
        bar_series.attachAxis(axis_y)

        # configure chart legend
        chart.legend().setVisible(True)
        chart.legend().setAlignment(QtCore.Qt.AlignBottom)

        self._chart_view.setChart(chart)

    def _set_y_axis_limits(self,
                           y_max: float,
                           y_min: float,
                           axis_y: QtCharts.QValueAxis) -> None:

        y_max_rounded = self._round_axis_limit(y_max)
        y_min_rounded = self._round_axis_limit(y_min)
        intervals = (y_max_rounded - y_min_rounded) // 10 + 1

        axis_y.setMax(y_max_rounded)
        axis_y.setMin(y_min_rounded)
        axis_y.setTickCount(intervals)

    @staticmethod
    def _round_axis_limit(lim: float):

        if lim == 0:
            return 0

        rounded_lim = (math.floor(abs(lim) / 10) + 1) * 10
        if lim < 0:
            return -rounded_lim
        else:
            return rounded_lim

