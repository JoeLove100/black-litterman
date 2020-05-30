import math
import pandas as pd
from typing import List, Optional
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCharts import QtCharts
from black_litterman.ui.chart_settings_control import ChartTypes


class PortfolioChart(QtWidgets.QWidget):

    def __init__(self):

        super().__init__()
        self._create_controls()
        self._add_controls_to_layout()

    def _create_controls(self) -> None:

        self._weights_chart_view = QtCharts.QChartView()
        self._returns_chart_view = QtCharts.QChartView()

    def _add_controls_to_layout(self) -> None:

        self._chart_stack = QtWidgets.QStackedLayout()
        self._chart_stack.addWidget(self._weights_chart_view)
        self._chart_stack.addWidget(self._returns_chart_view)

        self._layout = QtWidgets.QGridLayout()
        self._layout.addLayout(self._chart_stack, 0, 0)
        self.setLayout(self._layout)

    def select_chart(self,
                     selected_chart_type: str) -> None:

        selected_index = self._get_index_for_chart_type(selected_chart_type)
        self._chart_stack.setCurrentIndex(selected_index)

    def draw_charts(self,
                    asset_universe: List[str],
                    implied_returns: pd.Series,
                    selected_chart_type: Optional[str] = ChartTypes.WEIGHTS,
                    *args: pd.Series) -> None:

        # asset_universe = [s.replace(" ", "<br>") for s in asset_universe]  # no word wrap so add line break
        self._set_weights_chart(asset_universe, *args)
        self._set_returns_chart(asset_universe, implied_returns)
        self.select_chart(selected_chart_type)

    def _set_weights_chart(self,
                           asset_universe: List[str],
                           *args: pd.Series) -> None:

        bar_series = QtCharts.QBarSeries()
        y_min = 0
        y_max = 0

        for weights in args:

            weights = weights.reindex(asset_universe)
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
        axis_x.append([s.replace(" ", "<br>") for s in asset_universe])
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

        self._weights_chart_view.setChart(chart)

    def _set_returns_chart(self,
                           asset_universe: List[str],
                           implied_returns: pd.Series) -> None:

        implied_returns = implied_returns.reindex(asset_universe)
        bar_series = QtCharts.QBarSeries()
        bar_set = QtCharts.QBarSet("Returns")
        bar_set.append(implied_returns.mul(100).values.tolist())
        bar_series.append(bar_set)

        # configure basic chart
        chart = QtCharts.QChart()
        chart.setTitle("Market Implied Expected Returns")
        title_font = QtGui.QFont()
        title_font.setBold(True)
        chart.setFont(title_font)
        chart.addSeries(bar_series)

        # configure the x axis
        axis_x = QtCharts.QBarCategoryAxis()
        axis_x.append([s.replace(" ", "<br>") for s in asset_universe])
        chart.createDefaultAxes()
        chart.setAxisX(axis_x)

        # configure the y axis
        y_min = implied_returns.min() * 100
        y_max = implied_returns.max() * 100
        axis_y = QtCharts.QValueAxis()
        self._set_y_axis_limits(y_max, y_min, axis_y, 2)
        axis_y.setLabelFormat("%.0f")
        axis_y.setTitleText("Expected Return (%pa)")
        chart.setAxisY(axis_y)
        bar_series.attachAxis(axis_y)

        self._returns_chart_view.setChart(chart)

    def _set_y_axis_limits(self,
                           y_max: float,
                           y_min: float,
                           axis_y: QtCharts.QValueAxis,
                           round_to: int = 10) -> None:

        y_max_rounded = self._round_axis_limit(y_max, round_to)
        y_min_rounded = self._round_axis_limit(y_min, round_to)
        intervals = (y_max_rounded - y_min_rounded) // round_to + 1

        axis_y.setMax(y_max_rounded)
        axis_y.setMin(y_min_rounded)
        axis_y.setTickCount(intervals)

    @staticmethod
    def _round_axis_limit(lim: float,
                          round_to: int = 10):

        if lim == 0:
            return 0

        rounded_lim = (math.floor(abs(lim) / round_to) + 1) * round_to
        if lim < 0:
            return -rounded_lim
        else:
            return rounded_lim

    @staticmethod
    def _get_index_for_chart_type(chart_type: str):
        """
        convert the chart type to the index
        of the stacked chart
        """

        if chart_type == ChartTypes.WEIGHTS:
            return 0
        elif chart_type == ChartTypes.RETURNS:
            return 1
        else:
            raise ValueError(f"Unrecognised chart type {chart_type}")
