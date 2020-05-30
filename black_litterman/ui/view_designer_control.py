from typing import List
from PySide2 import QtWidgets, QtCore
from black_litterman.ui.allocation_controls import AllocationControlRelative, AllocationControlAbsolute
from black_litterman.domain.views import View, ViewAllocation


class ViewDesignerDialog(QtWidgets.QDialog):

    def __init__(self,
                 view: View,
                 asset_universe: List[str]):

        super().__init__()
        self._view = view
        self._asset_universe = asset_universe
        self._create_controls()
        self._initialise_controls(view, asset_universe)
        self._add_event_handlers()
        self._add_controls_to_layout()
        self._size_layout()
        self.setWindowTitle("Edit market view")

    def _create_controls(self) -> None:

        self._name_box = QtWidgets.QLineEdit()
        self._name_box.setFixedHeight(30)

        self._view_type_combo = QtWidgets.QComboBox()
        self._view_type_combo.setFixedHeight(30)

        self._confidence_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self._confidence_slider.setFixedHeight(30)
        self._slider_label = QtWidgets.QLabel()
        self._slider_label.setFixedHeight(30)

        self._outperf_up_down = QtWidgets.QDoubleSpinBox()
        self._outperf_up_down.setFixedHeight(30)

        self._save_button = QtWidgets.QPushButton("Save")
        self._save_button.setMinimumHeight(30)
        self._save_button.setMaximumWidth(100)

        self._exit_button = QtWidgets.QPushButton("Exit")
        self._exit_button.setMinimumHeight(30)
        self._exit_button.setMaximumWidth(100)

        self._allocation_group = QtWidgets.QGroupBox()
        v_box = QtWidgets.QVBoxLayout()
        self._allocation_group.setLayout(v_box)

    def _initialise_controls(self,
                             view: View,
                             asset_universe: List[str]) -> None:

        self._name_box.setText(view.name)

        self._view_type_combo.addItems(ViewAllocation.get_all_view_types())

        self._confidence_slider.setMinimum(0)
        self._confidence_slider.setMaximum(10)
        self._confidence_slider.setTickInterval(1)
        self._confidence_slider.setFixedHeight(30)
        self._confidence_slider.setSliderPosition(int(view.confidence * 10))

        self.slider_label = QtWidgets.QLabel("{:.0%}".format(view.confidence/10))

        self._outperf_up_down.setMinimum(-10)
        self._outperf_up_down.setMaximum(10)
        self._outperf_up_down.setDecimals(1)
        self._outperf_up_down.setSingleStep(0.1)
        self._outperf_up_down.setValue(view.out_performance)

        self._allocation_group.setTitle("View allocation")

        if view.allocation.view_type == ViewAllocation.ABSOLUTE:
            self._allocation_control = AllocationControlAbsolute(view.allocation, asset_universe)
        else:
            self._allocation_control = AllocationControlRelative(view.allocation, asset_universe)
        self._allocation_group.layout().addWidget(self._allocation_control)

    def _add_event_handlers(self):

        self._confidence_slider.valueChanged.connect(self._display_confidence)
        self._view_type_combo.currentTextChanged.connect(self._set_allocation_control)
        self._save_button.clicked.connect(self.on_click_ok)
        self._exit_button.clicked.connect(self.reject)

    def _add_controls_to_layout(self):

        self.layout = QtWidgets.QGridLayout()

        # add main controls
        self.layout.addWidget(self._name_box, 0, 1)
        self.layout.addWidget(self._confidence_slider, 1, 1)
        self.layout.addWidget(self.slider_label, 1, 2)
        self.layout.addWidget(self._view_type_combo, 3, 1)
        self.layout.addWidget(self._outperf_up_down, 2, 1)
        self.layout.addWidget(self._allocation_group, 4, 0, 1, 3)
        self.layout.addWidget(self._save_button, 5, 0)
        self.layout.addWidget(self._exit_button, 5, 1)

        # add control labels
        self.layout.addWidget(QtWidgets.QLabel("View name"), 0, 0)
        self.layout.addWidget(QtWidgets.QLabel("Confidence"), 1, 0)
        self.layout.addWidget(QtWidgets.QLabel("View type"), 3, 0)
        self.layout.addWidget(QtWidgets.QLabel("Return (%pa)"), 2, 0)
        self.setLayout(self.layout)

    def _size_layout(self):
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 1)
        self.layout.setRowStretch(2, 1)
        self.layout.setRowStretch(3, 10)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 10)
        self.layout.setColumnMinimumWidth(1, 200)
        self.layout.setColumnStretch(2, 1)

    def _display_confidence(self,
                            val):

        self.slider_label.setText("{:.0%}".format(val/10))

    def _set_allocation_control(self,
                                allocation_type):

        self._allocation_group.layout().removeWidget(self._allocation_control)
        self._allocation_control.deleteLater()
        self._allocation_control = None

        if allocation_type == ViewAllocation.ABSOLUTE:
            self._allocation_control = AllocationControlAbsolute(self._view.allocation,
                                                                 self._asset_universe)
        else:
            self._allocation_control = AllocationControlRelative(self._view.allocation,
                                                                 self._asset_universe)

        self._allocation_group.layout().addWidget(self._allocation_control)

    def on_click_ok(self):
        self._view = self._get_view_from_controls()
        self.accept()

    def _get_view_from_controls(self) -> View:

        view_id = self._view.id
        name = self._name_box.text()
        out_performance = self._outperf_up_down.value() / 100
        confidence = self._confidence_slider.value() / 10
        allocation = self._allocation_control.get_allocation()

        view = View(view_id, name, out_performance, confidence, allocation)
        return view

    def get_view(self):
        return self._view

