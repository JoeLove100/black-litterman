from typing import List, Dict
from PySide2 import QtWidgets, QtCore
from black_litterman.ui.view_button import View, ViewButton


class ViewManager(QtWidgets.QWidget):

    def __init__(self, all_views: Dict[str, View], asset_universe: List[str]) -> None:

        super().__init__()
        self._all_views = all_views
        self._asset_universe = asset_universe
        self._create_controls()
        self._add_event_handlers()
        self._add_controls_to_layout()
        self._size_layout()

    def _create_controls(self):

        self._views_panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        self._views_panel.setLayout(layout)
        self._views_panel.setMinimumHeight(300)

        self._add_view_button = QtWidgets.QPushButton("Add new view")
        self._add_view_button.setMinimumHeight(30)

    def _add_event_handlers(self):

        self._add_view_button.clicked.connect(self._add_new_view_button)

    def _add_controls_to_layout(self):

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self._views_panel, 0, 0)
        self.layout.addWidget(self._add_view_button, 1, 0)

    def _size_layout(self):

        self.layout.setRowStretch(0, 9)
        self.layout.setRowStretch(1, 1)

    def _add_new_view_button(self):

        new_view = View.get_new_view_with_defaults(self._asset_universe[0])
        button = ViewButton(view=new_view, asset_universe=self._asset_universe)
        button.setFixedHeight(75)
        self._views_panel.layout().addWidget(button)


if __name__ == "__main__":

    import sys
    from PySide2 import QtGui
    from black_litterman.domain.views import ViewAllocation

    app = QtWidgets.QApplication([])
    app.setFont(QtGui.QFont("Arial", 10))

    v = ViewManager({}, ["asset_1", "asset_2", "asset_3", "asset_4"])
    v.resize(200, 40)
    v.show()

    sys.exit(app.exec_())

