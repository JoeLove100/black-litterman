import numpy as np
import pandas as pd
from typing import List
from dataclasses import dataclass
from black_litterman.market_data.data_readers import BaseDataReader
from black_litterman.domain.views import ViewCollection


@dataclass(frozen=False)
class CalculationSettings:

    tau: float
    risk_aversion: float
    start_date: str
    calculation_date: str
    asset_universe: List[str]


class BLEngine:

    def __init__(self,
                 data_reader: BaseDataReader,
                 view_collection: ViewCollection,
                 ):

        self._market_data_engine = data_reader.get_market_data_engine()
        self._view_collection = view_collection

    def get_black_litterman_weights(self,
                                    calc_settings: CalculationSettings) -> pd.Series:

        market_weights = self._market_data_engine.get_market_weights(calc_settings.start_date)
        market_cov = self._market_data_engine.get_annualised_cov_matrix(calc_settings.start_date, calc_settings.calculation_date)

        view_mat = self._view_collection.get_view_matrix(calc_settings.asset_universe)
        view_cov = self._view_collection.get_view_cov_matrix()
        view_out_performance = self._view_collection.get_view_out_performances()

        mat_1 = (view_cov.divide(calc_settings.tau) +
                 view_mat.dot(market_cov).dot(view_mat.T))
        mat_1_inv = pd.DataFrame(np.invert(mat_1.values),
                                 index=mat_1.index, columns=mat_1.index)
        mat_2 = (view_out_performance.divide(calc_settings.risk_aversion)
                 - view_mat.dot(market_cov).dot(market_weights))

        bl_weights = market_weights + view_mat.T.dot(mat_1_inv).dot(mat_2)
        return bl_weights


