import requests
from dataclasses import dataclass, field
from typing import List, Dict, Any


# -----------------------------
# 数据结构（dataclasses）
# -----------------------------

@dataclass
class MainForm:
    type: str
    name: str
    ratio: str
    amount: str
    ratio_value: str


@dataclass
class CompanyProfile:
    secucode: str = ""
    name: str = ""
    industry: str = ""
    concept: str = ""
    profile: str = ""
    main_business: str = ""
    keywords: List[str] = field(default_factory=list)
    main_forms: List[MainForm] = field(default_factory=list)

    def main_forms_string(self) -> str:
        groups = {"1": [], "2": [], "3": []}
        for m in self.main_forms:
            groups.setdefault(m.type, []).append(m)

        def fmt(title, items):
            if not items:
                return f"{title}\n    暂无数据"
            return title + "".join(f"\n    {m.name}: {m.ratio}" for m in items)

        return "\n".join([
            fmt("按行业:", groups["1"]),
            fmt("按产品:", groups["3"]),
            fmt("按地区:", groups["2"]),
        ])

    def profile_string(self):
        return (
            f"公司简介:\n{self.profile}\n"
            f"主营业务:\n    {self.main_business}\n"
            f"所属概念:\n    {self.concept}"
        )

    def keywords_string(self):
        return ";".join(self.keywords)


# -----------------------------
# EastMoney API 客户端
# -----------------------------

class EastMoneyClient:

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()

    # 生成 fc 参数
    def _get_fc(self, code: str) -> str:
        c = code.upper()
        if c.endswith(".SH"):
            return c.replace(".SH", "01")
        if c.endswith(".SZ"):
            return c.replace(".SZ", "02")
        return c

    # 请求封装
    def _post(self, url: str, data):
        resp = self.session.post(url, json=data, timeout=10)
        resp.encoding = "utf-8"  # 强制按 UTF-8 解码
        resp.raise_for_status()
        return resp.json()

    def _get(self, url: str, params):
        resp = self.session.get(url, params=params, timeout=10)
        resp.encoding = "utf-8"
        resp.raise_for_status()
        return resp.json()


    # -----------------------------
    # 主逻辑：获取公司资料 + 操盘必读
    # -----------------------------
    def query_company_profile(self, secu_code: str) -> CompanyProfile:
        fc = self._get_fc(secu_code)
        profile = CompanyProfile()

        # ------ 基本资料 ------
        jbzl_url = "https://emh5.eastmoney.com/api/GongSiGaiKuang/GetJiBenZiLiao"
        jbzl = self._post(jbzl_url, {"fc": fc})

        if jbzl.get("Status") != 0:
            raise ValueError(f"基本资料查询失败: {jbzl.get('Message')}")

        base = jbzl["Result"]["JiBenZiLiao"]
        profile.secucode = base.get("SecurityCode")
        profile.name = base.get("CompanyName")
        profile.industry = base.get("Industry")
        profile.concept = base.get("Block")
        profile.profile = base.get("CompRofile")
        profile.main_business = base.get("MainBusiness")

        # ------ 操盘必读 ------
        cpbd_url = "https://emh5.eastmoney.com/api/CaoPanBiDu/GetCaoPanBiDuPart2Get"
        cpbd = self._get(cpbd_url, {"fc": fc})

        if cpbd.get("Status") != 0:
            raise ValueError(f"操盘必读查询失败: {cpbd.get('Message')}")

        # 关键词
        for item in cpbd["Result"].get("TiCaiXiangQingList", []):
            profile.keywords.append(item.get("KeyWord", ""))

        # 主营构成
        for item in cpbd["Result"].get("ZhuYingGouChengList", []):
            profile.main_forms.append(
                MainForm(
                    type=item.get("ReportType", ""),
                    name=item.get("MainForm", ""),
                    ratio=item.get("MainIncomeRatio", ""),
                    amount=item.get("MainIncome", ""),
                    ratio_value=item.get("MainIncomeRatioChart", "")
                )
            )

        return profile


# -----------------------------
# 使用示例
# -----------------------------
if __name__ == "__main__":
    client = EastMoneyClient()
    p = client.query_company_profile("600519.SH")

    print(p.profile_string())
    print()
    print(p.main_forms_string())
    print()
    print("关键词:", p.keywords_string())
