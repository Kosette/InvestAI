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
    
    def compute_rsi(self, symbol: str, period: str = "daily", n: int = 30, price_col: str = "收盘"):
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

            # ROE
            if stock_data.get("roe", 0) < config.get("roe_min", 0):
                failed.append("roe_min")
            if stock_data.get("roe_trend_years", 0) < config.get("roe_trend_years", 0):
                failed.append("roe_trend_years")

            # 净利润、营收增长
            if stock_data.get("net_profit_growth_years", 0) < config.get("net_profit_growth_years", 0):
                failed.append("net_profit_growth_years")
            if stock_data.get("revenue_growth_years", 0) < config.get("revenue_growth_years", 0):
                failed.append("revenue_growth_years")

            # 负债率
            if config.get("exclude_financial_sector", True) and stock_data.get("is_financial", False):
                pass  # 金融股忽略负债率
            else:
                if stock_data.get("debt_ratio", 100) > config.get("debt_ratio_max", 100):
                    failed.append("debt_ratio_max")

            # 毛利率/净利率波动
            if stock_data.get("margin_std", 100) > config.get("margin_std_max", 100):
                failed.append("margin_std_max")

            # 主营业务占比
            if stock_data.get("core_business_ratio", 0) < config.get("core_business_ratio_min", 0):
                failed.append("core_business_ratio_min")

            # PEG
            if stock_data.get("peg", 100) > config.get("peg_max", 100):
                failed.append("peg_max")

            # 配股利
            if config.get("dividend_required", False) and not stock_data.get("dividend", False):
                failed.append("dividend_required")

            # PB
            if stock_data.get("pb", 0) < config.get("pb_min", 0):
                failed.append("pb_min")

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
