# server.py
from fastmcp import FastMCP
from log import logger
from tools.watch_list import add_to_watchlist, load_watchlist
from config import WATCHLIST_PATH
from utils.stock import get_fullcode, extract_code
from datacenter.market.stock import stock_data_source
from notifiers.formater.stock import format_trend_signal_message
from engine.signal_engine import SignalEngine
from agents.strategy_editor import edit_strategy
from agents.strategy_explainer import explain_strategy
from config import STRATEGY_CONFIG_PATH, STRATEGY_CONFIG
import yaml



mcp = FastMCP("InvestAI 🚀")

@mcp.tool()
async def analyze_stock_tool(code: str):
    """
    分析特定code的股票

    参数:
        code: 股票代码

    返回:
    字符串，包含股票分析结果。
    """
    fullcode = get_fullcode(code)
    logger.info(f"分析股票 {fullcode}")
    signal_engine = SignalEngine()
    context = signal_engine.evaluate(fullcode)
    result = context['result']
    logger.info(f"股票 {fullcode} 分析结果: {result}")
    data = stock_data_source.get_company_profile(extract_code(fullcode))
    stock_name = data.get('股票简称') 
    result.update({
        "name": stock_name,
    })
    message = format_trend_signal_message(result)
    return message


@mcp.tool()
async def add_watchlist_tool(code: str):
    """
    将特定股票code到关注列表

    参数:
        code: 股票代码

    返回:
    字符串，包含成功信息。
    """
    fullcode = get_fullcode(code)
    logger.info(f"get company profile for {code}")
    data = stock_data_source.get_company_profile(extract_code(fullcode))
    name = data.get('股票简称') 
    logger.info(f"添加股票 {fullcode}({name}) 到关注列表")
    add_to_watchlist(WATCHLIST_PATH, {"code": fullcode, "name": name})
    return f"{fullcode}({name}) 已添加到关注列表"

@mcp.tool()
async def get_watchlist_tool():
    """
    获取当前关注的股票列表

    返回:
    字符串，包含关注列表。
    """
    watchlist = load_watchlist(WATCHLIST_PATH)
    return watchlist


@mcp.tool()
async def explain_strategy_tool():
    """
    对当前策略配置进行可读解释

    返回:
    字符串，包含策略解释文本。
    """
    strategy = explain_strategy(STRATEGY_CONFIG)
    return strategy

@mcp.tool()
async def edit_strategy_tool(user_input: str):
    """
    根据用户输入更新策略配置

    参数:
        user_input: 用户输入的偏好或调整描述

    返回:
    字符串，包含编辑后的策略配置文本。
    """
    with open(STRATEGY_CONFIG_PATH, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
        strategy = edit_strategy(raw, user_input)
    return strategy


# ----------- 启动服务器 ------------
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8888)