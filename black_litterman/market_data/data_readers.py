import pandas as pd
from logging import getLogger
from typing import Dict, List
from abc import ABC, abstractmethod
from black_litterman.market_data.engine import MarketDataEngine
from black_litterman.constants import Configuration, MarketData

logger = getLogger()


class BaseDataReader(ABC):

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
        data_engine = MarketDataEngine(formatted_data[MarketData.PRICE_DATA],
                                       formatted_data[MarketData.MARKET_CAP_DATA])
        return data_engine



class LocalDataReader(BaseDataReader):
    """
    read in data from a local spreadsheet
    """

    def __init__(self,
                 data_file_path):

        self._path = data_file_path

    def _read_raw_data(self) -> Dict[str, pd.DataFrame]:

        raw_data = pd.read_excel(self._path, sheet_name=self._get_data_types(), index_col=0)
        return raw_data

    def _validate_data(self, raw_data: Dict[str, pd.DataFrame]) -> None:

        pass
        # TODO: should add in some validation here

    def _get_formatted_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:

        for data in raw_data:
            data.index = pd.to_datetime(data.index)

        return raw_data


class SqlDataReader(BaseDataReader):
    """
    read in data from SQL server database
    """

    def _read_raw_data(self):
        raise NotImplementedError()

    def _validate_data(self,
                       raw_data: Dict[str, pd.DataFrame]):
        raise NotImplementedError()

    def _get_formatted_data(self,
                            raw_data: Dict[str, pd.DataFrame]):
        raise NotImplementedError()


class DataReaderFactory:

    SOURCE_LOCAL = "local"
    SOURCE_SQL = "sql"

    @classmethod
    def get_valid_sources(cls) -> List[str]:

        return [cls.SOURCE_LOCAL, cls.SOURCE_SQL]

    @classmethod
    def get_data_reader(cls,
                        config: Dict) -> BaseDataReader:

        data_source = config.get(Configuration.MARKET_DATA_SOURCE, "Not Defined")

        if data_source == cls.SOURCE_LOCAL:
            return LocalDataReader(config[Configuration.MARKET_DATA_FILE_PATH])
        elif data_source == cls.SOURCE_SQL:
            return SqlDataReader()
        else:
            logger.error(f"Data source '{data_source}' is not recognised - valid sources are "
                         f"{', '.join(cls.get_valid_sources())}")
