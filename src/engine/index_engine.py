from datacenter.market.index import index_data_source
from loguru import logger
from signals.structrue_signal import StructureSignal
from notifiers.formater.index import format_index_trend_message


class IndexEngine:
    def evaluate(self, index_code: str):
        context = {}
        context["kline"] = index_data_source.get_kline(index_code)
        signal = StructureSignal()
        context["result"] = signal.evaluate(context)
        return context


if __name__ == "__main__":
    index_engine = IndexEngine()
    context = index_engine.evaluate("sh000300")
    result = context["result"]
    result.update(
        {
            "name": "沪深300",
        }
    )
    message = format_index_trend_message(result)
    logger.debug(message)
