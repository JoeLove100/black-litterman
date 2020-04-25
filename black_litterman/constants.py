from typing import List


class Configuration:

    MARKET_DATA_SOURCE = "source"
    MARKET_DATA_FILE_PATH = "file_path"

    TAU = "tau"
    RISK_AVERSION = "risk_aversion"


class MarketData:

    PRICE_DATA = "price_data"
    MARKET_CAP_DATA = "market_cap_data"

    def _get_data_types(self) -> List[str]:

        return [self.PRICE_DATA, self.MARKET_CAP_DATA]
