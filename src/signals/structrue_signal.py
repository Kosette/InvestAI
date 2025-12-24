from signals.base import BaseSignal
from signals.base import TrendType

class StructureSignal(BaseSignal):

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
            price > resistance * 1.005
        )
        return {
            "price": price,
            "ma20": ma20,
            "ma60": ma60,
            "trend": trend,
            "pullback": pullback,
            "breakout": breakout,
        }
