import pandas as pd
from logging import getLogger
from typing import Dict, List
from abc import ABC, abstractmethod
from black_litterman.market_data.engine import MarketDataEngine
from black_litterman.constants import Configuration, MarketData
from cardano.market_data.market_data_client import MarketDataClient

logger = getLogger()


class BaseDataReader(ABC):

    @abstractmethod
    def _read_raw_data(self,
                       start_date: str,
                       end_date: str) -> Dict[str, pd.DataFrame]:
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
                            raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """
        apply type formatting
        to the data
        """

    def get_market_data_engine(self,
                               start_date: str,
                               end_date: str) -> MarketDataEngine:
        """
        read market data an wrap in engine class
        """

        raw_data = self._read_raw_data(start_date, end_date)
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

    def _read_raw_data(self,
                       start_date: str,
                       end_date: str) -> Dict[str, pd.DataFrame]:

        raw_data = pd.read_excel(self._path, sheet_name=MarketData.get_data_types(), index_col=0)
        raw_data = raw_data.loc[start_date: end_date, :]
        return raw_data

    def _validate_data(self, raw_data: Dict[str, pd.DataFrame]) -> None:

        pass
        # TODO: should add in some validation here

    def _get_formatted_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:

        for data in raw_data.values():
            data.index = pd.to_datetime(data.index)

        return raw_data


class SqlDataReader(BaseDataReader):
    """
    read in data from SQL server database
    """

    def _read_raw_data(self,
                       start_date: str,
                       end_date: str):
        raise NotImplementedError()

    def _validate_data(self,
                       raw_data: Dict[str, pd.DataFrame]) -> None:
        raise NotImplementedError()

    def _get_formatted_data(self,
                            raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        raise NotImplementedError()


class ReutersDataReader(BaseDataReader):
    """
    read in data from the Thompson Reuters
    market data API
    """

    def __init__(self,
                 credentials: Dict[str, str],
                 tickers: Dict[str, str]):
        self._mdc = MarketDataClient(credentials=credentials)
        self._tickers = tickers

    def _read_raw_data(self,
                       start_date: str,
                       end_date: str) -> Dict[str, pd.DataFrame]:

        n = len(self._tickers)
        price_requests = list(zip(self._tickers.values(), ["PI"] * n, [start_date] * n, [end_date] * n))
        price_requests = pd.DataFrame(price_requests, columns=self._mdc.get_reuters_input_headers())
        self._mdc.add_reuters_data(price_requests)

        market_cap_requests = list(zip(self._tickers.values(), ["X(MV)~GBP"] * n, [start_date] * n, [end_date] * n))
        market_cap_requests = pd.DataFrame(market_cap_requests, columns=self._mdc.get_reuters_input_headers())
        self._mdc.add_reuters_data(market_cap_requests)

        raw_data = self._mdc.get_data_as_dataframe()
        price_data = raw_data[raw_data["field"] == "PI"]
        market_cap_data = raw_data[raw_data["field"] == "X(MV)~GBP"]
        return {MarketData.PRICE_DATA: price_data, MarketData.MARKET_CAP_DATA: market_cap_data}

    def _validate_data(self, raw_data: Dict[str, pd.DataFrame]) -> None:
        # TODO: need to add some market data validation
        pass

    def _get_formatted_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:

        all_formatted_data = {}
        for data_type, data in raw_data.items():
            formatted_data = pd.pivot_table(data, columns="ticker", index="date", values="value")
            formatted_data.index = pd.to_datetime(formatted_data.index)
            all_formatted_data.update({data_type: formatted_data})

        return all_formatted_data


class DataReaderFactory:

    SOURCE_LOCAL = "local"
    SOURCE_SQL = "sql"
    SOURCE_REUTERS = "reuters"

    @classmethod
    def get_valid_sources(cls) -> List[str]:

        return [cls.SOURCE_LOCAL, cls.SOURCE_SQL]

    @classmethod
    def get_data_reader(cls,
                        config: Dict) -> BaseDataReader:

        config_data = config[Configuration.MARKET_DATA]
        data_source = config_data.get(Configuration.MARKET_DATA_SOURCE, "Not Defined")

        if data_source == cls.SOURCE_LOCAL:
            return LocalDataReader(config_data[Configuration.MARKET_DATA_FILE_PATH])
        elif data_source == cls.SOURCE_SQL:
            return SqlDataReader()
        elif data_source == cls.SOURCE_REUTERS:
            return ReutersDataReader(config[Configuration.CREDENTIALS],
                                     config_data[Configuration.ASSET_UNIVERSE])
        else:
            err_msg = f"Data source '{data_source}' is not recognised - valid sources " \
                f"are {', '.join(cls.get_valid_sources())}"
            logger.error(err_msg)
            raise ValueError(err_msg)
