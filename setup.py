from setuptools import setup

requires = [
    "beem",
    "sqlalchemy",
    "requests",
    "pandas",
]

setup(
    name="covid-report",
    version="0.1.0",
    description="Generate a Daily Coronavirus Report",
    url="https://lootkit.games/",
    author="Michael Garcia",
    author_email="thecrazygm@gmail.com",
    license="MIT",
    packages=[
        "covid",
    ],
    zip_safe=False,
    install_requires=requires,
    entry_points={
        "console_scripts": [
            "covid_report=covid.__main__:main",
        ],
    },
)
