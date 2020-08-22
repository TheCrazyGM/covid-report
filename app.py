import os
import random
import string
from datetime import date, datetime, timedelta
from io import StringIO
from pprint import pprint

import requests
from beem import Steem
from beem.wallet import Wallet
from pandas import read_csv
from sqlalchemy import create_engine

wif = os.environ['STEEM_POSTING']

stm = Steem(node="https://api.steemit.com", keys=wif)
w = Wallet(steem_instance=stm)
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
title = f'European Centre for Disease Prevention and Control Report for Date {covid_day}'
table = "| Date Reported | Cases | Deaths | Country / Territory | \n "
table += "| ------------- |------:| ------:| :------------------ |  \n "
for row in data:
    table += f'|{row["dateRep"]} | {row["cases"]}| {row["deaths"]}| {row["countriesAndTerritories"]} | \n'

body = f"""
# ECDC Automated Report
This is a work in progress, the data is gathered daily from the European Union CDC (which I find to be more believable than our government at this moment) If you would like to contribute, please feel free to check out the [GitHub Repo here](https://github.com/TheCrazyGM/covid-report).
## Report for end of day Yesterday - {covid_day}
![](https://www.ecdc.europa.eu/profiles/custom/ecdc/themes/anthrax/images/logo-ecdc.png)
{table}
"""
tags = ['coronavirus', 'covid', 'covid-19', 'quarantine']
permlink = ''.join(random.choices(string.digits, k=10))
tx = stm.post(title=title, body=body, author=author,
              tags=tags, permlink=permlink)
pprint(tx)
