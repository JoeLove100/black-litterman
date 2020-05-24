import os
import json
from PySide2 import QtWidgets
from black_litterman.ui.view_manager import ViewManager
from black_litterman.ui.portfolio_chart import PortfolioChart
from black_litterman.ui.chart_settings_control import ChartSettingsControl
from black_litterman.domain.config_handling import ConfigHandler
from black_litterman.ui.fonts import FontHelper


class BlackLittermanApp(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self._set_engine_from_config()
        self._create_controls()
        self._initialise_controls()
        self._add_event_handlers()
        self._add_controls_to_layout()
        self._size_layout()

    def _set_engine_from_config(self) -> None:

        config_path = os.path.abspath(os.path.dirname(__file__))
        config_handler = ConfigHandler(config_path)
        self._engine = config_handler.build_engine_from_config()

    def _create_controls(self):
        self._main_chart = PortfolioChart()
        self._view_manager = ViewManager({}, self._engine.get_asset_universe())
        self._chart_settings_control = ChartSettingsControl(*self._engine.get_dates())
        self._view_manager.setMaximumWidth(300)
        self._view_manager.setMinimumWidth(300)

    def _initialise_controls(self):
        self._plot_chart()

    def _add_event_handlers(self):

        self._view_manager.view_changed.connect(self._plot_chart)
        self._chart_settings_control.dates_changed.connect(self._plot_chart)
        self._chart_settings_control.chart_type_changed.connect(self._change_chart_type)

    def _add_controls_to_layout(self):
        layout = QtWidgets.QGridLayout()
        title_label = QtWidgets.QLabel("Black Litterman Asset Allocation Tool")
        title_label.setFont(FontHelper.get_title_font())

        layout.addWidget(title_label, 0, 0, 1, 1)
        layout.addWidget(self._main_chart, 1, 0, 1, 1)
        layout.addWidget(self._view_manager, 1, 1, 1, 1)
        layout.addWidget(self._chart_settings_control, 2, 0, 2, 1)

        self.layout = layout
        self.setLayout(self.layout)

    def _size_layout(self):
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 9)
        self.layout.setColumnStretch(1, 1)

    def _plot_chart(self):

        start_date, end_date, chart_type = self._chart_settings_control.get_settings()
        asset_universe = self._engine.get_asset_universe()
        market_weights = self._engine.get_market_weights(end_date)
        implied_returns = self._engine.get_market_returns(start_date, end_date)
        all_views = self._view_manager.get_all_views()
        if all_views.is_empty():
            self._main_chart.draw_charts(asset_universe, implied_returns, chart_type,
                                         market_weights)
        else:
            black_litterman_weights = self._engine.get_black_litterman_weights(all_views, start_date, end_date)
            self._main_chart.draw_charts(asset_universe, implied_returns, chart_type,
                                         market_weights, black_litterman_weights)

    def _change_chart_type(self):
        _, _, chart_type = self._chart_settings_control.get_settings()
        self._main_chart.select_chart(chart_type)

    @staticmethod
    def _read_config():
        config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "settings.json")
        with open(config_path) as config_file:
            configuration = json.load(config_file)

        return configuration


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication([])
    app.setStyle("fusion")
    blw = BlackLittermanApp()
    blw.setWindowTitle("Black Litterman")
    blw.resize(1000, 500)
    blw.show()
    sys.exit(app.exec_())
