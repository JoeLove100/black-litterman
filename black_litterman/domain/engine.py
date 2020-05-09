import numpy as np
import pandas as pd
from scipy import optimize
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from black_litterman.market_data.data_readers import BaseDataReader
from black_litterman.domain.views import ViewCollection, View
from black_litterman.constants import Configuration


@dataclass(frozen=False)
class CalculationSettings:
    tau: float
    risk_aversion: float
    start_date: str
    calculation_date: str
    asset_universe: Dict[str, str]

    @staticmethod
    def parse_from_config(config: Dict[str, Any]) -> "CalculationSettings":

        config_params = config[Configuration.PARAMETERS]
        config_data = config[Configuration.MARKET_DATA]

        calc_settings = CalculationSettings(config_params[Configuration.TAU],
                                            config_params[Configuration.RISK_AVERSION],
                                            config_data[Configuration.FIRST_DATE],
                                            config_data[Configuration.LAST_DATE],
                                            config_data[Configuration.ASSET_UNIVERSE])
        return calc_settings


class BLEngine:

    def __init__(self,
                 data_reader: BaseDataReader,
                 calc_settings: CalculationSettings,
                 view_collection: Optional[ViewCollection] = None):

        self._market_data_engine = data_reader.get_market_data_engine()
        self._calc_settings = calc_settings
        if view_collection is None:
            self._view_collection = ViewCollection()
        else:
            self._view_collection = view_collection

    def get_black_litterman_weights(self) -> pd.Series:
        """
        derive target portfolio weights based on the Black-Litterman
        portfolio optimisation model
        """

        # get the market data
        market_weights = self._market_data_engine.get_market_weights(self._calc_settings.start_date)
        market_cov = self._market_data_engine.get_annualised_cov_matrix(self._calc_settings.start_date,
                                                                        self._calc_settings.calculation_date)

        # get the view specific data
        view_mat = self.get_view_covariances_from_confidences(market_weights, market_cov)
        view_out_performance = self._view_collection.get_view_out_performances()
        view_cov = self.get_view_covariances_from_confidences(market_weights, market_cov)

        # calc BL weights
        bl_weights = self._get_weights(market_weights, market_cov, view_mat, view_cov, view_out_performance)
        return bl_weights

    def get_view_covariances_from_confidences(self,
                                              market_weights: pd.Series,
                                              market_covariance: pd.DataFrame) -> pd.DataFrame:
        """
        build a diagonal covariance matrix from the views
        based on the confidence in each view
        """

        cov_by_view = dict()
        all_views = self._view_collection.get_all_views()

        for view in all_views:
            var = self._confidence_to_variance(view, market_weights, market_covariance)
            cov_by_view.update({view.id: var})

        var_series = pd.Series(cov_by_view)
        cov_matrix = pd.DataFrame(np.diag(var_series), index=var_series.index, columns=var_series.index)
        return cov_matrix

    def _get_weights(self,
                     market_weights: pd.Series,
                     market_cov: pd.DataFrame,
                     view_matrix: pd.DataFrame,
                     view_cov: pd.DataFrame,
                     view_out_performance: pd.Series) -> pd.Series:
        """
        Black-Litterman calculation to derive target weights
        """

        mat_1 = (view_cov.divide(self._calc_settings.tau) +
                 view_matrix.dot(market_cov).dot(view_matrix.T))
        mat_1_inv = pd.DataFrame(np.linalg.inv(mat_1.values),
                                 index=mat_1.index, columns=mat_1.index)
        mat_2 = (view_out_performance.divide(self._calc_settings.risk_aversion)
                 - view_matrix.dot(market_cov).dot(market_weights))

        bl_weights = market_weights + view_matrix.T.dot(mat_1_inv).dot(mat_2)
        return bl_weights

    def _get_view_target_weights(self,
                                 view: View,
                                 market_weights: pd.Series,
                                 market_covariance: pd.DataFrame,
                                 view_matrix: pd.DataFrame,
                                 view_out_performance: pd.Series) -> pd.Series:
        """
        get target weights based on the view allocation and
        stated confidence in the view
        """

        zero_view_cov = pd.DataFrame([0], index=[view.id], columns=[view.id])
        full_confidence_weights = self._get_weights(market_weights, market_covariance, view_matrix, zero_view_cov,
                                                    view_out_performance)
        max_weight_difference = full_confidence_weights - market_weights
        target_weights = market_weights.add(view.confidence * max_weight_difference)

        return target_weights

    @staticmethod
    def _get_sum_squares_error(series_1: pd.Series,
                               series_2: pd.Series) -> float:
        """
        get the sum squared errors between two
        series
        """

        diff = series_1.subtract(series_2)
        sum_square = sum([x ** 2 for x in diff])
        return sum_square

    def _confidence_to_variance(self,
                                view: View,
                                market_weights: pd.Series,
                                market_covariance: pd.DataFrame):
        """
        convert a view confidence level to a variance for
        that view
        """

        view_matrix = view.get_view_data_frame(self._calc_settings.asset_universe)
        view_out_performance = pd.Series([view.out_performance], index=[view.id])
        target_weights = self._get_view_target_weights(view, market_weights, market_covariance,
                                                       view_matrix, view_out_performance)

        def _error_vs_target_weights(var) -> float:
            view_cov = pd.DataFrame(var, index=[view.id], columns=[view.id])
            weights_for_cov = self._get_weights(market_weights, market_covariance, view_matrix, view_cov,
                                                view_out_performance)

            return self._get_sum_squares_error(weights_for_cov, target_weights)

        variance = optimize.minimize(_error_vs_target_weights, np.array(0.1), method="BFGS")
        return variance.x[0]
