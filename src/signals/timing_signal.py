from signals.base import BaseSignal, TrendType
from pandas import DataFrame
from loguru import logger
import numpy as np
from config import STRATEGY_CONFIG


class TimingSignal(BaseSignal):

    PRICE_COL = "close"
    HIGH_COL = "high"
    LOW_COL = "low"

    # =====================
    # Indicator Computation
    # =====================
    def compute_cci(
        self,
        df: DataFrame,
        high_col: str,
        low_col: str,
        close_col: str,
        n: int
    ):
        try:
            if df.empty:
                return None

            tp = (df[high_col] + df[low_col] + df[close_col]) / 3
            tp_sma = tp.rolling(window=n).mean()
            mean_dev = tp.rolling(window=n).apply(
                lambda x: np.mean(np.abs(x - x.mean())),
                raw=True
            )

            return (tp - tp_sma) / (0.015 * mean_dev)

        except Exception as e:
            logger.error(f"Error computing CCI: {e}")
            return None

    def compute_rsi(self, df: DataFrame, price_col: str, n: int):
        try:
            if df.empty:
                return None

            delta = df[price_col].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.rolling(window=n).mean()
            avg_loss = loss.rolling(window=n).mean()

            rs = avg_gain / avg_loss
            return 100 - (100 / (1 + rs))

        except Exception as e:
            logger.error(f"Error computing RSI: {e}")
            return None

    # =====================
    # Signal Evaluation
    # =====================
    def evaluate(self, context: dict):
        df = context["kline"]

        # =========
        # Config
        # =========
        trend_cfg = STRATEGY_CONFIG.trend
        volume_cfg = STRATEGY_CONFIG.volume
        rsi_cfg = STRATEGY_CONFIG.rsi
        cci_cfg = STRATEGY_CONFIG.cci

        ma_short_window = 20
        ma_long_window = 60
        resistance_window = trend_cfg.resistance_window

        pullback_threshold = trend_cfg.pullback_threshold
        breakout_buffer = trend_cfg.breakout_buffer

        # =========
        # MA
        # =========
        df["ma_short"] = df[self.PRICE_COL].rolling(window=ma_short_window).mean()
        df["ma_long"] = df[self.PRICE_COL].rolling(window=ma_long_window).mean()

        price = round(df[self.PRICE_COL].iloc[-1], 2)
        prev_price = round(df[self.PRICE_COL].iloc[-2], 2)

        ma_short = round(df["ma_short"].iloc[-1], 2)
        ma_long = round(df["ma_long"].iloc[-1], 2)

        # =========
        # Trend
        # =========
        if price > ma_short > ma_long:
            trend = TrendType.UPTREND
        elif price > ma_long:
            trend = TrendType.NEUTRAL
        else:
            trend = TrendType.DOWNTREND

        # =========
        # Structure
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

        # =========
        # Timing Indicators
        # =========
        rsi_series = self.compute_rsi(df, self.PRICE_COL, n=14)
        cci_series = self.compute_cci(
            df,
            self.HIGH_COL,
            self.LOW_COL,
            self.PRICE_COL,
            n=20
        )

        rsi_value = round(rsi_series.iloc[-1], 2) if rsi_series is not None else None
        cci_value = round(cci_series.iloc[-1], 2) if cci_series is not None else None

        # =========
        # Range Filter
        # =========
        rsi_in_range = (
            rsi_value is not None and
            rsi_cfg.min <= rsi_value <= rsi_cfg.max
        )

        cci_in_range = (
            cci_value is not None and
            cci_cfg.min <= cci_value <= cci_cfg.max
        )

        return {
            "price": price,
            "ma_short": ma_short,
            "ma_long": ma_long,
            "trend": trend,
            "pullback": pullback,
            "breakout": breakout,
            "rsi": rsi_value,
            "rsi_in_range": rsi_in_range,
            "cci": cci_value,
            "cci_in_range": cci_in_range,
        }
