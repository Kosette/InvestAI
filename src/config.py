from dotenv import load_dotenv
import os

load_dotenv()

LOG_PATH = "./logs"
WATCHLIST_PATH = "./watchlist.json"

# ======================
# 股票池配置
# ======================

STOCK_POOL = [
    "600519.SH",
    "000001.SZ",
    "300750.SZ",
]


# ======================
# 监控与策略参数配置
# ======================

MONITOR_CONFIG = {
    # ====== 趋势策略参数 ======
    "trend": {
        "pullback_threshold": 0.03,   # 回调幅度（3%）
        "resistance_window": 20,      # 阻力位计算窗口
        "breakout_buffer": 0.005,     # 突破缓冲（0.5%）
    },

    # ====== 成交量 ======
    "volume": {
        "ma_window": 20,
        "min_ratio": 1.0,             # volume > volume_ma * ratio
    },

    # ====== 择时指标 ======
    "rsi": {
        "min": 40,
        "max": 65,
    },
    "cci": {
        "min": -100,
        "max": 100,
    },

}



class Config:
    SLACK_TOKEN = os.getenv("SLACK_TOKEN")


