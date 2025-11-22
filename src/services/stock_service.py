import pandas as pd
from typing import List, Dict, Any
from datacenter.stock_data_source import stock_data_source, StockDataSource
from log import logger


class StockAnalysisService:
    """
    股票分析服务层 (Service)
    调用 StockDataSource 提供的原始数据接口，完成组合分析和策略计算。
    """

    def __init__(self, data_source: StockDataSource = stock_data_source):
        self.data_source = data_source

    def calc_momentum(self, symbol: str, period: str = "daily", window: int = 20, price_col: str = "收盘") -> Dict[str, Any]:
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
        df['MA'] = df[price_col].rolling(window=window).mean()
        df['momentum'] = df[price_col] / df['MA'] - 1
        latest = df.iloc[-1]
        return {
            "momentum": latest['momentum'],
            "close": latest[price_col],
            "MA": latest['MA']
        }
    
    def compute_rsi(self, symbol: str, period: str = "daily", n: int = 30, price_col: str = "close"):
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

    def check_stock(self, symbol: str) -> bool:
        try:
            failed = []

            df = self.data_source.get_last_n_years_financials(symbol)

            # ROE 最低值
            if "净资产收益率(%)" in df.columns:
                last_3_roe = df["净资产收益率(%)"].tail(3).values
                if not np.all(last_3_roe >= config.roe_min):
                    failed.append("roe_min")
                # 连续增长
                if not np.all(np.diff(last_3_roe) > 0):
                    failed.append("roe_trend")

            # 净利润增长
            if "净利润增长率(%)" in df.columns:
                last_3_net_profit = df["净利润增长率(%)"].tail(3).values
                if not np.all(last_3_net_profit > 0):
                    failed.append("net_profit_growth")

            # 营业收入增长
            if "主营业务收入增长率(%)" in df.columns:
                last_3_revenue = df["主营业务收入增长率(%)"].tail(3).values
                if not np.all(last_3_revenue > 0):
                    failed.append("revenue_growth")

            # 毛利率/净利率波动标准差
            if "销售净利率(%)" in df.columns:
                margin_std = np.nanstd(df["销售净利率(%)"].tail(3).values)
                if margin_std > config.margin_std_max:
                    failed.append("margin_std")

            return {
                "is_quality": len(failed) == 0,
                "failed_criteria": failed
            }

        except Exception as e:
            logger.error(f"Error fetching Kline: {e}")
            return False

    def filter_stocks(self):
        pass


if __name__ == "__main__":
    service = StockAnalysisService()
    symbol = "600519"  # 示例股票
    # report = service.calc_momentum(symbol)
    report = service.compute_rsi(symbol)
    logger.info(report)
