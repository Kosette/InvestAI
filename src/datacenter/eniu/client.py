# ------------------------------
# 亿牛 API 客户端
# ------------------------------
import requests
from dataclasses import dataclass
from typing import List
import numpy as np
from datetime import datetime


@dataclass
class HistoricalPrice:
    dates: List[str]
    prices: List[float]

    @staticmethod
    def _normalize_date(date: str) -> str:
        """把 20251114 或 2025-11-14 都转成 YYYY-MM-DD."""
        if "-" in date:
            return date
        return datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")

    @classmethod
    def from_api(cls, data: dict):
        return cls(
            dates=[cls._normalize_date(d) for d in data.get("date", [])],
            prices=data.get("price", []),
        )

    # --------------------------
    # 去年12月最后一个交易日的价格
    # --------------------------
    def last_year_final_price(self) -> float:
        if not self.dates:
            return 0.0
        
        target_year = datetime.now().year - 1
        prefix = f"{target_year}-12-"

        # 从最新向前找
        for date, price in reversed(list(zip(self.dates, self.prices))):
            if date.startswith(prefix):
                return price

        return 0.0

    # --------------------------
    # 历史波动率（支持日、周、月、年）
    # --------------------------
    def historical_volatility(self, period: str = "DAY") -> float:
        if len(self.prices) < 2:
            raise ValueError("Insufficient historical prices")

        prices = np.array(self.prices, dtype=float)

        # 计算 log return：ln(p_t / p_{t-1})
        log_returns = np.diff(np.log(prices))

        # 标准差
        stdev = np.std(log_returns)

        period = period.upper()
        factor = {
            "DAY": 1,
            "WEEK": 5,
            "MONTH": 21.75,
            "YEAR": 250,
        }.get(period, 250)

        vol = stdev * np.sqrt(factor)
        if np.isnan(vol):
            raise ValueError("Volatility is NaN")

        return float(vol)


class EniuClient:
    BASE_URL = "https://eniu.com/chart/pricea/{}/t/all"

    def __init__(self, timeout=15):
        self.session = requests.Session()
        self.timeout = timeout

    @staticmethod
    def to_path_code(stock_code: str) -> str:
        """
        '000001.SZ' → 'sz000001'
        """
        if "." not in stock_code:
            raise ValueError("Stock code must be like '000001.SZ'")
        code, market = stock_code.split(".")
        return market.lower() + code

    def get_historical_price(self, stock_code: str) -> HistoricalPrice:
        path_code = self.to_path_code(stock_code)
        url = self.BASE_URL.format(path_code)

        resp = self.session.get(url, timeout=self.timeout)
        resp.raise_for_status()

        data = resp.json()
        return HistoricalPrice.from_api(data)


if __name__ == "__main__":
    eniu = EniuClient()

    stock = "000001.SZ"
    hp = eniu.get_historical_price(stock)

    print("去年最后一个交易日价格:", hp.last_year_final_price())
    print("年化波动率:", hp.historical_volatility("YEAR"))