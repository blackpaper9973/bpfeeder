import bpfeeder
import requests
from bs4 import BeautifulSoup
import pandas as pd
from bpfeeder.utils import deep_extend
import copy

hist_fields_dct = {
    "DATE": "날짜",
    "CLOSE": "종가",
    "OPEN": "시가",
    "HIGH": "고가",
    "LOW": "저가",
    "VOLUME": "거래량",
    "DIFF": "전일비",
    "DIVIDEND_YIELD": "배당수익률",
    "SHARESOUT": "상장주식수",
    "PER": "PER",
    "EPS": "EPS"
}

time_interval_dct = {
    "1D": "D"
}

chart_time_interval_dct = {
    "1D": "day"
}



class naver(bpfeeder.Feeder):
    urls = {
        'ohlcv': 'http://finance.naver.com/item/sise_day.nhn?code=',
        'item': 'https://finance.naver.com/item/main.nhn?code=',
        'chart': "https://fchart.stock.naver.com/sise.nhn?symbol={}&timeframe={}&count={}&requestType=0"
    }

    def get_ohlcv(self, symbol, params={}):
        custom_params = copy.deepcopy(self.ohlcv_headers)
        custom_params.update(params)
        headers = {
            'url': self.urls['chart'],
            'symbol': symbol,
            'data_fields': custom_params['data_fields'],
            'frequency': chart_time_interval_dct[custom_params['frequency']],
            'limit': (custom_params['end_date'] - custom_params['start_date']).days,
            'adjusted': False
        }
        custom_params.update(headers)
        return self._get_ohlcv(custom_params)

    def _get_ohlcv(self, params):
        url = params['url'].format(str(params['symbol']), params['frequency'], params['limit'])
        res = requests.get(url)

        soap = BeautifulSoup(res.text, "html.parser")
        items = soap.find_all("item")

        matrix = []

        for item in items:
            row = item['data'].split('|')
            matrix.append(row)

        df = pd.DataFrame(data=matrix, columns=['DATE', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME'])
        df = df[params['data_fields']]
        df.set_index(keys='DATE', drop=True, inplace=True)
        df.index = pd.to_datetime(df.index, format="%Y%m%d")
        df = df.sort_index(ascending=True)

        cond1 = df.index >= params['start_date'].strftime("%Y-%m-%d")
        cond2 = df.index <= params['end_date'].strftime("%Y-%m-%d")

        for column in df.columns:
            df[column] = pd.to_numeric(df[column])
            
        return df.loc[cond1 & cond2, ]

    def get_ohlcv_curl(self, symbol, params={}):
        custom_params = deep_extend(self.ohlcv_headers, params)

        headers = {
            'url': self.urls['ohlcv'],
            'symbol': symbol,
            'data_fields': custom_params['data_fields'],
            'req_data_fields': [hist_fields_dct[field] for field in custom_params['data_fields']],
            'frequency': time_interval_dct[custom_params['frequency']],
        }

        params = deep_extend(custom_params, headers)
        return self._get_ohlcv(params)

    def _get_ohlcv_curl(self, params):
        url = params['url'] + str(params['symbol'])
        res = requests.get(url)

        soap = BeautifulSoup(res.text, "html.parser")
        pg_navi = soap.find_all("table", align="center")
        max_pg_sec = pg_navi[0].find_all("td", class_="pgRR")
        max_pg_num = int(max_pg_sec[0].a.get('href').split('page=')[-1])

        df = None
        for page in range(1, max_pg_num + 1):
            _hist_price = self._parse_page(url, page)
            _hist_price_filtered = _hist_price[_hist_price['날짜'] > params['start_date'].strftime("%Y-%m-%d")]
            if df is None:
                df = _hist_price_filtered
            else:
                df = pd.concat([df, _hist_price_filtered])
            if len(_hist_price) > len(_hist_price_filtered):
                break

        df = df[params['req_data_fields']]
        df.columns = params['data_fields']
        df.set_index(keys='DATE', drop=True, inplace=True)
        df = df.sort_index(ascending=True)

        cond1 = df.index >= params['start_date'].strftime("%Y-%m-%d")
        cond2 = df.index <= params['end_date'].strftime("%Y-%m-%d")

        return df.loc[cond1 & cond2, ]

    @staticmethod
    def _parse_page(url, page):
        try:
            url = url + '&page={}'.format(page)
            res = requests.get(url)
            _soap = BeautifulSoup(res.text, 'lxml')
            _df = pd.read_html(str(_soap.find("table")), header=0)[0]
            _df = _df.dropna()
            _df["날짜"] = pd.to_datetime(_df["날짜"], format='%Y.%m.%d')
            return _df
        except Exception as e:
            print(e)
        return None

if __name__ == '__main__':
    print(naver().get_ohlcv(symbol="005380"))