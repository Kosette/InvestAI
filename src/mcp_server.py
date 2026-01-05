# server.py
from fastmcp import FastMCP, Context
from log import logger
from tools.watch_list import add_to_watchlist, load_watchlist
from config import WATCHLIST_PATH
from utils.stock import get_fullcode, extract_code, validate_stock_code
from datacenter.market.stock import stock_data_source
from notifiers.formater.stock import format_trend_signal_message
from engine.signal_engine import SignalEngine
from agents.strategy_editor import edit_strategy
from agents.strategy_explainer import explain_strategy
from config import STRATEGY_CONFIG_PATH, STRATEGY_CONFIG
import yaml
import os
from functools import wraps
from typing import Optional


mcp = FastMCP("InvestAI 🚀")

# 获取 MCP API Token
MCP_API_TOKEN = os.getenv("MCP_API_TOKEN", "")

def extract_token_from_headers(ctx: Optional[Context]) -> Optional[str]:
    """
    从HTTP请求头中提取认证token
    
    支持以下格式：
    1. Authorization: Bearer <token>
    2. X-API-Key: <token>
    
    参数:
        ctx: FastMCP 上下文对象
    
    返回:
        提取的token，如果未找到则返回None
    """
    if ctx is None or not hasattr(ctx, 'request_context'):
        return None
    
    request_ctx = ctx.request_context
    headers = getattr(request_ctx, 'headers', {})
    
    # 尝试从 Authorization header 获取 Bearer token
    auth_header = headers.get('authorization') or headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header[7:].strip()  # 移除 "Bearer " 前缀
    
    # 尝试从 X-API-Key header 获取
    api_key = headers.get('x-api-key') or headers.get('X-API-Key')
    if api_key:
        return api_key.strip()
    
    return None

def require_auth(func):
    """
    Token认证装饰器
    
    从HTTP请求头中提取token并验证：
    - Authorization: Bearer <token>
    - X-API-Key: <token>
    
    如果未设置MCP_API_TOKEN环境变量，仅记录警告不拦截（向后兼容）
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 如果没有设置 token，跳过验证（向后兼容）
        if not MCP_API_TOKEN:
            logger.warning("MCP_API_TOKEN 未设置，建议配置以增强安全性")
            return await func(*args, **kwargs)
        
        # 从上下文中提取token
        ctx = kwargs.get('ctx')
        token = extract_token_from_headers(ctx)
        
        # 验证token
        if token != MCP_API_TOKEN:
            logger.warning(f"认证失败：token不匹配")
            raise ValueError("认证失败：无效的 API token。请在请求头中设置 'Authorization: Bearer <token>' 或 'X-API-Key: <token>'")
        
        logger.info("Token认证通过")
        return await func(*args, **kwargs)
    return wrapper

@mcp.tool()
@require_auth
async def analyze_stock_tool(code: str, ctx: Context = None):
    """
    分析特定code的股票

    参数:
        code: 股票代码（6位数字，或带sh/sz前缀）

    认证:
        需要在HTTP请求头中提供token（如果设置了MCP_API_TOKEN环境变量）
        - Authorization: Bearer <token>
        - X-API-Key: <token>

    返回:
    字符串，包含股票分析结果。
    """
    # 输入验证
    if not validate_stock_code(code):
        raise ValueError(f"无效的股票代码格式: {code}。请提供6位数字代码或带sh/sz前缀的代码")
    
    try:
        fullcode = get_fullcode(code)
        logger.info(f"分析股票 {fullcode}")
        signal_engine = SignalEngine()
        context = signal_engine.evaluate(fullcode)
        result = context['result']
        logger.info(f"股票 {fullcode} 分析完成")
        data = stock_data_source.get_company_profile(extract_code(fullcode))
        stock_name = data.get('股票简称') if data else None
        if stock_name:
            result.update({"name": stock_name})
        message = format_trend_signal_message(result)
        return message
    except ValueError as e:
        logger.error(f"参数错误: {e}")
        raise
    except Exception as e:
        logger.exception(f"分析股票 {code} 时发生错误: {e}")
        raise ValueError(f"分析股票失败，请稍后重试")


@mcp.tool()
@require_auth
async def add_watchlist_tool(code: str, ctx: Context = None):
    """
    将特定股票code到关注列表

    参数:
        code: 股票代码（6位数字，或带sh/sz前缀）

    认证:
        需要在HTTP请求头中提供token（如果设置了MCP_API_TOKEN环境变量）
        - Authorization: Bearer <token>
        - X-API-Key: <token>

    返回:
    字符串，包含成功信息。
    """
    # 输入验证
    if not validate_stock_code(code):
        raise ValueError(f"无效的股票代码格式: {code}。请提供6位数字代码或带sh/sz前缀的代码")
    
    try:
        fullcode = get_fullcode(code)
        logger.info(f"获取股票信息 {fullcode}")
        data = stock_data_source.get_company_profile(extract_code(fullcode))
        name = data.get('股票简称') if data else f"未知({code})"
        logger.info(f"添加股票 {fullcode}({name}) 到关注列表")
        add_to_watchlist(WATCHLIST_PATH, {"code": fullcode, "name": name})
        return f"{fullcode}({name}) 已添加到关注列表"
    except ValueError as e:
        logger.error(f"参数错误: {e}")
        raise
    except Exception as e:
        logger.exception(f"添加股票 {code} 到关注列表时发生错误: {e}")
        raise ValueError(f"添加股票到关注列表失败，请稍后重试")

@mcp.tool()
@require_auth
async def get_watchlist_tool(ctx: Context = None):
    """
    获取当前关注的股票列表

    认证:
        需要在HTTP请求头中提供token（如果设置了MCP_API_TOKEN环境变量）
        - Authorization: Bearer <token>
        - X-API-Key: <token>

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
        raise ValueError(f"获取关注列表失败，请稍后重试")


@mcp.tool()
@require_auth
async def analyze_watchlist_tool(ctx: Context = None):
    """
    批量分析关注列表中的所有股票

    认证:
        需要在HTTP请求头中提供token（如果设置了MCP_API_TOKEN环境变量）
        - Authorization: Bearer <token>
        - X-API-Key: <token>

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
                result = context['result']
                result.update({"name": name})
                message = format_trend_signal_message(result)
                results.append(f"=== {name} ({code}) ===\n{message}\n")
            except Exception as e:
                logger.error(f"分析股票 {code} 失败: {e}")
                results.append(f"=== {name} ({code}) ===\n分析失败: {str(e)}\n")
        
        return "\n".join(results)
    except Exception as e:
        logger.exception(f"批量分析关注列表时发生错误: {e}")
        raise ValueError(f"批量分析失败，请稍后重试")


@mcp.tool()
@require_auth
async def explain_strategy_tool(ctx: Context = None):
    """
    对当前策略配置进行可读解释

    认证:
        需要在HTTP请求头中提供token（如果设置了MCP_API_TOKEN环境变量）
        - Authorization: Bearer <token>
        - X-API-Key: <token>

    返回:
    字符串，包含策略解释文本。
    """
    try:
        strategy = explain_strategy(STRATEGY_CONFIG)
        return strategy
    except Exception as e:
        logger.exception(f"解释策略时发生错误: {e}")
        raise ValueError(f"解释策略失败，请稍后重试")

@mcp.tool()
@require_auth
async def edit_strategy_tool(user_input: str, ctx: Context = None):
    """
    根据用户输入更新策略配置

    参数:
        user_input: 用户输入的偏好或调整描述

    认证:
        需要在HTTP请求头中提供token（如果设置了MCP_API_TOKEN环境变量）
        - Authorization: Bearer <token>
        - X-API-Key: <token>

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
        raise ValueError(f"编辑策略失败，请稍后重试")


@mcp.tool()
async def health_check():
    """
    健康检查端点，用于容器健康检查

    返回:
    字符串，包含服务状态。
    """
    return "OK"


# ----------- 启动服务器 ------------
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8888)