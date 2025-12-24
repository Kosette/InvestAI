from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from engine.monitor import StockMonitor
from tools.index_tool import load_index_pool
from tools.watch_list import load_watchlist
from config import WATCHLIST_PATH, INDEX_POOL_PATH


def start_scheduler():
    watchlist = load_watchlist(WATCHLIST_PATH)
    index_pool = load_index_pool(INDEX_POOL_PATH)   
    monitor = StockMonitor(
        watchlist=watchlist,
        index_pool=index_pool,
    )
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        monitor,
        CronTrigger(hour=14, minute=0)
    )
    scheduler.start()
