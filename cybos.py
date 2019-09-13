import time
from datetime import datetime as dt
import psutil
import pandas as pd
import re
import pyautogui
import pywinauto
from win32com import client
import backtrader.feeds as btfeeds

stock_chart_fields_dct = {
            "DATE": 0, "TIME": 1, "OPEN": 2, "HIGH": 3, "LOW": 4, "CLOSE": 5, "DIFF": 6,
            "VOLUME": 8, "TRADING_VAL": 9, "누적체결매도수량": 10, "누적체결매수수량": 11,
            "상장주식수": 12, "시가총액": 13, "외국인주문한도수량": 14, "외국인주문가능수량": 15,
            "외국인현보유수량": 16, "외국인현보유비율": 17, "기관순매수": 20, "기관누적순매수": 21,
            "등락주선": 22, "등락비율": 23, "예탁금": 24, "주식회전율": 25, "거래성립률": 26, "대비부호": 37
        }


def convert_bsymbol(bsymbol):
    """
    Convert Bloomberg Symbol to Cybos Symbol
    :param bsymbol: Bloomberg Symbol ex) 005380 KS Equity
    :return: A005380
    """
    str = bsymbol.split()
    return 'A' + str[0]



class CybosAbsInputValueBase:
    def __init__(self, field_name=None, default=None):
        self.field_name = field_name
        self.value = default

    def value(self):
        return self.value

def convert_date_format(str, in_fmt='%Y%m%d', out_fmt='%Y-%m-%d'):
    _datetime = dt.strptime(str, format=in_fmt)
    return _datetime.strftime(out_fmt) if out_fmt != 'datetime' else _datetime

class CybosClient:

    __client__ = None

    def get_header(self, index):
        return self.__client__.GetHeaderValue(index)

    def get_data(self, row, column):
        return self.__client__.GetDataValue(row, column)

    def run(self):
        self.__client__.BlockRequest()

    def set_input_value(self, key, value):
        self.__client__.SetInputValue(key, value)


class StockChart(CybosClient):

    __client__ = client.Dispatch("CpSysDib.StockChart")


class StockTrader(CybosClient):

    __client__ = client.Dispatch("CpTrade.CpTd0311")


class StockUtil(CybosClient):

    __client__ = client.Dispatch("CpTrade.CpTdUtil")

    def __init__(self):
        self.__client__.TradeInit()


class StockConclusion(CybosClient):

    __client__ = client.Dispatch("dscbo1.CpConclusion")

    def subscribe(self, callback=None):
        if callback is not None and callable(callback):
            class Callback:
                def OnReceived(self):
                    callback()
            client.WithEvents(self.__client__, Callback)
        self.__client__.Subscribe()

    def unsubscribe(self):
        self.__client__.Unsubscribe()


class Cybos:

    __stock_chart__ = None
    __stock_trader__ = None
    __stock_utill__ = None
    __stock_conclusion__ = None
    __bank_account_number__ = ''



    @property
    def stock_chart(self):
        if self.__stock_chart__ is None:
            self.__stock_chart__ = StockChart()
        return self.__stock_chart__

    @property
    def stock_trader(self):
        if self.__stock_trader__ is None:
            self.__stock_trader__ = StockTrader()
        assert self.__stock_utill__ is not None
        return self.__stock_trader__

    @property
    def stock_util(self):
        if self.__stock_utill__ is None:
            self.__stock_utill__ = StockUtil()
        return self.__stock_utill__

    @property
    def stock_conclusion(self):
        if self.__stock_conclusion__ is None:
            self.__stock_conclusion__ = StockConclusion()
        return self.__stock_conclusion__

    @staticmethod
    def run_process(account_password, certification_password):
        app = pywinauto.Application()
        app.start('C:\DAISHIN\STARTER\\ncStarter.exe /prj:cp')
        time.sleep(1)
        pyautogui.typewrite('\n', interval=0.1)

        dialog = pywinauto.timings.WaitUntilPasses(20, 0.5, lambda: app.window(title='CYBOS Starter'))

        account_password_input = dialog.Edit2
        account_password_input.SetFocus()
        account_password_input.TypeKeys(account_password)

        certification_password_input = dialog.Edit3
        certification_password_input.SetFocus()
        certification_password_input.TypeKeys(certification_password)

        dialog.Button.Click()

        time.sleep(5)
        pyautogui.typewrite('\n', interval=0.5)
        time.sleep(10)

    def get_chart(self, code, params={}):

        headers = {
            'symbol': code,
            'start_date': dt(2015, 1, 1).strftime("%Y-%m-%d"),
            'end_date': dt.now().strftime("%Y-%m-%d"),
            'limit': (dt.now() - dt(2015, 1, 1)).days,
            'data_fields': [
                "DATE",
                "OPEN",
                "LOW",
                "CLOSE",
                "VOLUME"
            ],
            'frequency': '1D',
            'adjusted': True
        }

        headers = deep_extend(headers, params)
        req_type = ord('2') if headers['limit'] != None else ord('1')

        self.stock_chart.set_input_value(0, headers['symbol'])
        self.stock_chart.set_input_value(1, req_type)
        if headers['start_date'] != None:
            self.stock_chart.set_input_value(2, dt.strptime(headers['end_date'], "%Y-%m-%d").strftime("%Y%m%d"))
        if headers['end_date'] != None:
            self.stock_chart.set_input_value(3, dt.strptime(headers['start_date'], "%Y-%m-%d").strftime("%Y%m%d"))
        self.stock_chart.set_input_value(4, headers['limit'])
        self.stock_chart.set_input_value(5, [stock_chart_fields_dct[data_field] for data_field in headers['data_fields']])
        self.stock_chart.set_input_value(6, ord(re.sub('\d+', "", headers['frequency'])))
        self.stock_chart.set_input_value(7, ord(re.findall('\d+', headers['frequency'])[0]))
        self.stock_chart.set_input_value(9, ord(str(int(headers['adjusted']))))

        self.stock_chart.run()
        rows = range(self.stock_chart.get_header(3))
        columns = range(self.stock_chart.get_header(1))

        lst = []
        for row in rows:
            data = []
            for column in columns:
                data.append(self.stock_chart.get_data(column, row))
            lst.append(data)

        df = pd.DataFrame(lst, columns=headers['data_fields'])
        df.set_index(keys='DATE', drop=True, inplace=True)
        df.index = pd.to_datetime(df.index, format='%Y%m%d')
        df = df.sort_index()
        return df.loc[headers['start_date']:]

    def trade(self, trade_type: int, code: str, quantity: int, price: int, bank_account_number: str):
        self.stock_trader.set_input_value(0, trade_type)
        if bank_account_number == '':
            bank_account_number = self.__bank_account_number__
        self.stock_trader.set_input_value(1, bank_account_number)
        self.stock_trader.set_input_value(3, code)
        self.stock_trader.set_input_value(4, quantity)
        self.stock_trader.set_input_value(5, price)
        self.stock_trader.run()

    def sell(self, code, quantity, price, bank_account_number=''):
        self.trade(1, code, quantity, price, bank_account_number)

    def buy(self, code, quantity, price, bank_account_number=''):
        self.trade(2, code, quantity, price, bank_account_number)

    def __init__(self, bank_account_number=''):
        if 'CpStart.exe' not in [p.name() for p in psutil.process_iter()]:
            raise ConnectionError('Please check API connection.')
            # self.run_process(account_password, certification_password)

        if bank_account_number == '':
            self.__bank_account_number__ = self.stock_util.__client__.AccountNumber[0]
        else:
            self.__bank_account_number__ = bank_account_number


if __name__ == '__main__':
    cybos = Cybos().get_chart("A005380")
    print(cybos)