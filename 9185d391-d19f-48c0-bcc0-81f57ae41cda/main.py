from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import EMA, VWAP
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):

    def __init__(self):
        self.ticker = "AAPL"  # Ticker to trade
        self.data_list = [Asset(self.ticker)]
        self.vwap_length = 9  # Period for VWAP, match with the market session or adjust as per strategy need

    @property
    def interval(self):
        return "1day"  # Using daily intervals for this strategy, adjust as needed

    @property
    def assets(self):
        return [self.ticker]

    @property
    def data(self):
        return self.data_list

    def run(self, data):
        # Initial allocation is empty
        allocation_dict = {self.ticker: 0}

        # Ensure there's enough data for both EMA and VWAP calculations
        if len(data["ohlcv"]) < self.vwap_length:
            log(f"Not enough data for VWAP calculation for {self.ticker}")
            return TargetAllocation(allocation_dict)

        # Calculating 9-period EMA and VWAP
        ema_values = EMA(self.ticker, data["ohlcv"], length=9)
        vwap_values = VWAP(self.ticker, data["ohlcv"], length=self.vwap_length)

        # Ensure we have the calculations
        if ema_values is None or vwap_values is None:
            log(f"Unable to calculate EMA or VWAP for {self.ticker}")
            return TargetAllocation(allocation_dict)

        # Checking the cross over or cross under conditions for the latest data points
        # Assuming last value is the most recent
        if ema_values[-1] > vwap_values[-1] and ema_values[-2] < vwap_values[-2]:
            # EMA crosses over VWAP, signal a buy
            allocation_dict[self.ticker] = 1  # Allocate 100% to this asset
            log(f"Buying {self.ticker}, as 9-period EMA crossed over VWAP.")
        elif ema_values[-1] < vwap_values[-1] and ema_values[-2] > vwap_values[-2]:
            # EMA crosses under VWAP, signal a sell or avoid buying
            allocation_dict[self.ticker] = 0  # Allocate 0% to this asset, essentially selling it
            log(f"Selling {self.ticker}, as 9-period EMA crossed under VWAP.")
        else:
            log(f"No action for {self.ticker}, as there's no EMA and VWAP cross.")

        return TargetAllocation(allocation_dict)