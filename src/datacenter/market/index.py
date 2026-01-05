import akshare as ak
import pandas as pd

from log import logger


class IndexDataSource:
    def get_kline(self, symbol: str, period: str = "daily") -> pd.DataFrame:
        try:
            if period == "daily":
                df = ak.stock_zh_index_daily(symbol=symbol)
            else:
                raise ValueError(f"Unsupported period: {period}")
            return df
        except Exception as e:
            logger.opt(exception=e).error(f"Error fetching Kline: {e}")
            return pd.DataFrame()


index_data_source = IndexDataSource()


if __name__ == "__main__":
    df = index_data_source.get_kline("sh000300")
    logger.info(df.tail())
