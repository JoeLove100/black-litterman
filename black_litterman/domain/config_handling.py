import os
import json
import pandas as pd
from datetime import datetime
from typing import Any, Dict
from black_litterman.constants import Configuration
from black_litterman.domain.engine import BLEngine, CalculationSettings
from black_litterman.market_data.data_readers import DataReaderFactory


class ConfigHandler:

    def __init__(self,
                 config_path):

        self._config_path = config_path

    def _read_config(self) -> Dict[str, Any]:

        main_path = os.path.join(self._config_path, "settings.json")
        credentials_path = os.path.join(self._config_path, "credentials.json")
        with open(main_path) as config_file:
            main_configuration = json.load(config_file)

        with open(credentials_path) as credentials_file:
            credentials = json.load(credentials_file)

        main_configuration[Configuration.CREDENTIALS] = credentials
        if not main_configuration[Configuration.MARKET_DATA][Configuration.LAST_DATE]:
            prev_date = (datetime.now() + pd.offsets.BusinessDay(-1)).strftime("%Y-%m-%d")
            main_configuration[Configuration.MARKET_DATA][Configuration.LAST_DATE] = prev_date
        return main_configuration

    def _build_engine(self,
                      config: Dict[str, Any]) -> BLEngine:

        data_reader = DataReaderFactory.get_data_reader(config)
        calc_settings = CalculationSettings.parse_from_config(config)
        engine = BLEngine(data_reader, calc_settings)
        return engine

    def build_engine_from_config(self) -> BLEngine:

        config = self._read_config()
        engine = self._build_engine(config)
        return engine
