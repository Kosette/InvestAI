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

    def get_latest_valuation(self, symbol: str) -> Dict[str, Any]:
        """
        获取最新估值指标，包括 PE、PB、PS 等
        """
        try:
            pe_pb_dict = self.data_source.get_pe_pb(symbol)
            # 可以只保留常用估值指标
            valuation = {
                "PE(TTM)": pe_pb_dict.get("PE(TTM)"),
                "PE(静)": pe_pb_dict.get("PE(静)"),
                "PB": pe_pb_dict.get("市净率"),
                "PS": pe_pb_dict.get("市销率"),
                "PEG": pe_pb_dict.get("PEG值"),
                "市现率": pe_pb_dict.get("市现率")
            }
            return valuation
        except Exception as e:
            logger.error(f"获取 {symbol} 估值失败: {e}")
            return {}

    def calc_momentum(self, symbol: str, period: str = "daily", window: int = 20) -> Dict[str, Any]:
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
        df['MA'] = df['close'].rolling(window=window).mean()
        df['momentum'] = df['close'] / df['MA'] - 1
        latest = df.iloc[-1]
        return {
            "momentum": latest['momentum'],
            "close": latest['close'],
            "MA": latest['MA']
        }

    def evaluate_quality(self, symbol: str) -> Dict[str, Any]:
        """
        基于财务指标计算股票质量评分
        可加入 ROE、净利润增长率、毛利率等因子
        """
        financials = self.data_source.get_financials(symbol)
        if not financials:
            return {}

        # 简单示例：ROE + 净利润增长率 + 销售毛利率综合评分
        roe = financials.get("净资产收益率(%)") or 0
        net_profit_growth = financials.get("净利润增长率(%)") or 0
        gross_margin = financials.get("销售毛利率(%)") or 0

        quality_score = (roe + net_profit_growth + gross_margin) / 3
        return {
            "roe": roe,
            "net_profit_growth": net_profit_growth,
            "gross_margin": gross_margin,
            "quality_score": quality_score
        }

    def generate_report(self, symbol: str) -> Dict[str, Any]:
        """
        综合分析报告，包含估值、动量、质量评分等
        """
        valuation = self.get_latest_valuation(symbol)
        momentum = self.calc_momentum(symbol)
        quality = self.evaluate_quality(symbol)
        profile = self.data_source.get_company_profile(symbol)

        report = {
            "symbol": symbol,
            "profile": profile,
            "valuation": valuation,
            "momentum": momentum,
            "quality": quality
        }
        return report


if __name__ == "__main__":
    service = StockAnalysisService()
    symbols = ["600519", "000001"]  # 示例股票
    for symbol in symbols:
        report = service.generate_report(symbol)
        logger.info(report)
