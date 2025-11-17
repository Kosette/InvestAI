from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional
import requests
import time


@dataclass
class CashflowData:
    """单条现金流量数据"""
    SECUCODE: str
    SECURITY_CODE: str
    SECURITY_NAME_ABBR: str
    ORG_CODE: str
    ORG_TYPE: str
    REPORT_DATE: str
    REPORT_TYPE: str
    REPORT_DATE_NAME: str
    SECURITY_TYPE_CODE: str
    NOTICE_DATE: str
    UPDATE_DATE: str
    CURRENCY: str
    SALES_SERVICES: float
    DEPOSIT_INTERBANK_ADD: float
    LOAN_PBC_ADD: float
    OFI_BF_ADD: float
    RECEIVE_ORIGIC_PREMIUM: float
    RECEIVE_REINSURE_NET: float
    INSURED_INVEST_ADD: float
    DISPOSAL_TFA_ADD: float
    RECEIVE_INTEREST_COMMISSION: float
    BORROW_FUND_ADD: float
    LOAN_ADVANCE_REDUCE: float
    REPO_BUSINESS_ADD: float
    RECEIVE_TAX_REFUND: float
    RECEIVE_OTHER_OPERATE: float
    OPERATE_INFLOW_OTHER: float
    OPERATE_INFLOW_BALANCE: float
    TOTAL_OPERATE_INFLOW: float
    BUY_SERVICES: float
    LOAN_ADVANCE_ADD: float
    PBC_INTERBANK_ADD: float
    PAY_ORIGIC_COMPENSATE: float
    PAY_INTEREST_COMMISSION: float
    PAY_POLICY_BONUS: float
    PAY_STAFF_CASH: float
    PAY_ALL_TAX: float
    PAY_OTHER_OPERATE: float
    OPERATE_OUTFLOW_OTHER: float
    OPERATE_OUTFLOW_BALANCE: float
    TOTAL_OPERATE_OUTFLOW: float
    OPERATE_NETCASH_OTHER: float
    OPERATE_NETCASH_BALANCE: float
    # 经营活动产生的现金流量净额
    NETCASH_OPERATE: float
    WITHDRAW_INVEST: float
    RECEIVE_INVEST_INCOME: float
    DISPOSAL_LONG_ASSET: float
    DISPOSAL_SUBSIDIARY_OTHER: float
    REDUCE_PLEDGE_TIMEDEPOSITS: float
    RECEIVE_OTHER_INVEST: float
    INVEST_INFLOW_OTHER: float
    INVEST_INFLOW_BALANCE: float
    TOTAL_INVEST_INFLOW: float
    CONSTRUCT_LONG_ASSET: float
    INVEST_PAY_CASH: float
    PLEDGE_LOAN_ADD: float
    OBTAIN_SUBSIDIARY_OTHER: float
    ADD_PLEDGE_TIMEDEPOSITS: float
    PAY_OTHER_INVEST: float
    INVEST_OUTFLOW_OTHER: float
    INVEST_OUTFLOW_BALANCE: float
    TOTAL_INVEST_OUTFLOW: float
    INVEST_NETCASH_OTHER: float
    INVEST_NETCASH_BALANCE: float
    # 投资活动产生的现金流量净额
    NETCASH_INVEST: float
    ACCEPT_INVEST_CASH: float
    SUBSIDIARY_ACCEPT_INVEST: float
    RECEIVE_LOAN_CASH: float
    ISSUE_BOND: float
    RECEIVE_OTHER_FINANCE: float
    FINANCE_INFLOW_OTHER: float
    FINANCE_INFLOW_BALANCE: float
    TOTAL_FINANCE_INFLOW: float
    PAY_DEBT_CASH: float
    ASSIGN_DIVIDEND_PORFIT: float
    SUBSIDIARY_PAY_DIVIDEND: float
    BUY_SUBSIDIARY_EQUITY: float
    PAY_OTHER_FINANCE: float
    SUBSIDIARY_REDUCE_CASH: float
    FINANCE_OUTFLOW_OTHER: float
    FINANCE_OUTFLOW_BALANCE: float
    TOTAL_FINANCE_OUTFLOW: float
    FINANCE_NETCASH_OTHER: float
    FINANCE_NETCASH_BALANCE: float
    # 筹资活动产生的现金流量净额
    NETCASH_FINANCE: float
    RATE_CHANGE_EFFECT: float
    CCE_ADD_OTHER: float
    CCE_ADD_BALANCE: float
    CCE_ADD: float
    BEGIN_CCE: float
    END_CCE_OTHER: float
    END_CCE_BALANCE: float
    END_CCE: float
    # 净利润
    NETPROFIT: float
    # 资产 impairment 资产 impairment
    ASSET_IMPAIRMENT: float
    # 固定资产折旧
    FA_IR_DEPR: float
    # 油气生物资产折旧
    OILGAS_BIOLOGY_DEPR: float
    # 无形资产折旧
    IR_DEPR: float
    # 资产减值准备
    IA_AMORTIZE: float
    # 长期待摊费用摊销
    LPE_AMORTIZE: float 
    # 递延收益摊销
    DEFER_INCOME_AMORTIZE: float
    # 待摊费用摊销
    PREPAID_EXPENSE_REDUCE: float
    # 待摊费用摊销
    ACCRUED_EXPENSE_ADD: float
    # 资产减值准备
    DISPOSAL_LONGASSET_LOSS: float
    # 资产减值准备
    FA_SCRAP_LOSS: float
    # 资产减值准备
    FAIRVALUE_CHANGE_LOSS: float
    # 财务费用
    FINANCE_EXPENSE: float
    # 投资损失
    INVEST_LOSS: float
    # 递延所得税资产减少
    DEFER_TAX: float
    # 递延所得税资产减少
    DT_ASSET_REDUCE: float
    # 递延所得税负债增加
    DT_LIAB_ADD: float
    # 预测负债增加
    PREDICT_LIAB_ADD: float
    # 存货减少
    INVENTORY_REDUCE: float
    # 经营活动产生的现金流量净额（其他）
    OPERATE_RECE_REDUCE: float
    # 经营活动产生的现金流量净额（增加）
    OPERATE_PAYABLE_ADD: float
    # 其他
    OTHER: float
    # 经营活动产生的现金流量净额（其他）
    OPERATE_NETCASH_OTHERNOTE: float
    # 经营活动产生的现金流量净额（余额）
    OPERATE_NETCASH_BALANCENOTE: float
    # 经营活动产生的现金流量净额（其他）
    NETCASH_OPERATENOTE: float
    # 资产处置
    DEBT_TRANSFER_CAPITAL: float
    # 资产处置
    CONVERT_BOND_1YEAR: float
    # 资产处置
    FINLEASE_OBTAIN_FA: float
    # 资产处置
    UNINVOLVE_INVESTFIN_OTHER: float
    # 期末现金及现金等价物
    END_CASH: float
    # 期初现金及现金等价物
    BEGIN_CASH: float
    # 期末现金及现金等价物
    END_CASH_EQUIVALENTS: float
    # 期初现金及现金等价物
    BEGIN_CASH_EQUIVALENTS: float
    # 现金流量增加（其他）
    CCE_ADD_OTHERNOTE: float
    # 现金流量增加（余额）
    CCE_ADD_BALANCENOTE: float
    # 现金流量增加（其他）
    CCE_ADDNOTE: float
    SALES_SERVICES_YOY: float
    DEPOSIT_INTERBANK_ADD_YOY: float
    LOAN_PBC_ADD_YOY: float
    OFI_BF_ADD_YOY: float
    RECEIVE_ORIGIC_PREMIUM_YOY: float
    RECEIVE_REINSURE_NET_YOY: float
    INSURED_INVEST_ADD_YOY: float
    DISPOSAL_TFA_ADD_YOY: float
    RECEIVE_INTEREST_COMMISSION_YOY: float
    BORROW_FUND_ADD_YOY: float
    LOAN_ADVANCE_REDUCE_YOY: float
    REPO_BUSINESS_ADD_YOY: float
    RECEIVE_TAX_REFUND_YOY: float
    RECEIVE_OTHER_OPERATE_YOY: float
    OPERATE_INFLOW_OTHER_YOY: float
    OPERATE_INFLOW_BALANCE_YOY: float
    TOTAL_OPERATE_INFLOW_YOY: float
    BUY_SERVICES_YOY: float
    LOAN_ADVANCE_ADD_YOY: float
    PBC_INTERBANK_ADD_YOY: float
    PAY_ORIGIC_COMPENSATE_YOY: float
    PAY_INTEREST_COMMISSION_YOY: float
    PAY_POLICY_BONUS_YOY: float
    PAY_STAFF_CASH_YOY: float
    PAY_ALL_TAX_YOY: float
    PAY_OTHER_OPERATE_YOY: float
    OPERATE_OUTFLOW_OTHER_YOY: float
    OPERATE_OUTFLOW_BALANCE_YOY: float
    TOTAL_OPERATE_OUTFLOW_YOY: float
    OPERATE_NETCASH_OTHER_YOY: float
    OPERATE_NETCASH_BALANCE_YOY: float
    # 经营活动产生的现金流量净额（其他）
    NETCASH_OPERATE_YOY: float
    WITHDRAW_INVEST_YOY: float
    RECEIVE_INVEST_INCOME_YOY: float
    DISPOSAL_LONG_ASSET_YOY: float
    DISPOSAL_SUBSIDIARY_OTHER_YOY: float
    REDUCE_PLEDGE_TIMEDEPOSITS_YOY: float
    RECEIVE_OTHER_INVEST_YOY: float
    INVEST_INFLOW_OTHER_YOY: float
    INVEST_INFLOW_BALANCE_YOY: float
    TOTAL_INVEST_INFLOW_YOY: float
    CONSTRUCT_LONG_ASSET_YOY: float
    INVEST_PAY_CASH_YOY: float
    PLEDGE_LOAN_ADD_YOY: float
    OBTAIN_SUBSIDIARY_OTHER_YOY: float
    ADD_PLEDGE_TIMEDEPOSITS_YOY: float
    PAY_OTHER_INVEST_YOY: float
    INVEST_OUTFLOW_OTHER_YOY: float
    INVEST_OUTFLOW_BALANCE_YOY: float
    TOTAL_INVEST_OUTFLOW_YOY: float
    INVEST_NETCASH_OTHER_YOY: float
    INVEST_NETCASH_BALANCE_YOY: float
    # 投资活动产生的现金流量净额（其他）
    NETCASH_INVEST_YOY: float
    ACCEPT_INVEST_CASH_YOY: float
    SUBSIDIARY_ACCEPT_INVEST_YOY: float
    RECEIVE_LOAN_CASH_YOY: float
    ISSUE_BOND_YOY: float
    RECEIVE_OTHER_FINANCE_YOY: float
    FINANCE_INFLOW_OTHER_YOY: float
    FINANCE_INFLOW_BALANCE_YOY: float
    TOTAL_FINANCE_INFLOW_YOY: float
    PAY_DEBT_CASH_YOY: float
    ASSIGN_DIVIDEND_PORFIT_YOY: float
    SUBSIDIARY_PAY_DIVIDEND_YOY: float
    BUY_SUBSIDIARY_EQUITY_YOY: float
    PAY_OTHER_FINANCE_YOY: float
    SUBSIDIARY_REDUCE_CASH_YOY: float
    # 投资活动产生的现金流量净额（其他）
    FINANCE_OUTFLOW_OTHER_YOY: float
    # 投资活动产生的现金流量净额（余额）
    FINANCE_OUTFLOW_BALANCE_YOY: float
    # 投资活动产生的现金流量净额（其他）
    TOTAL_FINANCE_OUTFLOW_YOY: float
    # 投资活动产生的现金流量净额（其他）
    FINANCE_NETCASH_OTHER_YOY: float
    # 投资活动产生的现金流量净额（余额）
    FINANCE_NETCASH_BALANCE_YOY: float
    # 投资活动产生的现金流量净额（其他）
    NETCASH_FINANCE_YOY: float
    # 汇率变化对现金流量的影响
    RATE_CHANGE_EFFECT_YOY: float
    # 现金流量增加（其他）
    CCE_ADD_OTHER_YOY: float
    # 现金流量增加（余额）
    CCE_ADD_BALANCE_YOY: float
    # 现金流量增加（其他）
    CCE_ADD_YOY: float
    BEGIN_CCE_YOY: float
    END_CCE_OTHER_YOY: float
    END_CCE_BALANCE_YOY: float
    END_CCE_YOY: float
    NETPROFIT_YOY: float
    ASSET_IMPAIRMENT_YOY: float
    FA_IR_DEPR_YOY: float
    OILGAS_BIOLOGY_DEPR_YOY: float
    IR_DEPR_YOY: float
    IA_AMORTIZE_YOY: float
    LPE_AMORTIZE_YOY: float
    DEFER_INCOME_AMORTIZE_YOY: float
    PREPAID_EXPENSE_REDUCE_YOY: float
    ACCRUED_EXPENSE_ADD_YOY: float
    DISPOSAL_LONGASSET_LOSS_YOY: float
    FA_SCRAP_LOSS_YOY: float
    FAIRVALUE_CHANGE_LOSS_YOY: float
    # 财务费用（其他）
    FINANCE_EXPENSE_YOY: float
    # 投资损失（其他）
    INVEST_LOSS_YOY: float
    # 递延所得税资产减少（其他）
    DEFER_TAX_YOY: float
    # 资产处置
    DT_ASSET_REDUCE_YOY: float
    # 资产处置
    DT_LIAB_ADD_YOY: float
    # 资产处置
    PREDICT_LIAB_ADD_YOY: float
    INVENTORY_REDUCE_YOY: float
    OPERATE_RECE_REDUCE_YOY: float
    OPERATE_PAYABLE_ADD_YOY: float
    OTHER_YOY: float
    OPERATE_NETCASH_OTHERNOTE_YOY: float
    OPERATE_NETCASH_BALANCENOTE_YOY: float
    NETCASH_OPERATENOTE_YOY: float
    DEBT_TRANSFER_CAPITAL_YOY: float
    CONVERT_BOND_1YEAR_YOY: float
    FINLEASE_OBTAIN_FA_YOY: float
    UNINVOLVE_INVESTFIN_OTHER_YOY: float
    END_CASH_YOY: float
    BEGIN_CASH_YOY: float
    END_CASH_EQUIVALENTS_YOY: float
    BEGIN_CASH_EQUIVALENTS_YOY: float
    CCE_ADD_OTHERNOTE_YOY: float
    CCE_ADD_BALANCENOTE_YOY: float
    CCE_ADDNOTE_YOY: float
    OPINION_TYPE: str
    OSOPINION_TYPE: str
    MINORITY_INTEREST: float
    MINORITY_INTEREST_YOY: float


@dataclass
class RespFinaCashflowData:
    pages: int
    count: int
    data: List[CashflowData]


class EastMoney:

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()

    def query_cashflow(self, secu_code: str) -> List[CashflowData]:
        base_url = "https://datacenter.eastmoney.com/securities/api/data/get"

        params = {
            "source": "HSF10",
            "client": "APP",
            "type": "RPT_F10_FINANCE_GCASHFLOW",
            "sty": "APP_F10_GCASHFLOW",
            "filter": f'(SECUCODE="{secu_code.upper()}")',
            "ps": "10",
            "sr": "-1",
            "st": "REPORT_DATE",
        }

        start = time.time()
        resp = self.session.get(base_url, params=params, timeout=10)
        latency = (time.time() - start) * 1000

        if not resp.ok:
            raise RuntimeError(f"HTTP error {resp.status_code}: {resp.text}")

        payload = resp.json()

        if payload.get("code") != 0:
            raise RuntimeError(f"API error: {payload}")

        result = payload["result"]

        data_list = [
            CashflowData(**item)
            for item in result["data"]
        ]

        print(f"Query time: {latency:.2f} ms")

        return data_list



if __name__ == "__main__":
    em = EastMoney()
    data = em.query_cashflow("000958.SZ")
    print(data)
