from typing import Dict

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
                   weights: Dict[str, float]) -> None:

        pie_series = QtCharts.QPieSeries()

        for asset_name, asset_weight in weights.items():
            pie_series.append(asset_name, asset_weight)

        chart = QtCharts.QChart()
        chart.addSeries(pie_series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QtCharts.QChart.SeriesAnimations)
        chart.setTitle("Portfolio Allocation")
        chart.legend().setVisible(True)
        self._chart_view.setChart(chart)


if __name__ == "__main__":

    from PySide2 import QtGui
    import sys

    app = QtWidgets.QApplication([])
    app.setFont(QtGui.QFont("Arial", 10))

    c = PortfolioChart()
    c.draw_chart({"Government Bonds": 0.4, "World Equity": 0.6})
    c.show()

    sys.exit(app.exec_())
