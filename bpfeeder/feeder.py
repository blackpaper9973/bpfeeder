from datetime import datetime as dt

class Feeder:
    ohlcv_headers = {
        'symbol': None,
        'start_date': dt(2015, 1, 1).strftime("%Y-%m-%d"),
        'end_date': dt.now().strftime("%Y-%m-%d"),
        'limit': (dt.now() - dt(2015, 1, 1)).days,
        'data_fields': ["DATE", "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME"],
        'frequency': '1D',
        'adjusted': True
    }

    events_headers = {
        'symbol': None,
        'start_date': dt(2015, 1, 1).strftime("%Y-%m-%d"),
        'end_date': dt.now().strftime("%Y-%m-%d"),
        'data_fields': ["DATE", "DIVIDENDS"]
    }
    urls = {
        'chart': None,
        'events': None
    }
    @staticmethod
    def find_key_by_value(dic, val):
        for key, value in dic.items():
            if val == value:
                return key
        return "key doesn't exist"

    @staticmethod
    def deep_extend(*args):
        result = None
        for arg in args:
            if isinstance(arg, dict):
                if not isinstance(result, dict):
                    result = {}
                for key in arg:
                    result[key] = Feeder.deep_extend(result[key] if key in result else None, arg[key])
            else:
                result = arg
        return result

    def _get_ohlcv(self, params):
        print(params)
        pass

    def get_ohlcv(self, code, params={}):
        return self._get_ohlcv(params)

