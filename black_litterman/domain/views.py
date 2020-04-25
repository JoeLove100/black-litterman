import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional
from uuid import uuid4


class ViewAllocation:

    def __init__(self,
                 long_asset: str,
                 short_asset: Optional[str] = None):

        self.long_asset = long_asset
        self.short_asset = short_asset

    ABSOLUTE = "Absolute"
    RELATIVE = "Relative"

    @classmethod
    def get_all_view_types(cls):
        return [cls.ABSOLUTE, cls.RELATIVE]

    @property
    def view_type(self):
        if self.short_asset:
            return self.RELATIVE
        else:
            return self.ABSOLUTE


@dataclass(frozen=True)
class View:

    id: str
    name: str
    out_performance: float
    confidence: float
    allocation: ViewAllocation

    @ staticmethod
    def get_new_view_with_defaults(asset: str):
        view_id = uuid4().hex
        name = "New view"
        out_performance = 0
        confidence = 0
        allocation = ViewAllocation(asset)

        return View(view_id, name, out_performance, confidence, allocation)


class ViewCollection:

    def __init__(self):

        self._all_views = dict()

    def add_view(self,
                 view: View) -> None:

        self._all_views.update({view.id: view})

    def get_view(self,
                 view_id: int) -> View:

        view = self._all_views[view_id]
        return view

    def get_view_matrix(self,
                        asset_universe: List[str]) -> pd.DataFrame:

        allocations = []
        for view_id, view in self._all_views.items():
            allocation_for_view = pd.Series([0] * len(asset_universe), index=asset_universe, name=view_id)
            allocation_for_view[view.allocation.long_asset] = 1
            if view.allocation.short_asset:
                allocation_for_view[view.allocation.short_asset] = -1

            allocations.append(allocation_for_view)

        if not allocations:
            return pd.DataFrame()
        else:
            view_matrix = pd.concat(allocations, axis=1).T
            return view_matrix

    def get_view_out_performances(self) -> pd.Series:

        out_performances = pd.Series({view_id: view.out_performance for view_id, view in self._all_views.items()})
        return out_performances

    def get_view_cov_matrix(self) -> pd.DataFrame:

        uncertainties = pd.Series({view_id: view.confidence for view_id, view in self._all_views.items()})
        cov_matrix = pd.DataFrame(np.diag(uncertainties), index=uncertainties.index, columns=uncertainties.index)
        return cov_matrix

