from dydx3 import Client
import pandas as pd
from pandas import DataFrame

# Scan dydx exchange by market and resolution
class Scaner:
    # Connect to public client dydx exchange
    def __init__(self, market: str, resolution: str):
        self.client = Client(host='https://api.dydx.exchange')
        self.market = market
        self.resolution = resolution
        print("Connected to exchange by market ", self.market, " resolution ", self.resolution)

    # Get candles data from client by market:
    # Close trade price
    # and
    # Volume of trade in baseToken currency
    def get_data(self) -> DataFrame:
        candles = self.client.public.get_candles(market=self.market,
                                                 resolution=self.resolution,
                                                 )
        df = pd.DataFrame(candles.data['candles'])
        df = df[['close', 'baseTokenVolume']]
        df = df.astype({'close': 'float64'})
        df = df.astype({'baseTokenVolume': 'float64'})
        return df

    # Get actual value of trade volume for market in last candle
    def get_trade_volume(self) -> float:
        candles = self.client.public.get_candles(market=self.market,
                                                 resolution=self.resolution,
                                                 )
        df = pd.DataFrame(candles.data['candles'])
        df = df.astype({'baseTokenVolume': 'float64'})
        return df.baseTokenVolume[0]

    # Variable Moving Average:
    # calc average sum at window size in USD
    def vma(self, window=1) -> float:
        data = self.get_data()
        return (data['baseTokenVolume'][:window] * data['close'][:window])[:window].sum()\
               / data['baseTokenVolume'][:window].sum()

    # Average volume of trade at window size in base token currency
    def average_spot(self, window=1) -> float:
        data = self.get_data()
        return data['baseTokenVolume'][:window].sum()/window
