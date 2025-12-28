from signals.base import BaseSignal, TrendType
from config import STRATEGY_CONFIG


class StructureSignal(BaseSignal):

    def evaluate(self, context: dict):
        df = context["kline"]
        price_col = "close"

        # ===== 配置读取 =====
        ma_cfg = STRATEGY_CONFIG.trend.moving_averages
        pullback_cfg = STRATEGY_CONFIG.trend.pullback
        breakout_cfg = STRATEGY_CONFIG.trend.breakout

        short_ma = ma_cfg.short
        long_ma = ma_cfg.long

        # ===== 均线计算 =====
        df["ma_short"] = df[price_col].rolling(window=short_ma).mean()
        df["ma_long"] = df[price_col].rolling(window=long_ma).mean()

        price = df[price_col].iloc[-1]
        prev_price = df[price_col].iloc[-2]

        ma_short_val = df["ma_short"].iloc[-1]
        ma_long_val = df["ma_long"].iloc[-1]

        # ===== 趋势判断 =====
        if price > ma_short_val > ma_long_val:
            trend = TrendType.UPTREND
        elif price > ma_long_val:
            trend = TrendType.NEUTRAL
        else:
            trend = TrendType.DOWNTREND

        # ===== 回调判断（可配置开关） =====
        pullback = False
        if pullback_cfg.enabled:
            pullback = (
                price < ma_short_val
                and price > ma_long_val
                and (ma_short_val - price) / ma_short_val <= pullback_cfg.threshold
            )

        # ===== 突破判断 =====
        resistance_window = breakout_cfg.resistance_window
        resistance = df[price_col].iloc[-resistance_window:].max()

        breakout = (
            prev_price <= resistance
            and price > resistance * (1 + breakout_cfg.buffer)
        )

        return {
            "price": round(price, 2),
            "ma_short": round(ma_short_val, 2),
            "ma_long": round(ma_long_val, 2),
            "trend": trend,
            "pullback": pullback,
            "breakout": breakout,
        }
