from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from engine.monitor import StockMonitor
from config import WATCHLIST, INDEX_POOL


def start_scheduler():
    monitor = StockMonitor(
        watchlist=WATCHLIST,
        index_pool=INDEX_POOL,
    )

    scheduler = BackgroundScheduler()

    scheduler.add_job(
        monitor,
        CronTrigger(hour=14, minute=0)
    )


    scheduler.start()
