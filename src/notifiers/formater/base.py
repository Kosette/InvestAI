from signals.base import TrendType

def get_trend_emoji(trend: TrendType) -> str:
    """
    根据市场/趋势状态返回对应 Emoji
    """
    emoji_map = {
        TrendType.UPTREND: "📈",
        TrendType.NEUTRAL: "📊",
        TrendType.DOWNTREND: "📉",
    }
    return emoji_map.get(trend, "❔")

