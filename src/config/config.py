from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

LOG_PATH = "./logs"
WATCHLIST_PATH = "./conf/watchlist.json"
INDEX_POOL_PATH = "./conf/index_pool.json"
STRATEGY_CONFIG_PATH = "./conf/strategy.yaml"

# ======================
# 监控与策略参数配置
# ======================
class TrendConfig(BaseModel):
    pullback_threshold: float = Field(..., description="回调幅度")
    resistance_window: int = Field(..., description="阻力位计算窗口")
    breakout_buffer: float = Field(..., description="突破缓冲")


class VolumeConfig(BaseModel):
    ma_window: int
    min_ratio: float = Field(..., description="volume > volume_ma * ratio")


class RangeIndicatorConfig(BaseModel):
    min: float
    max: float


class StrategyConfig(BaseModel):
    trend: TrendConfig
    volume: VolumeConfig
    rsi: RangeIndicatorConfig
    cci: RangeIndicatorConfig


class Config:
    SLACK_TOKEN = os.getenv("SLACK_TOKEN")


