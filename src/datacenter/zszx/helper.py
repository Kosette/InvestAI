from typing import List
from .client import ZszxClient, NetInflow
from log import logger


def summarize_net_inflows(inflows: List[NetInflow], days_list=(3,5,10,20,30,40)) -> dict:
    """
    返回最近 N 日主力净流入汇总
    """
    summary = {}
    for days in days_list:
        if len(inflows) >= days:
            summary[days] = sum(i.main_net_in for i in inflows[-days:])
        else:
            summary[days] = None
    return summary


