from notifiers.formater.base import get_trend_emoji
from signals.base import TrendType
from config import STRATEGY_CONFIG
from utils.json import to_pretty_json


def format_trend_signal_message(data: dict) -> str:
    """
    将趋势监控结果格式化为 Slack / 飞书通知文案
    """

    name = data.get("name")
    price = data.get("price")
    ma_short = data.get("ma_short")
    ma_long = data.get("ma_long")
    trend = data.get("trend")
    pullback = data.get("pullback")
    breakout = data.get("breakout")
    rsi = data.get("rsi")
    cci = data.get("cci")

    # === 结构判断 ===
    pullback_desc = "已形成" if pullback else "未形成"
    breakout_desc = "已确认" if breakout else "未确认"

    # === RSI / CCI 择时描述 ===
    rsi_ok = STRATEGY_CONFIG.rsi.min <= rsi <= STRATEGY_CONFIG.rsi.max
    cci_ok = STRATEGY_CONFIG.cci.min <= cci <= STRATEGY_CONFIG.cci.max

    if rsi_ok:
        rsi_desc = "处于有效区间"
    elif rsi < STRATEGY_CONFIG.rsi.min:
        rsi_desc = "偏弱"
    else:
        rsi_desc = "偏强"

    if cci_ok:
        cci_desc = "处于正常波动区间"
    elif cci < STRATEGY_CONFIG.cci.min:
        cci_desc = "超卖"
    else:
        cci_desc = "过热"

    # === 综合判断 ===
    if trend == TrendType.UPTREND and (pullback or breakout) and rsi_ok and cci_ok:
        final_desc = "满足趋势与择时条件，具备趋势型买入信号。"
    else:
        final_desc = (
            "当前趋势或结构 / 择时条件不满足，"
            "暂不具备趋势型买入条件，建议继续观望。"
        )

    # === 拼装消息 ===
    message = (
        f"股票名称：{name}{get_trend_emoji(trend)}\n"
        f"当前价格：{price:.2f}\n"
        f"MA_{STRATEGY_CONFIG.trend.moving_averages.short} / MA{STRATEGY_CONFIG.trend.moving_averages.long}：{ma_short:.2f} / {ma_long:.2f}\n"
        f"市场趋势：{trend.value}\n\n"
        f"结构判断：\n"
        f"- 回调形态：{pullback_desc}\n"
        f"- 突破形态：{breakout_desc}\n\n"
        f"择时指标（软约束）：\n"
        f"- RSI：{rsi:.1f}（{rsi_desc}）\n"
        f"- CCI：{cci:.1f}（{cci_desc}）\n\n"
        f"综合判断：\n"
        f"{final_desc}\n\n"
        f"━━━━━━━━━━━━━━━━"
    )

    return message
