import unittest
import pandas as pd
from datetime import datetime
from black_litterman.market_data.engine import MarketDataEngine


class TestMarketDataEngine(unittest.TestCase):

    @staticmethod
    def _get_market_data_engine() -> MarketDataEngine:

        dates = pd.date_range(start=datetime(2020, 3, 1), end=datetime(2020, 3, 10), freq="B")
        price_data = pd.DataFrame({"asset_1": [100, 101, 102, 100, 98, 99, 100],
                                   "asset_2": [95, 94, 97, 93, 95, 97, 99],
                                   "asset_3": [20, 20.5, 20.5, 20.5, 19.5, 19, 18]},
                                  index=dates)

        market_cap_data = pd.DataFrame({"asset_1": [1000000, 1000000, 1000000, 1000000, 1020000, 1020000, 1020000],
                                        "asset_2": [500000, 500000, 500000, 400000, 400000, 250000, 250000],
                                        "asset_3": [500000, 500000, 400000, 200000, 400000, 500000, 500000]},
                                       index=dates)

        engine = MarketDataEngine(price_data, market_cap_data)
        return engine

    def test_get_covariance_all_dates(self):
        # arrange
        engine = self._get_market_data_engine()
        start_date = "2020-03-01"
        end_date = "2020-03-10"

        # act
        result = engine.get_annualised_cov_matrix(start_date, end_date)

        # assert
        expected_result = {"asset_1": [0.00375866, 0.00318745, 0.00139934],
                           "asset_2": [0.00318745, 0.01216780, -0.00695777],
                           "asset_3": [0.00139934, -0.00695777, 0.01485093]}
        expected_result = pd.DataFrame(expected_result, index=["asset_1", "asset_2", "asset_3"])
        pd.testing.assert_frame_equal(expected_result, result)

    def test_get_covariance_different_end_date(self):
        # arrange
        engine = self._get_market_data_engine()
        start_date = "2020-03-01"
        end_date = "2020-03-05"

        # act
        result = engine.get_annualised_cov_matrix(start_date, end_date)

        # assert
        expected_result = {"asset_1": [0.00460482, 0.00807358, 0.00195711],
                           "asset_2": [0.00807358, 0.02133385, -0.00077281],
                           "asset_3": [0.00195711, -0.00077281, 0.00329404]}
        expected_result = pd.DataFrame(expected_result, index=["asset_1", "asset_2", "asset_3"])
        pd.testing.assert_frame_equal(expected_result, result)

    def test_get_covariance_different_start_date(self):
        # arrange
        engine = self._get_market_data_engine()
        start_date = "2020-03-05"
        end_date = "2020-03-10"

        # act
        result = engine.get_annualised_cov_matrix(start_date, end_date)

        # assert
        expected_result = pd.DataFrame({"asset_1": [0.00473009, 0.00478256, -0.00227043],
                                        "asset_2": [0.00478256, 0.01534223, -0.01042061],
                                        "asset_3": [-0.00227043, -0.01042061, 0.00933641]},
                                       index=["asset_1", "asset_2", "asset_3"])
        pd.testing.assert_frame_equal(expected_result, result)

    def test_get_market_weights(self):
        # arrange
        engine = self._get_market_data_engine()
        selected_date = "2020-03-05"

        # act
        result = engine.get_market_weights(selected_date)

        # assert
        expected_result = pd.Series([0.625, 0.25, 0.125], index=["asset_1", "asset_2", "asset_3"])
        pd.testing.assert_series_equal(expected_result, result, check_names=False)
