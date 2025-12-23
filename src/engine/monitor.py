from loguru import logger
from engine.signal_engine import SignalEngine


class IndexMonitor:
    def __init__(self, stock_pool, config):
        self.stock_pool = stock_pool
        self.config = config
        self.signal_engine = SignalEngine(config)

    def run_once(self):
        """
        单次扫描（可被 scheduler 调用）
        """
        for symbol in self.stock_pool:
            try:
                self._check_symbol(symbol)
            except Exception as e:
                logger.exception(f"Error processing {symbol}: {e}")

    def _check_symbol(self, symbol: str):
        data = load_market_data(symbol)
        indicators = calc_indicators(data)

        prices = data["close"]
        volumes = data["volume"]

        market_ctx = {
            "prices": prices,
            "volumes": volumes,
            "ma20": indicators["ma20"],
            "ma60": indicators["ma60"],
            "resistance": calc_resistance(prices),
            "volume_ma": indicators["volume_ma"],
            "rsi": indicators["rsi"],
            "cci": indicators["cci"],
        }

        result = self.signal_engine.evaluate(market_ctx)

        if result["triggered"]:
            message = self._format_message(symbol, market_ctx, result)
            send_slack_message(message)


class StockMonitor:
    def __init__(self, stock_pool, config):
        self.stock_pool = stock_pool
        self.config = config
        self.signal_engine = SignalEngine(config)

    def run_once(self):
        """
        单次扫描（可被 scheduler 调用）
        """
        for symbol in self.stock_pool:
            try:
                self._check_symbol(symbol)
            except Exception as e:
                logger.exception(f"Error processing {symbol}: {e}")

    def _check_symbol(self, symbol: str):
        data = load_market_data(symbol)
        indicators = calc_indicators(data)

        prices = data["close"]
        volumes = data["volume"]

        market_ctx = {
            "prices": prices,
            "volumes": volumes,
            "ma20": indicators["ma20"],
            "ma60": indicators["ma60"],
            "resistance": calc_resistance(prices),
            "volume_ma": indicators["volume_ma"],
            "rsi": indicators["rsi"],
            "cci": indicators["cci"],
        }

        result = self.signal_engine.evaluate(market_ctx)

        if result["triggered"]:
            message = self._format_message(symbol, market_ctx, result)
            send_slack_message(message)

 
