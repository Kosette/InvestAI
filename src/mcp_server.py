# server.py
from fastmcp import FastMCP
from log import logger
from tools.watch_list import add_to_watchlist, load_watchlist
from config import WATCHLIST_PATH
from utils.stock import get_fullcode
from datacenter.market.stock import stock_data_source
from notifiers.formater.stock import format_trend_signal_message
from engine.signal_engine import SignalEngine
from agents.strategy_editor import edit_strategy
from agents.strategy_explainer import explain_strategy
from config import STRATEGY_CONFIG_PATH, STRATEGY_CONFIG
import yaml



mcp = FastMCP("InvestAI 🚀")

@mcp.tool()
async def analyze(code: str):
    """
    分析股票code

    参数:
        code: 股票代码

    返回:
    字典，包含股票分析结果。
    """
    fullcode = get_fullcode(code)
    signal_engine = SignalEngine()
    context = signal_engine.evaluate(fullcode)
    result = context['result']
    data = stock_data_source.get_company_profile(code)
    stock_name = data.get('股票简称') 
    result.update({
        "name": stock_name,
    })
    message = format_trend_signal_message(result)
    return {"status": "ok", "message": message}


@mcp.tool()
async def add_watchlist(code: str):
    """
    将添加股票code到观察列表

    参数:
        code: 股票代码

    返回:
    字典，包含成功信息。
    """
    fullcode = get_fullcode(code)
    data = stock_data_source.get_company_profile(code)
    name = data.get('股票简称') 
    logger.info(f"添加股票 {fullcode}({name}) 到监控列表")
    add_to_watchlist(WATCHLIST_PATH, {"code": fullcode, "name": name})
    return {"status": "ok", "message": f"{fullcode}({name}) 已添加到监控列表"}

@mcp.tool()
async def get_watchlist():
    """
    获取当前观察列表

    返回:
    字典，包含观察列表。
    """
    watchlist = load_watchlist(WATCHLIST_PATH)
    return {"status": "ok", "watchlist": watchlist}


@mcp.tool()
async def explain_strategy():
    """
    解释策略

    返回:
    字典，包含策略解释。
    """
    strategy = explain_strategy(STRATEGY_CONFIG)
    return {"status": "ok", "strategy": strategy}

@mcp.tool()
async def edit_strategy(user_input: str):
    """
    编辑策略

    参数:
        user_input: 用户输入的策略描述

    返回:
    字典，包含编辑后的策略。
    """
    with open(STRATEGY_CONFIG_PATH, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
        strategy = edit_strategy(raw, user_input)
    return {"status": "ok", "strategy": strategy}


# ----------- 启动服务器 ------------
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8888)