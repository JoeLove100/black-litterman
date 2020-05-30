from typing import Tuple
from datetime import datetime
import pandas as pd
from PySide2 import QtWidgets, QtCore
from black_litterman.ui.fonts import FontHelper


class ChartTypes:

    WEIGHTS = "weights"
    RETURNS = "returns"

    @classmethod
    def get_chart_types(cls):
        return [cls.WEIGHTS, cls.RETURNS]


class ChartSettingsControl(QtWidgets.QWidget):

    dates_changed = QtCore.Signal()
    chart_type_changed = QtCore.Signal()

    def __init__(self,
                 start_date: str,
                 end_date: str):

        super().__init__()
        self._create_controls()
        self._initialise_controls(start_date, end_date)
        self._add_event_handlers()
        self._add_controls_to_layout()
        self._size_layout()
        self._set_control_style()

    def _create_controls(self):

        self._chart_type_combo = QtWidgets.QComboBox()
        self._chart_type_combo.setMaximumWidth(100)

        self._start_date_edit = QtWidgets.QDateEdit()
        self._start_date_edit.setMaximumWidth(100)

        self._end_date_edit = QtWidgets.QDateEdit()
        self._end_date_edit.setMaximumWidth(100)

    def _initialise_controls(self,
                             start_date: str,
                             end_date: str):

        max_start_date = pd.to_datetime(end_date) - pd.offsets.MonthEnd(3)
        min_end_date = pd.to_datetime(start_date) + pd.offsets.MonthEnd(3)

        self._start_date_edit.setMinimumDate(QtCore.QDate.fromString(start_date, "yyyy-MM-dd"))
        self._start_date_edit.setDate(QtCore.QDate.fromString(start_date, "yyyy-MM-dd"))
        self._start_date_edit.setMaximumDate(QtCore.QDate.fromString(max_start_date.strftime("%Y-%m-%d")))

        self._end_date_edit.setMinimumDate(QtCore.QDate.fromString(min_end_date.strftime("%Y-%m-%d")))
        self._end_date_edit.setDate(QtCore.QDate.fromString(end_date, "yyyy-MM-dd"))
        self._end_date_edit.setMaximumDate(QtCore.QDate.fromString(end_date, "yyyy-MM-dd"))

        self._chart_type_combo.addItems(ChartTypes.get_chart_types())
        self._chart_type_combo.setCurrentText(ChartTypes.WEIGHTS)

    def _add_event_handlers(self):

        self._start_date_edit.editingFinished.connect(self._start_date_updated)
        self._end_date_edit.editingFinished.connect(self._end_date_updated)
        self._chart_type_combo.currentTextChanged.connect(self._chart_type_changed)

    def _add_controls_to_layout(self):

        self._layout = QtWidgets.QGridLayout()
        self.setLayout(self._layout)

        combo_label = QtWidgets.QLabel("Show:")
        combo_label.setMaximumWidth(35)
        self._layout.addWidget(combo_label, 0, 0)
        self._layout.addWidget(self._chart_type_combo, 0, 1)

        start_date_label = QtWidgets.QLabel("History start:")
        start_date_label.setMaximumWidth(75)
        self._layout.addWidget(start_date_label, 0, 2)
        self._layout.addWidget(self._start_date_edit, 0, 3)

        end_date_label = QtWidgets.QLabel("Calculation Date:")
        end_date_label.setMaximumWidth(105)
        self._layout.addWidget(end_date_label, 0, 4)
        self._layout.addWidget(self._end_date_edit, 0, 5)

    def _size_layout(self):

        self._layout.setColumnMinimumWidth(0, 50)
        self._layout.setColumnMinimumWidth(1, 50)
        self._layout.setColumnMinimumWidth(2, 50)
        self._layout.setColumnMinimumWidth(3, 50)
        self._layout.setColumnMinimumWidth(4, 50)
        self._layout.setColumnMinimumWidth(5, 50)

    def _set_control_style(self):

        self._chart_type_combo.setFont(FontHelper.get_text_font())
        self._start_date_edit.setFont(FontHelper.get_text_font())
        self._end_date_edit.setFont(FontHelper.get_text_font())

    def _start_date_updated(self):

        new_start_date = self._start_date_edit.date().toPython()
        new_max_end_date = new_start_date - pd.offsets.MonthEnd(3)
        self._end_date_edit.setMaximumDate(QtCore.QDate.fromString(new_max_end_date.strftime("%Y-%m-%d")))
        self.dates_changed.emit()

    def _end_date_updated(self):

        new_end_date = self._end_date_edit.date().toPython()
        new_min_start_date = new_end_date + pd.offsets.MonthEnd(3)
        self._start_date_edit.setMinimumDate(QtCore.QDate.fromString(new_min_start_date.strftime("%Y-%m-%d")))
        self.dates_changed.emit()

    def _chart_type_changed(self):
        self.chart_type_changed.emit()

    def get_settings(self) -> Tuple[str, str, str]:

        start_date = self._start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self._end_date_edit.date().toString("yyyy-MM-dd")
        chart_type = self._chart_type_combo.currentText()

        return start_date, end_date, chart_type
