# server.py
from fastmcp import FastMCP
from log import logger
from tools.watch_list import add_to_watchlist
from config import WATCHLIST_PATH
from utils.code import get_fullcode
from datacenter.market.stock import stock_data_source

mcp = FastMCP("InvestAI 🚀")

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
    data = stock_data_source.get_company_profile(fullcode)
    name = data.get('股票简称') 
    logger.info(f"添加股票 {fullcode}({name}) 到监控列表")
    add_to_watchlist(WATCHLIST_PATH, {"code": fullcode, "name": name})
    return {"status": "ok", "message": f"{fullcode}({name}) 已添加到监控列表"}


# ----------- 启动服务器 ------------
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8888)