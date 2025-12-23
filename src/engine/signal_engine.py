from signals.structrue_signal import StructureSignal
from signals.timing_signal import TimingSignal
from datacenter.market.stock import stock_data_source
from loguru import logger
from notifiers.formater.stock import format_trend_signal_message


class SignalEngine:

    def evaluate(self, symbol: str):
        context = {}
        context["kline"] = stock_data_source.get_kline(symbol)
        structure_signal = StructureSignal()
        structure_data = structure_signal.evaluate(context)
        logger.debug(structure_data)
        signal = TimingSignal()
        data = signal.evaluate(context)
        structure_data.update(data)
        context['result'] = structure_data
        return context


if __name__ == "__main__":
    signal_engine = SignalEngine()
    context = signal_engine.evaluate("sh603192")
    result = context['result']
    result['name'] = '润本股份'
    logger.info(format_trend_signal_message(result))
