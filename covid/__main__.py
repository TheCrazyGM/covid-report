import os
import random
import string
from datetime import date, datetime, timedelta
from io import StringIO
from pprint import pprint

import requests
from beem.hive import Hive
from beem.wallet import Wallet
from pandas import read_csv
from sqlalchemy import create_engine

wif = os.environ['STEEM_POSTING']

hv = Hive(node="https://anyx.io", keys=wif, nobroadcast=False)
w = Wallet(blockchain_instance=hv)
author = w.getAccountFromPrivateKey(wif)
engine = create_engine('sqlite:///covid.db')
covid_cvs = requests.get(
    'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv')
yesterday = datetime.now() + timedelta(days=-1)
covid_day = yesterday.strftime("%d/%m/%Y")
df = read_csv(StringIO(covid_cvs.text))
sql = df.to_sql("Covid", con=engine, if_exists="replace")
result = engine.execute(f'SELECT * FROM Covid where dateRep="{covid_day}"')
data = result.fetchall()


def main():
    title = f'European Centre for Disease Prevention and Control Report for Date {covid_day}'
    table = "| Date Reported | Cases | Deaths | Country / Territory | \n "
    table += "| ------------- |------:| ------:| :------------------ |  \n "
    table += ''.join(f'|{row["dateRep"]} | {row["cases"]}| {row["deaths"]}| {row["countriesAndTerritories"]} | \n' for row in data)

    body = f"""
    #ECDC Automated Report
    This is a work in progress, the data is gathered daily from the European Union CDC 
    If you would like to contribute, please feel free to check out the [GitHub Repo here](https://github.com/TheCrazyGM/covid-report).
    ##Report for end of day Yesterday - {covid_day}
    ![](https://www.ecdc.europa.eu/profiles/custom/ecdc/themes/anthrax/images/logo-ecdc.png)
    {table}
    """
    tags = ['coronavirus', 'covid', 'covid-19', 'quarantine']
    tx = hv.post(title=title, body=body, author=author,
                 tags=tags, permlink=None)
    pprint(tx)


if __name__ == "__main__":
    main()
