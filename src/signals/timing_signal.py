from signals.base import BaseSignal
from pandas import DataFrame
from loguru import logger
import numpy as np
from config import STRATEGY_CONFIG


class TimingSignal(BaseSignal):

    # =====================
    # 指标计算
    # =====================

    def compute_rsi(self, df: DataFrame, price_col: str, n: int):
        try:
            delta = df[price_col].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.rolling(window=n).mean()
            avg_loss = loss.rolling(window=n).mean()

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except Exception as e:
            logger.error(f"RSI error: {e}")
            return None

    def compute_cci(
        self,
        df: DataFrame,
        high_col: str,
        low_col: str,
        close_col: str,
        n: int,
    ):
        try:
            tp = (df[high_col] + df[low_col] + df[close_col]) / 3
            tp_sma = tp.rolling(window=n).mean()
            mean_dev = tp.rolling(window=n).apply(
                lambda x: np.mean(np.abs(x - x.mean())),
                raw=True,
            )
            cci = (tp - tp_sma) / (0.015 * mean_dev)
            return cci
        except Exception as e:
            logger.error(f"CCI error: {e}")
            return None

    # =====================
    # Signal 评估
    # =====================

    def evaluate(self, context: dict):
        df = context["kline"]
        price_col = "close"

        # ===== 配置 =====
        volume_cfg = STRATEGY_CONFIG.volume
        rsi_cfg = STRATEGY_CONFIG.rsi
        cci_cfg = STRATEGY_CONFIG.cci

        # ===== 成交量 =====
        df["vol_ma"] = df["volume"].rolling(
            window=volume_cfg.ma_window
        ).mean()

        volume = df["volume"].iloc[-1]
        volume_ma = df["vol_ma"].iloc[-1]

        volume_ok = volume >= volume_ma * volume_cfg.min_ratio

        # ===== RSI =====
        rsi_series = self.compute_rsi(
            df, price_col, n=volume_cfg.ma_window
        )
        rsi_val = rsi_series.iloc[-1]

        rsi_ok = rsi_cfg.min <= rsi_val <= rsi_cfg.max

        # ===== CCI =====
        cci_series = self.compute_cci(
            df, "high", "low", price_col, n=volume_cfg.ma_window
        )
        cci_val = cci_series.iloc[-1]

        cci_ok = cci_cfg.min <= cci_val <= cci_cfg.max

        return {
            "volume": round(volume, 2),
            "volume_ma": round(volume_ma, 2),
            "volume_ok": volume_ok,
            "rsi": round(rsi_val, 2),
            "rsi_ok": rsi_ok,
            "cci": round(cci_val, 2),
            "cci_ok": cci_ok,
            "timing_ok": volume_ok and rsi_ok and cci_ok,
        }
