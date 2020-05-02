import unittest
import pandas as pd
from black_litterman.domain.engine import BLEngine, CalculationSettings


class TestEngine(unittest.TestCase):

    @staticmethod
    def _get_market_data():
        asset_universe = ["asset_1", "asset_2", "asset_3"]
        market_cov = pd.DataFrame([[0.18, -0.04, 0], [-0.04, 0.05, 0.07], [0, 0.07, 0.11]],
                                  index=asset_universe, columns=asset_universe)
        market_weights = pd.Series([0.3, 0.5, 0.2], index=asset_universe)

        return market_cov, market_weights

    def test_get_bl_weights_absolute_view(self):
        # arrange
        market_cov, market_weights = self._get_market_data()
        view_matrix = pd.Series([1, 0, 0], index=market_cov.index, name="view_1").to_frame().T
        view_cov = pd.DataFrame([[0.05]], index=["view_1"], columns=["view_1"])
        view_outperf = pd.Series([0.2], index=["view_1"])
        calc_settings = CalculationSettings(1, 3, None, None, None)

        # act
        result = BLEngine._get_weights(market_weights, market_cov, view_matrix, view_cov,
                                       view_outperf, calc_settings)

        # assert
        expected_result = pd.Series([0.442028986, 0.5, 0.2], index=market_cov.index)
        pd.testing.assert_series_equal(expected_result, result)

    def test_get_bl_weights_relative_view(self):
        # arrange
        market_cov, market_weights = self._get_market_data()
        view_matrix = pd.Series([0, -1, 1], index=market_cov.index, name="view_1").to_frame().T
        view_cov = pd.DataFrame([0.1], index=["view_1"], columns=["view_1"])
        view_outperf = pd.Series([0.06], index=["view_1"])
        calc_settings = CalculationSettings(1, 3, None, None, None)

        # act
        result = BLEngine._get_weights(market_weights, market_cov, view_matrix, view_cov,
                                       view_outperf, calc_settings)

        # assert
        expected_result = pd.Series([0.3, 0.5833333, 0.1166667], index=market_cov.index)
        pd.testing.assert_series_equal(expected_result, result)

    def test_get_bl_weights_multiple_views(self):
        # arrange
        market_cov, market_weights = self._get_market_data()
        view_matrix = pd.DataFrame([[0, -1, 1], [1, 0, 0], [-1, 0, 1]], index=["view_1", "view_2", "view_3"],
                                   columns=market_cov.index)
        view_cov = pd.DataFrame([[0.1, 0, 0], [0, 0.05, 0], [0, 0, 0.04]], index=["view_1", "view_2", "view_3"],
                                columns=["view_1", "view_2", "view_3"])
        view_outperf = pd.Series([0.05, 0.09, 0.08], index=["view_1", "view_2", "view_3"])
        calc_settings = CalculationSettings(1, 3, None, None, None)

        # act
        result = BLEngine._get_weights(market_weights, market_cov, view_matrix, view_cov,
                                       view_outperf, calc_settings)

        # assert
        expected_result = pd.Series([0.2982666, 0.6179881, 0.1043762], index=market_cov.index)
        pd.testing.assert_series_equal(expected_result, result)

    def test_get_sum_squares(self):
        # arrange
        series_1 = pd.Series([0.5, 0.25, 0.75, 0.3])
        series_2 = pd.Series([0.2, 0.3, 0.75, 0.4])

        # act
        result = BLEngine._get_sum_squares_error(series_1, series_2)

        # assert
        self.assertAlmostEqual(0.1025, result)



