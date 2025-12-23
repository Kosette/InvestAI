from datetime import datetime
from notifiers.formater.base import get_trend_emoji

def format_index_trend_message(data: dict) -> str:
    """
    将指数趋势监控结果格式化为 Slack / 飞书通知文案
    """

    name = data.get("name")
    price = data.get("price")
    ma20 = data.get("ma20")
    ma60 = data.get("ma60")
    trend = data.get("trend")
    pullback = data.get("pullback")
    breakout = data.get("breakout")

    # === 趋势描述 ===
    trend_desc_map = {
        "risk_on": "多头趋势占优（risk_on）",
        "neutral": "震荡整理（neutral）",
        "risk_off": "趋势走弱（risk_off）"
    }
    trend_desc = trend_desc_map.get(trend, trend)

    # === 结构描述 ===
    pullback_desc = "回调结构中" if pullback else "未处于回调结构"
    breakout_desc = "突破确认" if breakout else "未出现有效突破"

    # === 综合解读 ===
    if trend == "risk_on":
        final_desc = "指数维持多头结构，对趋势策略形成正向支持。"
    elif trend == "risk_off":
        final_desc = (
            "指数趋势偏弱，整体风险偏好下降，"
            "需警惕系统性回撤风险。"
        )
    else:
        final_desc = (
            "指数处于震荡区间，多空分歧明显，"
            "对个股趋势策略的支持力度有限。"
        )

    # === 拼装消息 ===
    message = (
        f"{get_trend_emoji(trend)} 指数趋势监控\n\n"
        f"指数：{name}\n"
        f"当前点位：{price:.2f}\n"
        f"MA20 / MA60：{ma20:.2f} / {ma60:.2f}\n"
        f"趋势状态：{trend_desc}\n\n"
        f"结构观察：\n"
        f"- {pullback_desc}\n"
        f"- {breakout_desc}\n\n"
        f"环境解读：\n"
        f"{final_desc}\n\n"
    )

    return message
