
# ======================
# 监控与策略参数配置
# ======================
from pydantic import BaseModel, Field
from typing import List
# =====================
# 趋势相关配置
# =====================

class MovingAverageConfig(BaseModel):
    short: int = Field(..., description="短期均线周期，如 MA20")
    long: int = Field(..., description="长期均线周期，如 MA60")


class PullbackConfig(BaseModel):
    enabled: bool = Field(True, description="是否启用趋势内回调判断")
    threshold: float = Field(
        ..., description="回调幅度阈值，如 0.03 表示 3%"
    )


class BreakoutConfig(BaseModel):
    resistance_window: int = Field(
        ..., description="阻力位计算回看窗口（交易日数）"
    )
    buffer: float = Field(
        ..., description="突破确认缓冲比例，如 0.005 表示 0.5%"
    )


class TrendConfig(BaseModel):
    """
    趋势识别与结构信号相关配置
    """
    moving_averages: MovingAverageConfig
    pullback: PullbackConfig
    breakout: BreakoutConfig


# =====================
# 成交量过滤配置
# =====================

class VolumeConfig(BaseModel):
    ma_window: int = Field(..., description="成交量均线周期")
    min_ratio: float = Field(
        ..., description="当前成交量 ≥ 均量 × 该比例"
    )


# =====================
# 区间型指标配置（RSI / CCI）
# =====================

class RangeIndicatorConfig(BaseModel):
    min: float = Field(..., description="指标下限")
    max: float = Field(..., description="指标上限")


# =====================
# 策略元信息（可选，但强烈建议保留）
# =====================

class StrategyMetaConfig(BaseModel):
    id: str
    name: str
    version: str
    description: str


# =====================
# 顶层策略配置
# =====================

class StrategyConfig(BaseModel):
    """
    策略完整配置定义（与 YAML 严格一致）
    """
    strategy: StrategyMetaConfig
    trend: TrendConfig
    volume: VolumeConfig
    rsi: RangeIndicatorConfig
    cci: RangeIndicatorConfig
    risk_disclaimer: List[str]
