from datacenter.market.index import index_data_source
from loguru import logger
from signals.structrue_signal import StructureSignal
from notifiers.formater.index import format_index_trend_message

INDEX_CODES = {
    "沪深300": "sh000300",
    # "中证500": "sh000905",
    # "中证1000": "sh000852",
}


class IndexEngine:
    def __init__(self, index_codes: dict = INDEX_CODES):
        self.index_codes = index_codes

    def evaluate(self, index_code: str):
        context = {}
        context["kline"] = index_data_source.get_kline(index_code)
        signal = StructureSignal()
        context['result'] = signal.evaluate(context)
        return context


if __name__ == "__main__":
    index_engine = IndexEngine()
    context = index_engine.evaluate("sh000300")
    result = context['result']
    result.update({
        "name": "沪深300",
    })
    message = format_index_trend_message(result)
    logger.debug(message)
