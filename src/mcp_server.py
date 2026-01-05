# server.py

import yaml
from fastmcp import FastMCP

from agents.strategy_editor import edit_strategy
from agents.strategy_explainer import explain_strategy
from config import STRATEGY_CONFIG, STRATEGY_CONFIG_PATH, WATCHLIST_PATH
from datacenter.market.stock import stock_data_source
from engine.signal_engine import SignalEngine
from log import logger
from notifiers.formater.stock import format_trend_signal_message
from tools.watch_list import add_to_watchlist, load_watchlist
from utils.stock import extract_code, get_fullcode, validate_stock_code

mcp = FastMCP("InvestAI 🚀")


@mcp.tool()
async def analyze_stock_tool(code: str):
    """
    分析特定code的股票

    参数:
        code: 股票代码（6位数字，或带sh/sz前缀）

    返回:
    字符串，包含股票分析结果。
    """
    # 输入验证
    if not validate_stock_code(code):
        raise ValueError(
            f"无效的股票代码格式: {code}。请提供6位数字代码或带sh/sz前缀的代码"
        )

    try:
        fullcode = get_fullcode(code)
        logger.info(f"分析股票 {fullcode}")
        signal_engine = SignalEngine()
        context = signal_engine.evaluate(fullcode)
        result = context["result"]
        logger.info(f"股票 {fullcode} 分析完成")
        data = stock_data_source.get_company_profile(extract_code(fullcode))
        stock_name = data.get("股票简称") if data else None
        if stock_name:
            result.update({"name": stock_name})
        message = format_trend_signal_message(result)
        return message
    except ValueError as e:
        logger.error(f"参数错误: {e}")
        raise
    except Exception as e:
        logger.exception(f"分析股票 {code} 时发生错误: {e}")
        raise ValueError("分析股票失败，请稍后重试")


@mcp.tool()
async def add_watchlist_tool(code: str):
    """
    将特定股票code到关注列表

    参数:
        code: 股票代码（6位数字，或带sh/sz前缀）

    返回:
    字符串，包含成功信息。
    """
    # 输入验证
    if not validate_stock_code(code):
        raise ValueError(
            f"无效的股票代码格式: {code}。请提供6位数字代码或带sh/sz前缀的代码"
        )

    try:
        fullcode = get_fullcode(code)
        logger.info(f"获取股票信息 {fullcode}")
        data = stock_data_source.get_company_profile(extract_code(fullcode))
        name = data.get("股票简称") if data else f"未知({code})"
        logger.info(f"添加股票 {fullcode}({name}) 到关注列表")
        add_to_watchlist(WATCHLIST_PATH, {"code": fullcode, "name": name})
        return f"{fullcode}({name}) 已添加到关注列表"
    except ValueError as e:
        logger.error(f"参数错误: {e}")
        raise
    except Exception as e:
        logger.exception(f"添加股票 {code} 到关注列表时发生错误: {e}")
        raise ValueError("添加股票到关注列表失败，请稍后重试")


@mcp.tool()
async def get_watchlist_tool():
    """
    获取当前关注的股票列表

    返回:
    字符串，包含关注列表。
    """
    try:
        watchlist = load_watchlist(WATCHLIST_PATH)
        return watchlist
    except FileNotFoundError as e:
        logger.error(f"关注列表文件不存在: {e}")
        raise ValueError("关注列表文件不存在")
    except Exception as e:
        logger.exception(f"获取关注列表时发生错误: {e}")
        raise ValueError("获取关注列表失败，请稍后重试")


@mcp.tool()
async def analyze_watchlist_tool():
    """
    批量分析关注列表中的所有股票

    返回:
    字符串，包含所有股票的分析结果。
    """
    try:
        watchlist = load_watchlist(WATCHLIST_PATH)
        if not watchlist:
            return "关注列表为空"

        results = []
        for name, code in watchlist.items():
            try:
                # 验证股票代码
                if not validate_stock_code(code):
                    logger.warning(f"跳过无效的股票代码: {code}")
                    continue

                fullcode = get_fullcode(code)
                signal_engine = SignalEngine()
                context = signal_engine.evaluate(fullcode)
                result = context["result"]
                result.update({"name": name})
                message = format_trend_signal_message(result)
                results.append(f"=== {name} ({code}) ===\n{message}\n")
            except Exception as e:
                logger.error(f"分析股票 {code} 失败: {e}")
                results.append(f"=== {name} ({code}) ===\n分析失败: {str(e)}\n")

        return "\n".join(results)
    except Exception as e:
        logger.exception(f"批量分析关注列表时发生错误: {e}")
        raise ValueError("批量分析失败，请稍后重试")


@mcp.tool()
async def explain_strategy_tool():
    """
    对当前策略配置进行可读解释

    返回:
    字符串，包含策略解释文本。
    """
    try:
        strategy = explain_strategy(STRATEGY_CONFIG)
        return strategy
    except Exception as e:
        logger.exception(f"解释策略时发生错误: {e}")
        raise ValueError("解释策略失败，请稍后重试")


@mcp.tool()
async def edit_strategy_tool(user_input: str):
    """
    根据用户输入更新策略配置

    参数:
        user_input: 用户输入的偏好或调整描述

    返回:
    字符串，包含编辑后的策略配置文本。
    """
    try:
        with open(STRATEGY_CONFIG_PATH, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)
            strategy = edit_strategy(raw, user_input)
        return strategy
    except FileNotFoundError as e:
        logger.error(f"策略配置文件不存在: {e}")
        raise ValueError("策略配置文件不存在")
    except Exception as e:
        logger.exception(f"编辑策略时发生错误: {e}")
        raise ValueError("编辑策略失败，请稍后重试")


# ----------- 启动服务器 ------------
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8888)
