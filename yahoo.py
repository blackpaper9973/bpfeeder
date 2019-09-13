import bpfeeder
from yahoofinancials import YahooFinancials
import pandas as pd
from bpfeeder.utils import deep_extend, find_key_by_value

hist_fields_dct = {
    "DATE": "formatted_date",
    "CLOSE": "adjclose",
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

class yahoo(bpfeeder.Feeder):

    def get_ohlcv(self, symbol, params={}):
        custom_params = deep_extend(self.ohlcv_headers, params)
        headers = {
            'symbol': symbol,
            'data_fields': custom_params['data_fields'],
            'req_data_fields': [hist_fields_dct[field] for field in custom_params['data_fields']],
            'frequency': time_interval_dct[custom_params['frequency']],
        }

        params = deep_extend(custom_params, headers)
        return self._get_ohlcv(params)

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
            df[column] = pd.to_numeric(df[column])
        return df

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