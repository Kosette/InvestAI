from abc import ABC, abstractmethod
from typing import Dict, Any
from enum import Enum

class TrendType(Enum):
    UPTREND = "上升趋势，可以考虑买入"
    NEUTRAL = "建议观望"
    DOWNTREND = "弱势，请注意避险"


class BaseSignal(ABC):

    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> dict:
        """
        context 中包含：
        - 行情数据
        - 基本面数据
        - 事件数据
        """
        pass
