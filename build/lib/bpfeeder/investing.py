import investpy

class InvestingEquitySymbol:
    country = None
    name = None
    full_name = None
    tag = None
    isin = None
    id = None
    currency = None

class Investing:
    def get_equities_list(self):
        """
        Retrieve all the available equities as a Python list
        :return: A List of All the available equities
        """
        return investpy.get_equities_list()

# Retrieve the recent historical data (past month) of an equity as a pandas.DataFrame on ascending date order
df = investpy.get_recent_data(equity='Hyundai Motor', country='south-korea', as_json=False, order='ascending', debug=False)

# Retrieve the company profile of the introduced equity on english
#profile = investpy.get_equity_company_profile(equity='bbva', country='spain', language='english')

#print(equities.to_excel(r'C:\Users\jinho\PycharmProjects\test.xlsx'))

print(df)

#print(profile)