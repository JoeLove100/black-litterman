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
                 view_collection: ViewCollection):

        self._market_data_engine = data_reader.get_market_data_engine()
        self._view_collection = view_collection

    def get_black_litterman_weights(self,
                                    calc_settings: CalculationSettings) -> pd.Series:
        """
        derive target portfolio weights based on the Black-Litterman
        portfolio optimisation model
        """

        market_weights = self._market_data_engine.get_market_weights(calc_settings.start_date)
        market_cov = self._market_data_engine.get_annualised_cov_matrix(calc_settings.start_date,
                                                                        calc_settings.calculation_date)

        view_mat = self._view_collection.get_view_matrix(calc_settings.asset_universe)
        view_cov = self._view_collection.get_view_cov_matrix()
        view_out_performance = self._view_collection.get_view_out_performances()

        bl_weights = self._get_weights(market_weights, market_cov, view_mat, view_cov, view_out_performance,
                                       calc_settings)
        return bl_weights

    @staticmethod
    def _get_weights(market_weights: pd.Series,
                     market_cov: pd.DataFrame,
                     view_matrix: pd.DataFrame,
                     view_cov: pd.DataFrame,
                     view_out_performance: pd.Series,
                     calc_settings: CalculationSettings) -> pd.Series:
        """
        Black-Litterman calculation to derive target weights
        """

        mat_1 = (view_cov.divide(calc_settings.tau) +
                 view_matrix.dot(market_cov).dot(view_matrix.T))
        mat_1_inv = pd.DataFrame(np.linalg.inv(mat_1.values),
                                 index=mat_1.index, columns=mat_1.index)
        mat_2 = (view_out_performance.divide(calc_settings.risk_aversion)
                 - view_matrix.dot(market_cov).dot(market_weights))

        bl_weights = market_weights + view_matrix.T.dot(mat_1_inv).dot(mat_2)
        return bl_weights




