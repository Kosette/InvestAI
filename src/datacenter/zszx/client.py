import requests
from typing import List
from log import logger
from datetime import datetime
from dataclasses import dataclass

# ---------- 数据模型 ----------
@dataclass
class NetInflow:
    date: str
    close_price: float
    main_net_in: float
    huge_net_in: float
    big_net_in: float
    mid_net_in: float
    small_net_in: float
    total_net_in: float

    @classmethod
    def from_dict(cls, data: dict):
        # 自动将字符串转 float，出错用 0.0
        def parse_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return 0.0
        return cls(
            date=data.get("TrdDt", ""),
            close_price=parse_float(data.get("ClsPrc")),
            main_net_in=parse_float(data.get("MainMnyNetIn")),
            huge_net_in=parse_float(data.get("HugeNetIn")),
            big_net_in=parse_float(data.get("BigNetIn")),
            mid_net_in=parse_float(data.get("MidNetIn")),
            small_net_in=parse_float(data.get("SmallNetIn")),
            total_net_in=parse_float(data.get("TtlMnyNetIn")),
        )

# ---------- 核心接口 ----------
class ZszxClient:
    BASE_URL = "https://zszx.cmschina.com/pcnews/f10/stkcnmnyflow"

    def __init__(self, timeout: int = 10):
        self.session = requests.Session()
        self.timeout = timeout

    def get_net_inflows(self, stock_code: str, start_date: str, end_date: str) -> List[NetInflow]:
        """
        查询股票资金净流入
        stock_code: e.g., "000001.SZ"
        start_date, end_date: "YYYY-MM-DD"
        """
        if "." not in stock_code:
            raise ValueError("Invalid stock_code, must be like '000001.SZ'")
        code, market = stock_code.split(".")
        market_code = "1" if market.upper() == "SH" else "0"

        params = {
            "scode": code,
            "ecode": market_code,
            "dateStart": start_date,
            "dateEnd": end_date,
        }

        resp = self.session.get(self.BASE_URL, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        if data.get("code") != 0:
            raise RuntimeError(f"API Error: {data}")

        inflows = [NetInflow.from_dict(item) for item in data.get("data", [])]
        # 按日期升序
        inflows.sort(key=lambda x: datetime.strptime(x.date, "%Y%m%d"))
        return inflows

# ---------- 辅助方法 ----------


# ---------- 使用示例 ----------
if __name__ == "__main__":
    client = ZszxClient()

    stock = "000001.SZ"
    inflows = client.get_net_inflows(stock, "2025-11-01", "2025-11-17")
    logger.info(inflows)
