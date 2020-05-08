import unittest
import pandas as pd
from unittest import mock
from black_litterman.domain.engine import BLEngine, CalculationSettings
from black_litterman.domain.views import View, ViewAllocation, ViewCollection


class TestEngine(unittest.TestCase):

    @staticmethod
    def _get_market_data():
        asset_universe = ["asset_1", "asset_2", "asset_3"]
        market_cov = pd.DataFrame([[0.18, -0.04, 0], [-0.04, 0.05, 0.07], [0, 0.07, 0.11]],
                                  index=asset_universe, columns=asset_universe)
        market_weights = pd.Series([0.3, 0.5, 0.2], index=asset_universe)
        calc_settings = CalculationSettings(1, 3, None, None, ["asset_1", "asset_2", "asset_3"])

        return market_cov, market_weights, calc_settings

    def test_get_bl_weights_absolute_view(self):
        # arrange
        market_cov, market_weights, calc_settings = self._get_market_data()
        view_matrix = pd.Series([1, 0, 0], index=market_cov.index, name="view_1").to_frame().T
        view_cov = pd.DataFrame([[0.05]], index=["view_1"], columns=["view_1"])
        view_outperf = pd.Series([0.2], index=["view_1"])

        # act
        result = BLEngine._get_weights(market_weights, market_cov, view_matrix, view_cov,
                                       view_outperf, calc_settings)

        # assert
        expected_result = pd.Series([0.442028986, 0.5, 0.2], index=market_cov.index)
        pd.testing.assert_series_equal(expected_result, result)

    def test_get_bl_weights_relative_view(self):
        # arrange
        market_cov, market_weights, calc_settings = self._get_market_data()
        view_matrix = pd.Series([0, -1, 1], index=market_cov.index, name="view_1").to_frame().T
        view_cov = pd.DataFrame([0.1], index=["view_1"], columns=["view_1"])
        view_outperf = pd.Series([0.06], index=["view_1"])

        # act
        result = BLEngine._get_weights(market_weights, market_cov, view_matrix, view_cov,
                                       view_outperf, calc_settings)

        # assert
        expected_result = pd.Series([0.3, 0.5833333, 0.1166667], index=market_cov.index)
        pd.testing.assert_series_equal(expected_result, result)

    def test_get_bl_weights_multiple_views(self):
        # arrange
        market_cov, market_weights, calc_settings = self._get_market_data()
        view_matrix = pd.DataFrame([[0, -1, 1], [1, 0, 0], [-1, 0, 1]], index=["view_1", "view_2", "view_3"],
                                   columns=market_cov.index)
        view_cov = pd.DataFrame([[0.1, 0, 0], [0, 0.05, 0], [0, 0, 0.04]], index=["view_1", "view_2", "view_3"],
                                columns=["view_1", "view_2", "view_3"])
        view_outperf = pd.Series([0.05, 0.09, 0.08], index=["view_1", "view_2", "view_3"])

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

    def test_get_target_weights_relative_view(self):
        # arrange
        test_view = View("1", "test_view", 0.08, 0.5, ViewAllocation("asset_3", "asset_2"))
        market_cov, market_weights, calc_settings = self._get_market_data()
        view_matrix = test_view.get_view_data_frame(["asset_1", "asset_2", "asset_3"])
        view_out_performance = pd.Series([0.08], index=["1"])

        # act
        result = BLEngine._get_view_target_weights(test_view, calc_settings, market_weights, market_cov,
                                                   view_matrix, view_out_performance)

        # assert
        expected_result = pd.Series([0.3, 0.58333333, 0.11666667], index=["asset_1", "asset_2", "asset_3"])
        pd.testing.assert_series_equal(expected_result, result)

    def test_get_target_weights_absolute_view(self):
        # arrange
        test_view = View("1", "test_view", 0.13, 0.8, ViewAllocation("asset_1", None))
        market_cov, market_weights, calc_settings = self._get_market_data()
        view_matrix = test_view.get_view_data_frame(["asset_1", "asset_2", "asset_3"])
        view_out_performance = pd.Series([0.13], index=["1"])

        # act
        result = BLEngine._get_view_target_weights(test_view, calc_settings, market_weights, market_cov,
                                                   view_matrix, view_out_performance)

        # assert
        expected_result = pd.Series([0.3414814815, 0.5, 0.2], index=["asset_1", "asset_2", "asset_3"])
        pd.testing.assert_series_equal(expected_result, result)

    def test_confidence_to_variance_absolute_view(self):
        # arrange
        view = View("test_view", "test_view", 0.13, 0.5, ViewAllocation("asset_1"))
        market_cov, market_weights, calc_settings = self._get_market_data()

        # act
        result = BLEngine._confidence_to_variance(view, calc_settings, market_weights, market_cov)

        # assert
        self.assertAlmostEqual(0.18, result, delta=1e-4)

    def test_confidence_to_variance_relative_view(self):
        # arrange
        view = View("test_view", "test_view", 0.06, 0.3, ViewAllocation("asset_3", "asset_2"))
        market_cov, market_weights, calc_settings = self._get_market_data()

        # act
        result = BLEngine._confidence_to_variance(view, calc_settings, market_weights, market_cov)

        # assert
        self.assertAlmostEqual(0.04667, result, delta=1e-4)

    def test_get_view_covariances_from_confidences(self):
        # arrange
        view_collection = ViewCollection()
        view_collection.add_view(View("view_1", "view_1", 0.14, 0.6, ViewAllocation("asset_1")))
        view_collection.add_view(View("view_2", "view_2", 0.06, 0.3, ViewAllocation("asset_3", "asset_2")))

        engine = BLEngine(mock.MagicMock(), view_collection)
        mock_conf_to_var = mock.MagicMock()
        mock_conf_to_var.side_effect = [0.1, 0.05]
        engine._confidence_to_variance = mock_conf_to_var

        market_cov, market_weight, calc_settings = self._get_market_data()

        # act
        result = engine.get_view_covariances_from_confidences(market_weight, market_cov, calc_settings)

        # assert
        expected_result = pd.DataFrame([[0.1, 0], [0, 0.05]], index=["view_1", "view_2"], columns=["view_1", "view_2"])
        pd.testing.assert_frame_equal(expected_result, result)









