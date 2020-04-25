import unittest
import pandas as pd
from typing import List
from black_litterman.domain.views import ViewAllocation, ViewCollection, View


class TestViews(unittest.TestCase):

    @staticmethod
    def _get_view_collection(collection_type: str):

        view_allocation_1 = ViewAllocation("asset_2")
        view_1 = View("1", "view_1", 0.06, 0.5, view_allocation_1)
        view_allocation_2 = ViewAllocation("asset_1", "asset_3")
        view_2 = View("2", "view_2", 0.02, 0.9, view_allocation_2)
        view_allocation_3 = ViewAllocation("asset_3", "asset_2")
        view_3 = View("3", "view_3", 0.08, 0.2, view_allocation_3)

        view_collection = ViewCollection()
        if collection_type == "none":
            return view_collection
        elif collection_type == "absolute":
            view_collection.add_view(view_1)
            return view_collection
        elif collection_type == "relative":
            view_collection.add_view(view_2)
            view_collection.add_view(view_3)
            return view_collection
        else:
            view_collection.add_view(view_1)
            view_collection.add_view(view_2)
            view_collection.add_view(view_3)
            return view_collection

    def test_get_view_matrix_no_views(self):
        # arrange
        view_collection = self._get_view_collection("none")
        asset_universe = ["asset_1", "asset_2", "asset_3", "asset_4"]

        # act
        result = view_collection.get_view_matrix(asset_universe)

        # assert
        expected_result = pd.DataFrame()
        pd.testing.assert_frame_equal(expected_result, result)

    def test_get_view_matrix_absolute_view(self):
        # arrange
        view_collection = self._get_view_collection("absolute")
        asset_universe = ["asset_1", "asset_2", "asset_3", "asset_4"]

        # act
        result = view_collection.get_view_matrix(asset_universe)

        # assert
        expected_result = pd.Series([0, 1, 0, 0], index=asset_universe, name="1").to_frame()
        pd.testing.assert_frame_equal(expected_result, result)

    def test_get_view_matrix_relative(self):
        # arrange
        view_collection = self._get_view_collection("relative")
        asset_universe = ["asset_1", "asset_2", "asset_3", "asset_4"]

        # act
        result = view_collection.get_view_matrix(asset_universe)

        # assert
        expected_result = pd.DataFrame([[1, 0, -1, 0], [0, -1, 1, 0]], index=["2", "3"],
                                       columns=asset_universe)
        pd.testing.assert_frame_equal(expected_result, result)

    def test_get_view_matrix_all_view_types(self):
        # arrange
        view_collection = self._get_view_collection("")
        asset_universe = ["asset_1", "asset_2", "asset_3", "asset_4"]

        # act
        result = view_collection.get_view_matrix(asset_universe)

        # assert
        expected_result = pd.DataFrame([[0, 1, 0, 0], [1, 0, -1, 0], [0, -1, 1, 0]], index=["1", "2", "3"],
                                       columns=asset_universe)
        pd.testing.assert_frame_equal(expected_result, result)

    def test_get_out_performance(self):
        # arrange
        view_collection = self._get_view_collection("")

        # act
        result = view_collection.get_view_out_performances()

        # assert
        expected_result = pd.Series({"1": 0.06, "2": 0.02, "3": 0.08})
        pd.testing.assert_series_equal(expected_result, result)

    def test_get_view_cov_matrix(self):
        # arrange
        view_collection = self._get_view_collection("")

        # act
        result = view_collection.get_view_cov_matrix()

        # assert
        expected_result = pd.DataFrame([[0.5, 0, 0], [0, 0.9, 0], [0, 0, 0.2]],
                                       index=["1", "2", "3"], columns=["1", "2", "3"])
        pd.testing.assert_frame_equal(expected_result, result, check_dtype=False)


