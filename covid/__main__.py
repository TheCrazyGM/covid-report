import logging
import os

from datetime import datetime, timedelta
from io import StringIO

import requests
from beem.steem import Steem
from beem.wallet import Wallet
from pandas import read_csv
from sqlalchemy import create_engine

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p"
)

wif = os.environ["STEEM_WIF"]
stm = Steem(node="https://api.steemit.com", keys=wif, nobroadcast=False, )
w = Wallet(blockchain_instance=stm)
author = w.getAccountFromPrivateKey(wif)
logging.debug(author)
engine = create_engine("sqlite:///covid.db")
covid_cvs = requests.get(
    "https://opendata.ecdc.europa.eu/covid19/nationalcasedeath_eueea_daily_ei/csv/data.csv"
)
yesterday = datetime.now() + timedelta(days=-1)
covid_day = yesterday.strftime("%d/%m/%Y")
df = read_csv(StringIO(covid_cvs.text))
sql = df.to_sql("Covid", con=engine, if_exists="replace")
result = engine.execute(f'SELECT * FROM Covid where dateRep="{covid_day}"')
data = result.fetchall()


def main():
    title = f"European Centre for Disease Prevention and Control Report for Date {covid_day}"

    table = "| Date Reported | Cases | Deaths | Country / Territory | \n " + "| ------------- |------:| ------:| :------------------ |  \n "

    table += "".join(
        f'|{row["dateRep"]} | {row["cases"]}| {row["deaths"]}| {row["countriesAndTerritories"]} | \n'
        for row in data
    )
    beneficiaries = [
        {"account": author, "weight": 5000},
        {"account": "thecrazygm", "weight": 5000},
    ]

    body = f"""# ECDC Automated Report

This is a work in progress, the data is gathered daily from the European Union CDC

![ECDC](https://www.ecdc.europa.eu/profiles/custom/ecdc/themes/anthrax/images/logo-ecdc.png)
## Report for end of day Yesterday - {covid_day}

{table}

If you would like to contribute, please feel free to check out the [GitHub Repo here](https://github.com/TheCrazyGM/covid-report) or contact @thecrazygm.
"""

    tags = ["coronavirus", "covid", "covid-19", "quarantine"]
    tx = stm.post(
        title=title,
        body=body,
        author=author,
        tags=tags,
        beneficiaries=beneficiaries,
        permlink=None,
        self_vote=True,
    )
    logging.info(title)
    logging.debug(tx)


if __name__ == "__main__":
    main()
