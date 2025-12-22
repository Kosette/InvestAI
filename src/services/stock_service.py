import pandas as pd
from typing import List, Dict, Any
from datacenter.stock import stock_data_source, StockDataSource
from log import logger
from config import Config
import numpy as np

class StockAnalysisService:
    """
    股票分析服务层 (Service)
    调用 StockDataSource 提供的原始数据接口，完成组合分析和策略计算。
    """

    def __init__(self, data_source: StockDataSource = stock_data_source):
        self.data_source: StockDataSource = data_source

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
            last_roe_trend = df["净资产收益率(%)"].tail(Config.QualityStockConfig.roe_trend_years).values
            logger.debug(f"净资产收益率: {last_roe_trend}")
            if not np.all(last_roe_trend >= Config.QualityStockConfig.roe_min):
                failed.append("roe_min")
            # 连续增长
            if not np.all(np.diff(last_roe_trend) > 0):
                failed.append("roe_trend")

            # 净利润连续增长的年份数
            last_net_profit_trend = df["净利润增长率(%)"].tail(Config.QualityStockConfig.net_profit_growth_years).values
            logger.debug(f"净利润增长率: {last_net_profit_trend}")
            if not np.all(last_net_profit_trend > 0):
                failed.append("net_profit_growth")

            # 最大资产负债率 (%)
            last_asset_debt_ratio_trend = df["资产负债率(%)"].tail(3).values
            logger.debug(f"资产负债率: {last_asset_debt_ratio_trend}")
            if not np.all(last_asset_debt_ratio_trend <= Config.QualityStockConfig.debt_ratio_max):
                failed.append("debt_ratio_max")

            # 营业收入连续增长的年份数
            last_revenue_trend = df["主营业务收入增长率(%)"].tail(Config.QualityStockConfig.revenue_growth_years).values
            logger.debug(f"主营业务收入增长率: {last_revenue_trend}")
            if not np.all(last_revenue_trend > 0):
                failed.append("revenue_growth")

            # 毛利率/净利率波动标准差
            margin_std = np.nanstd(df["销售净利率(%)"].tail(3).values)
            logger.debug(f"销售净利率波动标准差: {margin_std}")
            if margin_std > Config.QualityStockConfig.margin_std_max:
                failed.append("margin_std")

            # 主营业务收入占比下限
            last_core_business_ratio = df.tail(1)["主营利润比重"].item()
            logger.debug(f"主营利润比重: {last_core_business_ratio}")
            if not (last_core_business_ratio >= Config.QualityStockConfig.core_business_ratio_min):
                failed.append("core_business_ratio_min")

            df2 = self.data_source.get_pe_pb(symbol)
            # PEG 最大值
            peg = df2.tail(1)["PEG值"].item()
            logger.debug(f"PEG值: {peg}")
            if not (peg <= Config.QualityStockConfig.peg_max):
                failed.append("peg_max")

            # 市净率 PB 下限
            pb = df2.tail(1)["市净率"].item()
            logger.debug(f"市净率: {pb}")
            if not (pb >= Config.QualityStockConfig.pb_min):
                failed.append("pb_min")

            return {
                "is_quality": len(failed) == 0,
                "failed_criteria": failed
            }

        except Exception as e:
            logger.opt(exception=True).error(f"Error fetching Kline: {e}")
            return False

    def filter_stocks_by_quality(self):
        shares = self.data_source.get_all_a_shares()
        codes = shares["code"].tolist()
        logger.debug(f"total stocks: {len(codes)}")
        logger.debug(f"codes: {codes[:10]}")


if __name__ == "__main__":
    service = StockAnalysisService()
    symbol = "600519"  # 示例股票
    # report = service.calc_momentum(symbol)
    # report = service.compute_rsi(symbol)
    # report = service.check_stock(symbol)
    # logger.info(report)
    service.filter_stocks_by_quality()

