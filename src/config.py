from dotenv import load_dotenv
import os

load_dotenv()

LOG_PATH = "./logs"

class QualityStockConfig:
    """
    优质股筛选配置类
    所有参数为类变量，可通过环境变量动态覆盖默认值
    """

    # 核心财务指标
    roe_min = float(os.getenv("ROE_MIN", 8))                        # 最低净资产收益率 ROE (%)
    roe_trend_years = int(os.getenv("ROE_TREND_YEARS", 3))         # ROE 连续增长的年份数
    net_profit_growth_years = int(os.getenv("NET_PROFIT_GROWTH_YEARS", 3))  # 净利润连续增长的年份数
    revenue_growth_years = int(os.getenv("REVENUE_GROWTH_YEARS", 3))        # 营业收入连续增长的年份数
    debt_ratio_max = float(os.getenv("DEBT_RATIO_MAX", 60))        # 最大资产负债率 (%)
    margin_std_max = float(os.getenv("MARGIN_STD_MAX", 5))         # 毛利率/净利率波动标准差上限 (%)
    core_business_ratio_min = float(os.getenv("CORE_BUSINESS_RATIO_MIN", 0.8))  # 主营业务收入占比下限
    peg_max = float(os.getenv("PEG_MAX", 1.5))                     # PEG 最大值
    pb_min = float(os.getenv("PB_MIN", 1))                          # 市净率 PB 下限


class Config:
    QualityStockConfig = QualityStockConfig