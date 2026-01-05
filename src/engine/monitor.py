import time

from loguru import logger

from agents.index_explainer import explain_index_trend
from agents.stock_explainer import explain_stock_trend
from notifiers.manager import notification_manager

from .index_engine import IndexEngine
from .signal_engine import SignalEngine


class StockMonitor:
    def __init__(self, watchlist: dict, index_pool: dict, config: dict = {}):
        self.watchlist = watchlist
        self.index_pool = index_pool
        self.config = config

    def check_index(self, index_symbol: str, index_name: str):
        index_engine = IndexEngine()
        context = index_engine.evaluate(index_symbol)
        result = context["result"]
        result.update(
            {
                "name": index_name,
            }
        )
        return result

    def check_stock(self, symbol: str, stock_name: str):
        signal_engine = SignalEngine()
        context = signal_engine.evaluate(symbol)
        result = context["result"]
        result.update(
            {
                "name": stock_name,
            }
        )
        message = explain_stock_trend(result)
        logger.debug(message)
        notification_manager.notify(f"""
        {message}\n━━━━━━━━━━━━━━━━
        """)

    def run(self):
        index_result = []
        for name, symbol in self.index_pool.items():
            try:
                result = self.check_index(symbol, name)
                index_result.append(result)
                time.sleep(1)
            except Exception as e:
                logger.exception(f"Error processing {symbol}: {e}")

        message = explain_index_trend(index_result)
        # logger.debug(message)
        notification_manager.notify(f"""
        {message}\n━━━━━━━━━━━━━━━━
        """)

        for name, symbol in self.watchlist.items():
            try:
                self.check_stock(symbol, name)
                time.sleep(1)
            except Exception as e:
                logger.exception(f"Error processing {symbol}: {e}")


if __name__ == "__main__":
    from config import INDEX_POOL_PATH, WATCHLIST_PATH
    from tools.index_tool import load_index_pool
    from tools.watch_list import load_watchlist

    watchlist = load_watchlist(WATCHLIST_PATH)
    index_pool = load_index_pool(INDEX_POOL_PATH)
    monitor = StockMonitor(
        watchlist=watchlist,
        index_pool=index_pool,
    )
    monitor.run()
