import requests
import time
from typing import List, Optional
from dataclasses import dataclass
from log import logger

# GBK 解码
def gbk_decode(data: bytes) -> str:
    return data.decode("gbk", errors="ignore")


@dataclass
class SearchResult:
    security_code: str           # 数字代码
    secucode: str                # 代码+市场后缀
    name: str                    # 股票名称
    market: int                  # 市场：11=沪深，31=港股，41=美股等


class Sina:
    """新浪财经数据源（Python 版本）"""

    def __init__(self, timeout: int = 300):
        self.session = requests.Session()
        self.session.timeout = timeout

    def keyword_search(self, kw: str) -> List[SearchResult]:
        """
        关键词搜索（股票名称、代码、拼音）
        """
        url = f"https://suggest3.sinajs.cn/suggest/key={kw}"
        logger.debug(f"[Sina] KeywordSearch begin → {url}")
        begin = time.time()

        resp = self.session.get(url, timeout=self.session.timeout)
        raw = gbk_decode(resp.content)

        logger.debug(f"[Sina] raw_response={raw}, latency={int((time.time() - begin)*1000)}ms")

        # 格式示例：var suggestdata="...;"
        if "=" not in raw:
            raise ValueError(f"Invalid response: {raw}")

        data = raw.split("=", 1)[1].strip('"')

        results = []
        for line in data.split(";"):
            items = line.split(",")
            if len(items) < 9:
                continue

            # market
            try:
                market = int(items[1])
            except ValueError:
                continue

            # "sh600519" -> “600519.SH”
            raw_code = items[3]
            secucode = raw_code[2:] + "." + raw_code[:2].upper()

            results.append(
                SearchResult(
                    security_code=items[2],
                    secucode=secucode,
                    name=items[6],
                    market=market,
                )
            )

        # A 股优先：按 market 升序
        results.sort(key=lambda x: x.market)
        return results


# 简单测试
if __name__ == "__main__":
    s = Sina()
    res = s.keyword_search("maotai")
    for r in res:
        print(r)
