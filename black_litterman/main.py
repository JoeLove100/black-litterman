import os
import json
from PySide2 import QtWidgets
from black_litterman.ui.view_manager import ViewManager
from black_litterman.ui.portfolio_chart import PortfolioChart
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

        config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "settings.json")
        config_handler = ConfigHandler(config_path)
        self._engine = config_handler.build_engine_from_config()

    def _create_controls(self):
        self._main_chart = PortfolioChart()
        self._view_manager = ViewManager({}, self._engine.get_asset_universe())
        self._view_manager.setMaximumWidth(300)
        self._view_manager.setMinimumWidth(300)

    def _initialise_controls(self):
        market_weights = self._engine.get_market_weights()
        asset_universe = self._engine.get_asset_universe()
        self._main_chart.draw_chart(asset_universe, market_weights)

    def _add_event_handlers(self):

        self._view_manager.view_changed.connect(self._plot_chart)

    def _add_controls_to_layout(self):
        layout = QtWidgets.QGridLayout()
        title_label = QtWidgets.QLabel("Black Litterman Asset Allocation Tool")
        title_label.setFont(FontHelper.get_title_font())

        layout.addWidget(title_label, 0, 0, 1, 1)
        layout.addWidget(self._main_chart, 1, 0, 1, 1)
        layout.addWidget(self._view_manager, 1, 1, 1, 1)

        self.layout = layout
        self.setLayout(self.layout)

    def _size_layout(self):
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 9)
        self.layout.setColumnStretch(1, 1)

    def _plot_chart(self):

        asset_universe = self._engine.get_asset_universe()
        market_weights = self._engine.get_market_weights()
        all_views = self._view_manager.get_all_views()
        if all_views.is_empty():
            self._main_chart.draw_chart(asset_universe, market_weights)
        else:
            black_litterman_weights = self._engine.get_black_litterman_weights(all_views)
            self._main_chart.draw_chart(asset_universe, market_weights, black_litterman_weights)

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
    blw.resize(900, 500)
    blw.show()
    sys.exit(app.exec_())
