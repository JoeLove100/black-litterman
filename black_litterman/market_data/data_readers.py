import pandas as pd
from typing import Dict
from abc import ABC, abstractmethod
from black_litterman.market_data.engine import MarketDataEngine


class BaseDataReader(ABC):

    PRICE_DATA = "price_data"
    MARKET_CAP_DATA = "market_cap_data"

    @abstractmethod
    def _read_raw_data(self) -> Dict[str, pd.DataFrame]:
        """
        read in the raw data from
        local source
        """

    @abstractmethod
    def _validate_data(self,
                       raw_data: Dict[str, pd.DataFrame]) -> None:
        """
        check raw data for incorrect
        values
        """

    @abstractmethod
    def _get_formatted_data(self,
                            raw_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        apply type formatting
        to the data
        """

    def get_market_data_engine(self) -> MarketDataEngine:
        """
        read market data an wrap in engine class
        """

        raw_data = self._read_raw_data()
        self._validate_data(raw_data)
        formatted_data = self._get_formatted_data(raw_data)
        data_engine = MarketDataEngine(formatted_data[self.PRICE_DATA],
                                       formatted_data[self.MARKET_CAP_DATA])
        return data_engine


class LocalDataReader(BaseDataReader):
    """
    read in data from a local spreadsheet
    """

    def __init__(self,
                 data_file_path):

        self._path = data_file_path

    def _read_raw_data(self) -> Dict[str, pd.DataFrame]:

        raw_data = pd.read_excel(self._path, sheet_name=MarketData.get_data_types(), index_col=0)
        return raw_data

    def _validate_data(self, raw_data: Dict[str, pd.DataFrame]) -> None:

        pass
        # TODO: should add in some validation here

    def _get_formatted_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:

        for data in raw_data:
            data.index = pd.to_datetime(data.index)

        return raw_data
