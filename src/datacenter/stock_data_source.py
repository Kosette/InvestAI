import akshare as ak
from typing import Optional, Dict, Any
import pandas as pd
from log import logger
import orjson


class StockDataSource:
    """
    基于 AkShare 的股票数据源模块
    提供 Kline、财务指标、公司资料等原始数据访问接口
    """

    def get_kline(self, symbol: str, period: str = "daily", adjust: str = "qfq") -> pd.DataFrame:
        """
        获取股票历史 K 线数据
        :param symbol: 股票代码，例如 '000001'
        :param period: 'daily', 'weekly', 'monthly'
        :param adjust: 复权类型 'qfq' 前复权, 'hfq' 后复权, 'none' 不复权
        :return: pd.DataFrame 包含 date, open, high, low, close, volume 等
        """
        try:
            if period == "daily":
                df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust=adjust)
            elif period == "weekly":
                df = ak.stock_zh_a_hist(symbol=symbol, period="weekly", adjust=adjust)
            elif period == "monthly":
                df = ak.stock_zh_a_hist(symbol=symbol, period="monthly", adjust=adjust)
            else:
                raise ValueError(f"Unsupported period: {period}")
            return df
        except Exception as e:
            logger.error(f"Error fetching Kline: {e}")
            return pd.DataFrame()

    def get_financials(self, symbol: str, start_year: str = '2025') -> Dict[str, Any]:
        """
        获取财务指标数据，例如 ROE, EPS, 净利润等
        :param symbol: 股票代码
        :return: 字典形式的财务指标
        """
        try:
            df = ak.stock_financial_analysis_indicator(symbol=symbol, start_year=start_year)
            # 可以根据需要提取最新一行数据
            if not df.empty:
                latest = df.iloc[0].to_dict()
                return latest
            else:
                logger.warning(f"未获取到 {symbol} 的财务指标数据。")
                return {}
        except Exception as e:
            logger.error(f"Error fetching financials: {e}")
            return {}

    # 获取个股概要信息
    def get_company_profile(self, symbol: str):
        """
        通过东方财富接口获取指定股票代码的公司基本信息。
        :param symbol: 股票代码，如 '600519' (贵州茅台)
        :return: 包含公司基本信息的 DataFrame 或 None
        """
        try:
            # 获取个股的概要信息
            # symbol: 股票代码
            # indicator: 用于指定获取信息的类型，这里用 '基本情况'
            company_info_df = ak.stock_individual_info_em(symbol=symbol)
            
            if not company_info_df.empty:
                info_dict = company_info_df.set_index('item')['value'].to_dict()
                return info_dict # 返回字典形式
            else:
                logger.warning(f"未获取到 {symbol} 的东方财富个股基本情况。")
                return None
        except Exception as e:
            logger.error(f"获取 {symbol} 东方财富个股基本情况失败: {e}")
            return None


    def get_pe_pb(self, symbol: str) -> Dict[str, float]:
        """
        获取估值指标 PE 和 PB
        """
        try:
            df = ak.stock_value_em(symbol=symbol)
            latest = df.iloc[-1]
            logger.debug(f"PE/PB 数据: {latest}")
            return latest.to_dict()
        except Exception as e:
            logger.error(f"Error fetching PE/PB: {e}")
            return {}
    
    def get_all_a_shares(self) -> pd.DataFrame:
        """
        获取中国A股市场所有上市公司的股票列表。
        数据源：东方财富-A股实时行情
        :return: 包含股票代码、名称等信息的 DataFrame
        """
        try:
            # 获取东方财富A股实时行情数据
            # 实际返回的是所有A股的列表及实时数据
            stock_list_df = ak.stock_info_a_code_name()
            return stock_list_df
        except Exception as e:
            logger.error(f"获取A股股票列表失败: {e}")
            return pd.DataFrame()


stock_data_source = StockDataSource()


if __name__ == "__main__":
    # res = stock_data_source.get_company_profile("600519")
    # res = stock_data_source.get_financials("600519")
    res = stock_data_source.get_pe_pb("600519")
    logger.info(orjson.dumps(res,option=orjson.OPT_INDENT_2).decode())
    # df = stock_data_source.get_all_a_shares()
    # df = stock_data_source.get_kline("600519")
    # logger.info(df.tail())