import pandas as pd
from PySide2 import QtWidgets, QtCore
from black_litterman.ui.fonts import FontHelper
from black_litterman.domain.engine import CalculationSettings


class ChartTypes:

    WEIGHTS = "weights"
    RETURNS = "returns"

    @classmethod
    def get_chart_types(cls):
        return [cls.WEIGHTS, cls.RETURNS]


class ChartSettingsControl(QtWidgets.QWidget):

    settings_changed = QtCore.Signal()

    def __init__(self,
                 calc_settings: CalculationSettings):

        super().__init__()
        self._create_controls()
        self._initialise_controls(calc_settings)
        self._add_event_handlers()
        self._add_controls_to_layout()
        self._size_layout()
        self._set_control_style()

    def _create_controls(self):

        self._chart_type_combo = QtWidgets.QComboBox("Show:")
        self._start_date_edit = QtWidgets.QDateEdit("Start date")
        self._end_date_edit = QtWidgets.QDateEdit("Calculation date")

    def _initialise_controls(self,
                             calc_settings: CalculationSettings):

        max_start_date = pd.to_datetime(calc_settings.calculation_date) - pd.offsets.MonthEnd(-3)
        min_end_date = pd.to_datetime(calc_settings.start_date) + pd.offsets.MonthEnd(3)

        self._start_date_edit.setMinimumDate(QtCore.QDate.fromString(calc_settings.start_date))
        self._start_date_edit.setDate(QtCore.QDate.fromString(calc_settings.start_date))
        self._start_date_edit.setMaximumDate(QtCore.QDate.fromString(max_start_date.strftime("%Y-%m-%d")))

        self._end_date_edit.setMinimumDate(QtCore.QDate.fromString(min_end_date.strftime("%Y-%m-%d")))
        self._end_date_edit.setDate(QtCore.QDate.fromString(calc_settings.calculation_date))
        self._end_date_edit.setMaximumDate(QtCore.QDate.fromString(calc_settings.calculation_date))

        self._chart_type_combo.addItems(ChartTypes.get_chart_types())
        self._chart_type_combo.setCurrentText(ChartTypes.WEIGHTS)

    def _add_event_handlers(self):

        self._start_date_edit.dateChanged.connect(self._start_date_updated)
        self._end_date_edit.dateChanged.connect(self._end_date_updated)

    def _add_controls_to_layout(self):

        self._layout = QtWidgets.QGridLayout()
        self.setLayout(self._layout)

        self._layout.addWidget(self._chart_type_combo, 0, 0)
        self._layout.addWidget(self._start_date_edit, 0, 1)
        self._layout.addWidget(self._end_date_edit, 0, 2)

    def _size_layout(self):

        self._layout.setColumnMinimumWidth(0, 100)
        self._layout.setColumnMinimumWidth(1, 100)
        self._layout.setColumnMinimumWidth(2, 100)

    def _set_control_style(self):

        self._chart_type_combo.setFont(FontHelper.get_text_font())
        self._start_date_edit.setFont(FontHelper.get_text_font())
        self._end_date_edit.setFont(FontHelper.get_text_font())

    def _start_date_updated(self):

        new_start_date = self._start_date_edit.date().toPython()
        new_max_end_date = new_start_date - pd.offsets.MonthEnd(3)
        self._end_date_edit.setMaximumDate(QtCore.QDate.fromString(new_max_end_date.strftime("%Y-%m-%d")))

    def _end_date_updated(self):

        new_end_date = self._end_date_edit.date().toPython()
        new_min_start_date = new_end_date + pd.offsets.MonthEnd(3)
        self._start_date_edit.setMinimumDate(QtCore.QDate.fromString(new_min_start_date.strftime("%Y-%m-%d")))
