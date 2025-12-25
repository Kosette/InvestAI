from signals.base import BaseSignal
from pandas import DataFrame
from loguru import logger
import numpy as np
from signals.base import TrendType
from config import STRATEGY_CONFIG

class TimingSignal(BaseSignal):
   def compute_cci(
      self,
      df: DataFrame,
      high_col: str,
      low_col: str,
      close_col: str,
      n: int = 20
   ):
      try:
         if df.empty:
               return None

         # 1️⃣ Typical Price
         tp = (df[high_col] + df[low_col] + df[close_col]) / 3

         # 2️⃣ TP 的简单移动平均
         tp_sma = tp.rolling(window=n).mean()

         # 3️⃣ 平均绝对偏差（Mean Deviation）
         mean_dev = tp.rolling(window=n).apply(
               lambda x: np.mean(np.abs(x - x.mean())),
               raw=True
         )

         # 4️⃣ CCI
         cci = (tp - tp_sma) / (0.015 * mean_dev)

         return cci

      except Exception as e:
         logger.error(f"Error computing CCI: {e}")
         return None

   def compute_rsi(self, df: DataFrame, price_col:str, n:int = 30):
      try:
         if df.empty:
               return None

         # 计算涨跌
         delta = df[price_col].diff()

         # 分解涨跌
         gain = delta.where(delta > 0, 0)
         loss = -delta.where(delta < 0, 0)

         # 简单平均（因为你的数据量太小，不适合 Wilder 平滑）
         avg_gain = gain.rolling(window=n).mean()
         avg_loss = loss.rolling(window=n).mean()

         # RS
         rs = avg_gain / avg_loss

         # RSI
         rsi = 100 - (100 / (1 + rs))
         return rsi
      except Exception as e:
         logger.error(f"Error computing RSI: {e}")
         return None

   def evaluate(self, context: dict):
        price_col = 'close'
        df = context["kline"]
        df['ma20'] = df[price_col].rolling(window=20).mean()
        df['ma60'] = df[price_col].rolling(window=60).mean()

        pullback_threshold = 0.03
        
        ma20 = df["ma20"].iloc[-1].round(2)
        ma60 = df["ma60"].iloc[-1].round(2)
        price = df[price_col].iloc[-1].round(2)

        if price > ma20 > ma60:
            trend =  TrendType.UPTREND
        elif price > ma60:
            trend = TrendType.NEUTRAL
        else:
            trend = TrendType.DOWNTREND

        prev_price = df[price_col].iloc[-2].round(2)
        resistance = max(df[price_col].iloc[-20:])

        pullback = (
            price < ma20 and
            price > ma60 and
            (ma20 - price) / ma20 <= pullback_threshold
        )

        breakout = (
            prev_price <= resistance and
            price > resistance * (1 + STRATEGY_CONFIG.trend.breakout_buffer)
        )
        return {
            "price": price,
            "ma20": ma20,
            "ma60": ma60,
            "trend": trend,
            "pullback": pullback,
            "breakout": breakout,
            "rsi": self.compute_rsi(df, price_col).iloc[-1].round(2),
            "cci": self.compute_cci(df, 'high', 'low', price_col).iloc[-1].round(2),
        }
