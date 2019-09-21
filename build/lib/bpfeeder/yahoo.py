import bpfeeder
from yahoofinancials import YahooFinancials
import pandas as pd
import numpy as np
from bpfeeder.utils import deep_extend, find_key_by_value, adjust

hist_fields_dct = {
    "DATE": "formatted_date",
    "ADJ_CLOSE": "adjclose",
    "CLOSE": "close",
    "OPEN": "open",
    "HIGH": "high",
    "LOW": "low",
    "VOLUME": "volume",
    "DIVIDENDS": "dividends"
}

time_interval_dct = {
    "1D": "daily",
    "1W": "weekly",
    "1M": "monethly"
}

adj_params = {
    'round': True,
    'decimals': 2,
    'OPEN': 'OPEN',
    'HIGH': 'HIGH',
    'LOW': 'LOW',
    'CLOSE': 'CLOSE',
    'ADJ_CLOSE': 'ADJ_CLOSE',
    'VOLUME': 'VOLUME'
}

class yahoo(bpfeeder.Feeder):

    def get_ohlcv(self, symbol, params={}):
        custom_params = deep_extend(self.ohlcv_headers, params)
        custom_params['data_fields'].append('ADJ_CLOSE') if custom_params['adjusted'] == True and 'ADJ_CLOSE' not in \
        custom_params['data_fields'] else True

        headers = {
            'symbol': symbol,
            'data_fields': custom_params['data_fields'],
            'req_data_fields': [hist_fields_dct[field] for field in custom_params['data_fields']],
            'frequency': time_interval_dct[custom_params['frequency']],
        }

        params = deep_extend(custom_params, headers)
        return self._get_ohlcv(params)

    def _adjust_ohlcv(self, df, rounding=4):
        """
        Yahoo Returns adj-price only close.
        We adjust other prices using adj-close and raw close.

        :param df: Having cols [OPEN, HIGH, LOW, CLOSE, ADJ_CLOSE, VOLUME]
        :return: adj_df: Having cols [OPEN, HIGH, LOW, CLOSE, VOLUME]
        """
        
        # Adjust the rest of the data
        df[adj_params['OPEN']] = np.vectorize(adjust)(df.index, df[adj_params['CLOSE']], df[adj_params['ADJ_CLOSE']],
                                                df[adj_params['OPEN']], rounding=rounding)
        df[adj_params['HIGH']] = np.vectorize(adjust)(df.index, df[adj_params['CLOSE']], df[adj_params['ADJ_CLOSE']],
                                                df[adj_params['HIGH']], rounding=rounding)
        df[adj_params['LOW']] = np.vectorize(adjust)(df.index, df[adj_params['CLOSE']], df[adj_params['ADJ_CLOSE']],
                                                df[adj_params['LOW']], rounding=rounding)
        df[adj_params['CLOSE']] = df[adj_params['ADJ_CLOSE']]

        # Extract the colums we want to work with and rename them.
        df = df[[adj_params['OPEN'], adj_params['HIGH'], adj_params['LOW'], adj_params['CLOSE'], adj_params['VOLUME']]]
        return df

    def _get_ohlcv(self, params):
        yf = YahooFinancials([params['symbol']])
        hist_price = yf.get_historical_price_data(
            start_date=params['start_date'],
            end_date=params['end_date'],
            time_interval=params['frequency'],)[params['symbol']]['prices']

        df = pd.DataFrame.from_dict(hist_price)
        df = df[params['req_data_fields']]
        df.columns = params['data_fields']
        df.set_index('DATE', drop=True, inplace=True)
        df.index = pd.to_datetime(df.index)

        for column in df.columns:
            try:
                df[column] = pd.to_numeric(df[column])
            except:
                print(column)

        return self._adjust_ohlcv(df) if params['adjusted'] == True else df

    def get_events(self, symbol, params={}):
        custom_params = deep_extend(self.events_headers, params)
        headers = {
            'symbol': symbol,
            'data_fields': custom_params['data_fields'],
            'req_data_fields': [hist_fields_dct[field] for field in self.events_headers['data_fields']],
            'frequency': 'daily'
        }

        params =  deep_extend(custom_params, headers)
        return self._get_events(params)

    def _get_events(self, params):
        yf = YahooFinancials([params['symbol']])
        hist_events = yf.get_historical_price_data(
            start_date=params['start_date'],
            end_date=params['end_date'],
            time_interval=params['frequency'])[params['symbol']]['eventsData']

        hist_events = hist_events

        res = {}

        for req_data_field in [x for x in params['req_data_fields'] if x!='formatted_date']:
            hist = pd.DataFrame.from_dict(hist_events[req_data_field]).T
            hist = hist[['amount']]
            data_field = find_key_by_value(hist_fields_dct, req_data_field)
            hist.columns = [data_field]
            hist.index = pd.to_datetime(hist.index)
            hist.index.name = 'DATE'
            hist = hist.sort_index()
            hist[data_field] = pd.to_numeric(hist[data_field])
            res[data_field] = hist

        return res

def main():
   print(Yahoo().get_ohlcv(symbol="005380.KS"))
   print(Yahoo().get_events(symbol="005380.KS"))

if __name__ == '__main__':
    main()