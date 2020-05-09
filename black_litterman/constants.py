from typing import List


class Configuration:

    MARKET_DATA = "market_data"
    MARKET_DATA_SOURCE = "source"
    MARKET_DATA_FILE_PATH = "file_path"
    FIRST_DATE = "first_date"
    LAST_DATE = "last_date"
    ASSET_UNIVERSE = "asset_universe"

    PARAMETERS = "parameters"
    TAU = "tau"
    RISK_AVERSION = "risk_aversion"


class MarketData:

    PRICE_DATA = "price_data"
    MARKET_CAP_DATA = "market_cap_data"

    @classmethod
    def get_data_types(cls) -> List[str]:

        return [cls.PRICE_DATA, cls.MARKET_CAP_DATA]
