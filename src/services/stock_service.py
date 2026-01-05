from typing import Any, Dict

from datacenter.stock import StockDataSource, stock_data_source

from config import Config
from log import logger


class StockAnalysisService:
    """
    股票分析服务层 (Service)
    调用 StockDataSource 提供的原始数据接口，完成组合分析和策略计算。
    """

    def __init__(self, data_source: StockDataSource = stock_data_source):
        self.data_source: StockDataSource = data_source

    def calc_momentum(
        self,
        symbol: str,
        period: str = "daily",
        window: int = 20,
        price_col: str = "收盘",
    ) -> Dict[str, Any]:
        """
        基于K线计算股票动量指标
        :param symbol: 股票代码
        :param period: K线周期
        :param window: 窗口长度
        """
        df = self.data_source.get_kline(symbol, period)
        if df.empty:
            return {}

        # 计算简单动量：最近收盘价 / N日均价
        df["MA"] = df[price_col].rolling(window=window).mean()
        df["momentum"] = df[price_col] / df["MA"] - 1
        latest = df.iloc[-1]
        return {
            "momentum": latest["momentum"],
            "close": latest[price_col],
            "MA": latest["MA"],
        }

    def compute_rsi(
        self, symbol: str, period: str = "daily", n: int = 30, price_col: str = "close"
    ):
        """
        基于 pandas DataFrame 计算 RSI（简单平均版本）
        df: 包含收盘价的 DataFrame
        n : 周期
        price_col : 收盘价列名
        """
        try:
            df = self.data_source.get_kline(symbol, period)
            if df.empty:
                return None

            # 计算涨跌
            delta = df[price_col].diff()

            # 分解涨跌
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            # 简单平均（因为你的数据量太小，不适合 Wilder 平滑）
            avg_gain = gain.rolling(window=n).mean()
            avg_loss = loss.rolling(window=n).mean()

            # RS
            rs = avg_gain / avg_loss

            # RSI
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"Error computing RSI: {e}")
            return None


if __name__ == "__main__":
    service = StockAnalysisService()
    symbol = "600519"  # 示例股票
    # report = service.calc_momentum(symbol)
    # report = service.compute_rsi(symbol)
    # report = service.check_stock(symbol)
    # logger.info(report)
