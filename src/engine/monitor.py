from loguru import logger
from .signal_engine import SignalEngine
from .index_engine import IndexEngine
from notifiers.formater.index import format_index_trend_message
from notifiers.formater.stock import format_trend_signal_message
from notifiers.manager import notification_manager
import time

class StockMonitor:
    def __init__(self, watchlist: dict, index_pool: dict, config: dict = {}):
        self.watchlist = watchlist  
        self.index_pool = index_pool
        self.config = config

    def check_index(self, index_symbol: str, index_name: str):
        index_engine = IndexEngine()
        context = index_engine.evaluate(index_symbol)
        result = context['result']
        result.update({
            "name": index_name,
        })
        message = format_index_trend_message(result)
        logger.debug(message)
        notification_manager.notify(message)


    def check_stock(self, symbol: str, stock_name: str):
        signal_engine = SignalEngine()
        context = signal_engine.evaluate(symbol)
        result = context['result']
        result.update({
            "name": stock_name,
        })
        message = format_trend_signal_message(result)
        logger.debug(message)
        notification_manager.notify(message)


    def run(self):
        for name, symbol in self.index_pool.items():
            try:
                self.check_index(symbol, name)
                time.sleep(1)
            except Exception as e:
                logger.exception(f"Error processing {symbol}: {e}")

        for name, symbol in self.watchlist.items():
            try:
                self.check_stock(symbol, name)
                time.sleep(1)
            except Exception as e:
                logger.exception(f"Error processing {symbol}: {e}")
 


if __name__ == "__main__":
    from tools.watch_list import load_watchlist
    from tools.index_tool import load_index_pool
    from config import WATCHLIST_PATH, INDEX_POOL_PATH
    watchlist = load_watchlist(WATCHLIST_PATH)
    index_pool = load_index_pool(INDEX_POOL_PATH)
    monitor = StockMonitor(
        watchlist=watchlist,
        index_pool=index_pool,
    )
    monitor.run()
