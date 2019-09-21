from bpfeeder.utils import deep_extend
"""
[*] Bloomberg
    005380 KS Equity

[*] Yahoo
    005380.KS

[*] Cybos
    A005380

[*] Naver
    005380


"""

class SymbolAbstract:
    base = {
        'info': {
        'type': None,
        'symbol': None,
        'pure_symbol': None,
        'prefix': None,
        'suffix': None,
        },

        'symbol': None,
        'name': None,
        'nation': None,
        'exchange': None,
        'asset_type': None,
    }

    def _base(self, params={}):
        base = deep_extend(self.base, params)
        return base['info']['symbol']


class BloombergSymbol(SymbolAbstract):
    def __init__(self, symbol, params={}):
        self.base = deep_extend(self.base, params)
        pure_symbol, suffix, asset_type = symbol.split(' ')[:]

        base = {
            'info': {
            'type': 'bloomberg',
            'symbol': symbol,
            'pure_symbol': pure_symbol,
            'suffix': suffix,
            },

            'symbol': pure_symbol,
            'asset_type': asset_type
        }

        self.base = deep_extend(self.base, base)

    def use(self, feeder='bloomberg', params={}):
        __feeder__ = getattr(self, feeder)
        return __feeder__(params)

    def bloomberg(self, params={}):
        return self._base(params)

    def yahoo(self, params={}):
        base = deep_extend(self.base, params)
        return base['symbol'] if base['info']['suffix'] == 'US' \
            else '{}.{}'.format(base['symbol'], base['info']['suffix'])

    def naver(self, params={}):
        base = deep_extend(self.base, params)
        return base['symbol']

if __name__ == '__main__':
    print(BloombergSymbol(symbol='005380 KS Equity').use('bloomberg'))