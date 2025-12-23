from apscheduler.schedulers.blocking import BlockingScheduler

from engine.monitor import StockMonitor
from config.settings import STOCK_POOL, MONITOR_CONFIG


def start_scheduler():
    monitor = StockMonitor(
        stock_pool=STOCK_POOL,
        config=MONITOR_CONFIG
    )

    scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    # 每 5 分钟扫描一次
    scheduler.add_job(
        monitor.run_once,
        trigger="interval",
        minutes=5,
        id="stock_monitor"
    )

    scheduler.start()
