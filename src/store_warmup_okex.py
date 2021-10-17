import threading
import time
import traceback
import ccxt

class StoreWarpupOkex:
    def __init__(self, store=None, logger=None, min_interval=None):
        self.store = store
        self.logger = logger
        self.min_interval = min_interval

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        while True:
            time.sleep(60)
            try:
                self._loop()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.logger.error('exception ' + traceback.format_exc())
                time.sleep(60)

    def _loop(self, raise_error=False):
        intervals = [
            60,
            180,
            300,
            900,
            1800,
            3600,
            3600 * 2,
            3600 * 4,
            3600 * 6,
            3600 * 12,
            86400
        ]

        price_types = [
            None,
        ]

        okex = ccxt.okex()
        markets = okex.publicGetMarketTickers({ 'instType': 'SWAP' })['data']
        markets = list(map(lambda x: x['instId'], markets))

        for symbol in markets:
            for interval in intervals:
                if self.min_interval is not None and interval < self.min_interval:
                    continue

                for price_type in price_types:
                    try:
                        self.store.get_df_ohlcv(
                            exchange='okex',
                            market=symbol,
                            interval=interval,
                            price_type=price_type,
                            force_fetch=True
                        )
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        if raise_error:
                            raise
                        self.logger.error('exception ' + traceback.format_exc())
                        time.sleep(60)
