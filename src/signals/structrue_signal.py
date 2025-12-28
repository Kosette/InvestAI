from signals.base import BaseSignal
from signals.base import TrendType
from signals.base import BaseSignal, TrendType
from config import STRATEGY_CONFIG


class StructureSignal(BaseSignal):

    PRICE_COL = "close"

    def evaluate(self, context: dict):
        df = context["kline"]

        # =========
        # 读取配置
        # =========
        trend_cfg = STRATEGY_CONFIG.trend

        ma_short_window = 20
        ma_long_window = 60
        resistance_window = trend_cfg.resistance_window

        pullback_threshold = trend_cfg.pullback_threshold
        breakout_buffer = trend_cfg.breakout_buffer

        # =========
        # 指标计算
        # =========
        df["ma_short"] = df[self.PRICE_COL].rolling(window=ma_short_window).mean()
        df["ma_long"] = df[self.PRICE_COL].rolling(window=ma_long_window).mean()

        price = round(df[self.PRICE_COL].iloc[-1], 2)
        prev_price = round(df[self.PRICE_COL].iloc[-2], 2)

        ma_short = round(df["ma_short"].iloc[-1], 2)
        ma_long = round(df["ma_long"].iloc[-1], 2)

        # =========
        # 趋势判断
        # =========
        if price > ma_short > ma_long:
            trend = TrendType.UPTREND
        elif price > ma_long:
            trend = TrendType.NEUTRAL
        else:
            trend = TrendType.DOWNTREND

        # =========
        # 结构信号
        # =========
        resistance = df[self.PRICE_COL].iloc[-resistance_window:].max()

        pullback = (
            trend == TrendType.UPTREND and
            price < ma_short and
            price > ma_long and
            (ma_short - price) / ma_short <= pullback_threshold
        )

        breakout = (
            prev_price <= resistance and
            price > resistance * (1 + breakout_buffer)
        )

        return {
            "price": price,
            "ma_short": ma_short,
            "ma_long": ma_long,
            "trend": trend,
            "pullback": pullback,
            "breakout": breakout,
        }

