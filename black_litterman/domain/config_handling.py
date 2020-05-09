import json
from typing import Any, Dict
from black_litterman.domain.engine import BLEngine, CalculationSettings
from black_litterman.market_data.data_readers import DataReaderFactory


class ConfigHandler:

    def __init__(self,
                 config_path):

        self._config_path = config_path

    def _read_config(self) -> Dict[str, Any]:

        with open(self._config_path) as config_file:
            configuration = json.load(config_file)

        return configuration

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
