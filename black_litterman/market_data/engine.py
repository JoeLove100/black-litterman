import pandas as pd


class MarketDataEngine:

    def __init__(self,
                 price_data: pd.DataFrame,
                 market_cap_data: pd.DataFrame) -> None:

        self._returns_data = price_data.pct_change(1)
        self._market_cap_data = market_cap_data

    def get_annualised_cov_matrix(self,
                                  start_date: str,
                                  end_date: str):
        """
        get cov matrix based on returns for the
        given dates (inclusive)
        """

        date_mask = (self._returns_data.index >= start_date) & (self._returns_data.index <= end_date)
        returns_for_dates = self._returns_data[date_mask]
        covariance_for_dates = returns_for_dates.cov() * 250
        return covariance_for_dates

    def get_market_weights(self,
                           selected_date: str) -> pd.Series:
        """
        get market-cap weights for instruments based
        on index market caps
        """

        market_cap_for_date = self._market_cap_data.loc[selected_date, :]
        market_weights = market_cap_for_date / market_cap_for_date.sum()
        return market_weights

    def get_implied_returns(self,
                            start_date: str,
                            end_date: str,
                            risk_aversion: float) -> pd.Series:
        """
        get the market clearing returns for the given
        level of risk aversion
        """

        cov_matrix = self.get_annualised_cov_matrix(start_date, end_date)
        market_weights = self.get_market_weights(end_date)
        market_returns = cov_matrix.dot(market_weights).mul(risk_aversion)

        return market_returns
