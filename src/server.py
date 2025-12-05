# server.py
from fastmcp import FastMCP
from .config import WATCHLIST_PATH
import json



mcp = FastMCP("InvestAI 🚀")

@app.tool()
async def add_watchlist(item: dict):
    """
    添加股票到观察列表
    """
    current_watchlist = []
    with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
        current_watchlist = json.load(f)
    current_watchlist.append(item)
    with open(WATCHLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(current_watchlist, f, ensure_ascii=False, indent=4)
    return {"status": "ok", "message": f"Watchlist updated: {WATCHLIST_PATH}"}


# ----------- 启动服务器 ------------
if __name__ == "__main__":
    mcp.run()