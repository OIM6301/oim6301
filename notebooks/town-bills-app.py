# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo[sql]",
#     "duckdb",
#     "polars",
#     "pyarrow",
#     "altair",
#     "requests",
# ]
# ///
"""Town bills.
"""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import altair as alt
    import duckdb
    import requests

    return alt, duckdb, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Town Bills

    Pick a county to compare its towns: what a single-family home pays in property tax each year, and the income per person.
    """)
    return


@app.cell
def _(mo, requests):
    # The database. In your own app, point this at your project's database.
    _folder = mo.notebook_dir().parent / "data"
    _folder.mkdir(exist_ok=True)
    towns_database = _folder / "combining-towns.duckdb"
    if not towns_database.exists():
        _reply = requests.get(
            f"https://oim7510.github.io/data/combining/{towns_database.name}", timeout=60
        )
        _reply.raise_for_status()
        towns_database.write_bytes(_reply.content)
    return (towns_database,)


@app.cell
def _(duckdb, towns_database):
    # Every query goes through this function. A value that comes from the user
    # goes into params, one for each ?, and never into the SQL text.
    def ask(sql, params=None):
        with duckdb.connect(towns_database, read_only=True) as _con:
            return _con.sql(sql, params=params).pl()

    return (ask,)


@app.cell
def _(ask, mo):
    # 1. The input: a dropdown whose options come from the database.
    county_names = ask("SELECT name FROM counties ORDER BY name")["name"].to_list()
    county_picker = mo.ui.dropdown(options=county_names, value="Norfolk", label="County")
    county_picker
    return (county_picker,)


@app.cell
def _(ask, county_picker):
    # 2. The query, with ? where the user's choice goes.
    town_bills = ask(
        """
        SELECT name AS town,
               average_single_family_bill_dollars AS tax_bill,
               income_per_capita_dollars AS income_per_person
        FROM towns
        WHERE county = ?
        ORDER BY tax_bill DESC
        """,
        [county_picker.value],
    )
    return (town_bills,)


@app.cell
def _(alt, mo, town_bills):
    # 3. The table and the chart, side by side, with where the numbers come from.
    _chart = town_bills.plot.bar(
        x=alt.X("tax_bill", title="Average single-family tax bill (dollars)"),
        y=alt.Y("town", sort="-x", title=None),
    ).properties(height=max(200, 18 * town_bills.height))
    mo.vstack([
        mo.hstack([mo.ui.table(town_bills, selection=None), mo.ui.altair_chart(_chart)], widths=[1, 1]),
        mo.md(
            "Source: Massachusetts Department of Revenue, Division of Local Services, Municipal Databank. "
            "The tax bill is the average for a single-family home in the latest fiscal year each town reported; "
            "income is per person, for everyone who lives in the town."
        ),
    ])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
