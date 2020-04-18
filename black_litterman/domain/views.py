import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Optional


class ViewAllocation:

    def __init__(self,
                 long_asset: str,
                 short_asset: Optional[str] = None):

        self.long_assert = long_asset
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

    id: int
    name: str
    out_performance: float
    confidence: float
    allocation: ViewAllocation


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
        for view in self._all_views:
            view_allocation = pd.Series(view.allocation, name=view.id)
            view_allocation = view_allocation.reindex(asset_universe)
            view_allocation.fillna(0, inplace=True)
            allocations.append(view_allocation)

        view_matrix = pd.concat(allocations, axis=1)
        return view_matrix

    def get_view_out_performances(self) -> pd.Series:

        out_performances = pd.Series({v.id: v.out_performance for v in self._all_views})
        return out_performances

    def get_view_cov_matrix(self) -> pd.DataFrame:

        uncertainties = pd.Series({v.id: v.confidence for v in self._all_views})
        cov_matrix = pd.DataFrame(0, index=uncertainties.index, columns=uncertainties.index)
        np.fill_diagonal(cov_matrix, uncertainties)
        return cov_matrix

