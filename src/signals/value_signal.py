from signals.base import BaseSignal, SignalResult


class ValueSignal(BaseSignal):

    def evaluate(self, symbol: str, context: dict) -> SignalResult:
        fundamentals = context["fundamentals"]

        pe = fundamentals["pe"]
        historical_pe_low = fundamentals["pe_percentile"] < 0.2

        triggered = pe < fundamentals["industry_pe"] and historical_pe_low

        return SignalResult(
            triggered=triggered,
            score=0.7 if triggered else 0.0,
            reason={
                "pe": pe,
                "pe_percentile": fundamentals["pe_percentile"],
                "logic": "估值低于行业 + 历史低分位"
            }
        )
