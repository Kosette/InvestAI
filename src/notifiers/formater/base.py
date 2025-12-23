def get_trend_emoji(trend: str) -> str:
    """
    根据市场/趋势状态返回对应 Emoji
    """
    emoji_map = {
        "risk_on": "📈",
        "neutral": "📊",
        "risk_off": "📉",
    }
    return emoji_map.get(trend, "❔")