from abc import ABC, abstractmethod
from typing import Dict, Any


class SignalResult:
    def __init__(self, triggered: bool, score: float, reason: Dict[str, Any]):
        self.triggered = triggered
        self.score = score
        self.reason = reason


class BaseSignal(ABC):

    @abstractmethod
    def evaluate(self, symbol: str, context: Dict[str, Any]) -> SignalResult:
        """
        context 中包含：
        - 行情数据
        - 基本面数据
        - 事件数据
        """
        pass
