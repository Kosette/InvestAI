from notifiers.formater.base import get_trend_emoji
from signals.base import TrendType
from config import STRATEGY_CONFIG
from utils.json import to_pretty_json



def format_index_trend_message(data: dict) -> str:
    """
    将指数趋势监控结果格式化为 Slack / 飞书通知文案
    """

    name = data.get("name")
    price = data.get("price")
    ma_short = data.get("ma_short")
    ma_long = data.get("ma_long")
    trend = data.get("trend")
    pullback = data.get("pullback")
    breakout = data.get("breakout")


    # === 结构描述 ===
    pullback_desc = "回调结构中" if pullback else "未处于回调结构"
    breakout_desc = "突破确认" if breakout else "未出现有效突破"

    # === 综合解读 ===
    if trend == TrendType.UPTREND:
        final_desc = "指数维持多头结构，对趋势策略形成正向支持。"
    elif trend == TrendType.DOWNTREND:
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
        f"指数：{name}{get_trend_emoji(trend)}\n"
        f"当前点位：{price:.2f}\n"
        f"MA_{STRATEGY_CONFIG.trend.moving_averages.short} / MA{STRATEGY_CONFIG.trend.moving_averages.long}：{ma_short:.2f} / {ma_long:.2f}\n"
        f"趋势状态：{trend.value}\n\n"
        f"结构观察：\n"
        f"- {pullback_desc}\n"
        f"- {breakout_desc}\n\n"
        f"环境解读：\n"
        f"{final_desc}\n\n"
        f"━━━━━━━━━━━━━━━━"
    )

    return message
