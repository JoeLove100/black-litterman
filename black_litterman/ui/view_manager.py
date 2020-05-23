from typing import List, Dict
from PySide2 import QtWidgets, QtCore
from black_litterman.ui.view_button import ViewButton
from black_litterman.ui.fonts import FontHelper
from black_litterman.domain.views import ViewCollection, View


class ViewManager(QtWidgets.QFrame):

    view_changed = QtCore.Signal()

    def __init__(self, all_views: Dict[str, View], asset_universe: List[str]) -> None:

        super().__init__()
        self._all_views = all_views
        self._asset_universe = asset_universe
        self._create_controls()
        self._add_event_handlers()
        self._add_controls_to_layout()
        self._size_layout()
        self._set_control_style()
        self._view_count = 0

    def _create_controls(self):

        self._views_panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)
        self._views_panel.setLayout(layout)
        self._views_panel.setMinimumHeight(300)

        self._add_view_button = QtWidgets.QPushButton("Add new view")
        self._add_view_button.setMinimumHeight(30)

        self._title_label = QtWidgets.QLabel()
        self._title_label.setText("Add market views (max 4)")
        self._title_label.setFont(FontHelper.get_title_font())

    def _add_event_handlers(self):

        self._add_view_button.clicked.connect(self._add_new_view_button)

    def _add_controls_to_layout(self):

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self._title_label, 0, 0)
        self.layout.addWidget(self._views_panel, 1, 0)
        self.layout.addWidget(self._add_view_button, 2, 0)

    def _size_layout(self):

        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 9)
        self.layout.setRowStretch(2, 1)

    def _set_control_style(self):

        self.setFrameStyle(QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Raised)
        self.setLineWidth(3)

    def _add_new_view_button(self) -> None:

        if self._view_count == 4:
            error_msg = QtWidgets.QMessageBox()
            error_msg.setIcon(QtWidgets.QMessageBox.Critical)
            error_msg.setText("Error")
            error_msg.setInformativeText('Max views reached')
            error_msg.setWindowTitle("Error")
            error_msg.exec_()
        else:
            new_view = View.get_new_view_with_defaults(self._asset_universe[0])
            button = ViewButton(view=new_view, asset_universe=self._asset_universe)
            button.setFixedHeight(75)
            self._views_panel.layout().addWidget(button)
            button.delete_clicked.connect(self._delete_button)
            button.view_changed.connect(self._raise_view_changed)
            self._view_count += 1
            self.view_changed.emit()

    def _delete_button(self,
                       button):
        button.setParent(None)
        self.view_changed.emit()
        self._view_count -= 1

    def _raise_view_changed(self):
        self.view_changed.emit()

    def get_all_views(self) -> ViewCollection:

        all_views = ViewCollection()

        for child_control in self._views_panel.children():
            if isinstance(child_control, ViewButton):
                view = child_control.get_view()
                all_views.add_view(view)

        return all_views
