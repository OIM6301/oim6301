# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo[sql]",
#     "duckdb",
#     "polars",
#     "pyarrow",
#     "requests",
# ]
# ///
"""Changing data safely.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(layout_file="layouts/08-changing-data-safely.slides.json", width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import duckdb
    import requests

    return duckdb, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Changing Data Safely

    In this notebook we change the data in a database and look at what keeps a change from going wrong. We start with a delete the database refuses, then make a change that takes several statements, and end with a value typed by a user, which has to go into a query. We use the towns and counties again, with their keys declared.

    | | |
    |---|---|
    | ✏️ | Your turn. Add cells with the **+** button |

    For a written answer, add a cell under the question, open the cell's **⋯** menu and choose **Convert to Markdown**.

    The ✏️ exercises are for practice. They are not part of a checkpoint. The **Going further** at the end of an exercise is optional; try it once the rest is done.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Work with your agent the same way as in notebook 7.** Try it yourself first, or write the steps in words. Then ask your agent, ask it to explain any line you could not have written, and ask which concepts its answer used. Do exercise A by hand.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **The data.** This notebook uses `combining-towns.duckdb`, the towns database notebook 7 downloaded into your `data` folder. The next cell downloads it if it is not there.
    """)
    return


@app.cell
def _(mo, requests):
    _folder = mo.notebook_dir().parent / "data"
    _folder.mkdir(exist_ok=True)
    towns_database = _folder / "combining-towns.duckdb"
    if not towns_database.exists():
        _reply = requests.get(
            f"https://oim7510.github.io/data/combining/{towns_database.name}", timeout=60
        )
        _reply.raise_for_status()
        towns_database.write_bytes(_reply.content)
    towns_database.name
    return (towns_database,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **A fresh copy for every cell.** Each cell in this notebook changes the data, so each one starts from a copy of its own. `build_database()` makes a new database in memory, creates the two tables with their keys, as notebook 6 did, and loads the rows from the file into them. The file in your `data` folder does not change.
    """)
    return


@app.cell
def _(duckdb, towns_database):
    def build_database():
        with duckdb.connect(towns_database, read_only=True) as source:
            county_rows = source.sql("SELECT name, towns, population FROM counties").pl()
            town_rows = source.sql("SELECT * FROM towns").pl()
        database = duckdb.connect()
        database.execute("""
            CREATE TABLE counties (
                name       VARCHAR PRIMARY KEY,
                towns      INTEGER NOT NULL CHECK (towns >= 0),
                population INTEGER NOT NULL CHECK (population > 0)
            )
        """)
        database.execute("""
            CREATE TABLE towns (
                name                               VARCHAR PRIMARY KEY,
                county                             VARCHAR NOT NULL REFERENCES counties(name),
                population                         INTEGER NOT NULL CHECK (population > 0),
                income_per_capita_dollars          INTEGER,
                average_single_family_bill_dollars INTEGER CHECK (average_single_family_bill_dollars >= 0)
            )
        """)
        database.execute("INSERT INTO counties SELECT * FROM county_rows")
        database.execute("INSERT INTO towns SELECT * FROM town_rows")
        return database

    return (build_database,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The following cell builds one copy and counts the rows of both tables.
    """)
    return


@app.cell
def _(build_database):
    build_database().sql("""
        SELECT (SELECT count(*) FROM towns) AS towns,
               (SELECT count(*) FROM counties) AS counties
    """).pl()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There are 351 towns in 14 counties.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 1. Deleting a Row Others Point At

    `towns.county` is a foreign key to `counties.name`, so every county that has towns is a row other rows point at. The following cell tries to delete Suffolk County, which has four towns. As in notebook 6, `try` and `except` catch the refusal, and the cell shows the message.
    """)
    return


@app.cell
def _(build_database, duckdb):
    _database = build_database()
    try:
        _database.execute("DELETE FROM counties WHERE name = 'Suffolk'")
        _message = "deleted"
    except duckdb.ConstraintException as _error:
        _message = str(_error).splitlines()[0]
    _message
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    DuckDB refuses the delete. Suffolk stays, and its four towns keep their county; none of them gets `NULL`. The message says the key is still referenced.

    In SQL Server and PostgreSQL, a foreign key can be declared with `ON DELETE CASCADE`, and then deleting a county deletes its towns too. DuckDB refuses that declaration, so here the delete is always refused. To delete a county, we delete its towns first. The following cell does that and counts the rows again.
    """)
    return


@app.cell
def _(build_database):
    _database = build_database()
    _database.execute("DELETE FROM towns WHERE county = 'Suffolk'")
    _database.execute("DELETE FROM counties WHERE name = 'Suffolk'")
    _database.sql("""
        SELECT (SELECT count(*) FROM towns) AS towns,
               (SELECT count(*) FROM counties) AS counties
    """).pl()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Now there are 347 towns and 13 counties. Once the four towns are gone, no row points at Suffolk, and the delete runs.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ A · A County and Its Towns

    **No agent for this one**, and no code completion either. When the editor suggests code in grey as you type, press `Esc` and keep typing your own.

    1. In a cell of your own, start from `build_database()` and try to delete Norfolk County. Show the message. *Check yourself: the message contains `still referenced`.*
    2. Delete Norfolk the way that works, then count the rows of both tables. *Check yourself: 323 towns and 13 counties.*
    3. In another cell, start from a fresh copy and try to move Wellesley into a county that does not exist, with `UPDATE towns SET county = 'Atlantis' WHERE name = 'Wellesley'`. *Check yourself: the message contains `does not exist`.*
    4. In a markdown cell under it, explain what would happen to Wellesley in step 3 if `towns` had no foreign key.

    **Going further.** Pick a table in your database project that other tables point at. Which delete from it would a manager of that business ask for, and what should happen to the rows that point at it?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 2. Changes That Belong Together

    `counties` keeps a count of its towns in the `towns` column. That count is a fact stored twice, once as a number and once as the rows of `towns`, so a change to one has to change the other. Moving Brookline from Norfolk County to Suffolk County takes three statements: change Brookline's county, take one from Norfolk's count, and add one to Suffolk's.

    The following function lists every county whose stored count differs from the number of its towns in `towns`. When the data agrees with itself, the result is empty.
    """)
    return


@app.cell
def _():
    def find_wrong_counts(database):
        return database.sql("""
            SELECT c.name, c.towns AS stored_count, count(t.name) AS counted_towns
            FROM counties AS c
            LEFT JOIN towns AS t ON t.county = c.name
            GROUP BY c.name, c.towns
            HAVING c.towns <> count(t.name)
        """).pl()

    return (find_wrong_counts,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The next cell runs the three statements one after another. The third has a typo, `town` for `towns`, so it fails. The cell shows the error and then the counts that disagree.
    """)
    return


@app.cell
def _(build_database, duckdb, find_wrong_counts, mo):
    _database = build_database()
    try:
        _database.execute("UPDATE towns SET county = 'Suffolk' WHERE name = 'Brookline'")
        _database.execute("UPDATE counties SET towns = towns - 1 WHERE name = 'Norfolk'")
        _database.execute("UPDATE counties SET town = towns + 1 WHERE name = 'Suffolk'")
        _message = "no error"
    except duckdb.Error as _error:
        _message = str(_error).splitlines()[0]
    mo.vstack([_message, find_wrong_counts(_database)])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The first two statements were kept and the third was not. Brookline is now in Suffolk and Norfolk's count went down, but Suffolk's count is still 4 while it has five towns. Each row on its own is valid, so no constraint refuses anything, and the database now holds half a change.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **A transaction** groups statements so that either all of them are kept or none is. This property is called **atomicity**. In Python, `begin()` starts the transaction, `commit()` keeps its changes, and `rollback()` undoes every change since `begin()`. With `try` and `except` around them, an error in any statement leads to `rollback()`. The next cell runs the same three statements, typo included, as one transaction.
    """)
    return


@app.cell
def _(build_database, duckdb, find_wrong_counts, mo):
    _database = build_database()
    try:
        _database.begin()
        _database.execute("UPDATE towns SET county = 'Suffolk' WHERE name = 'Brookline'")
        _database.execute("UPDATE counties SET towns = towns - 1 WHERE name = 'Norfolk'")
        _database.execute("UPDATE counties SET town = towns + 1 WHERE name = 'Suffolk'")
        _database.commit()
        _message = "committed"
    except duckdb.Error as _error:
        _database.rollback()
        _message = "rolled back: " + str(_error).splitlines()[0]
    mo.vstack([
        _message,
        find_wrong_counts(_database),
        _database.sql("SELECT name, county FROM towns WHERE name = 'Brookline'").pl(),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    This time nothing changed. No count is wrong, and Brookline is still in Norfolk.

    The next cell runs the same transaction with the typo fixed.
    """)
    return


@app.cell
def _(build_database, duckdb, find_wrong_counts, mo):
    _database = build_database()
    try:
        _database.begin()
        _database.execute("UPDATE towns SET county = 'Suffolk' WHERE name = 'Brookline'")
        _database.execute("UPDATE counties SET towns = towns - 1 WHERE name = 'Norfolk'")
        _database.execute("UPDATE counties SET towns = towns + 1 WHERE name = 'Suffolk'")
        _database.commit()
        _message = "committed"
    except duckdb.Error as _error:
        _database.rollback()
        _message = "rolled back: " + str(_error).splitlines()[0]
    mo.vstack([
        _message,
        find_wrong_counts(_database),
        _database.sql("SELECT name, county FROM towns WHERE name = 'Brookline'").pl(),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The message is `committed`, and Brookline is in Suffolk. The list of wrong counts is still empty, because the transaction kept every change.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ B · Moving Cambridge

    1. In a cell of your own, start from a fresh copy and move Cambridge from Middlesex County to Suffolk County in one transaction. Then show `find_wrong_counts()` and the two counties' counts. *Check yourself: no wrong counts; Middlesex has 53 towns and Suffolk 5.*
    2. In another cell, run the same transaction with a fourth statement that sets Cambridge's population to 0, which the `CHECK` on `population` refuses. Show that none of the four changes was kept. *Check yourself: Cambridge is in Middlesex, Middlesex has 54 towns and Suffolk 4.*
    3. In a markdown cell under it, name a change in your database project's business that takes more than one statement, and the statements it takes.

    **Going further.** Write a function `move_town(database, town_name, county_name)` that moves any town in one transaction, and test it on a county that does not exist.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # 3. A Value Typed by a User

    A product takes input from the person using it, such as a name typed into a search box or a county picked from a list, and that value goes into a query. The following function finds a town by the name a user typed. It puts the name into the query with an f-string.
    """)
    return


@app.cell
def _():
    def find_town_with_fstring(database, town_name):
        return database.sql(
            f"SELECT name, county, population FROM towns WHERE name = '{town_name}'"
        ).pl()

    return (find_town_with_fstring,)


@app.cell
def _(build_database, find_town_with_fstring):
    find_town_with_fstring(build_database(), "Wellesley")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    With `Wellesley`, it finds one town. Now suppose the user types `x' OR '1'='1` into the box:
    """)
    return


@app.cell
def _(build_database, find_town_with_fstring):
    find_town_with_fstring(build_database(), "x' OR '1'='1")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    It returns all 351 towns. The quote after `x` closes the string in the query early, so the query became `WHERE name = 'x' OR '1'='1'`, and `'1'='1'` is true for every row. Typing SQL into an input so that it changes the query is called **SQL injection**. Here it reads more rows than it should. On a login form it can skip the password check, and with `x'; DROP TABLE towns; --` it deletes the table.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Write `?` where the value goes.** The value travels beside the query as a **parameter**, and the database never reads it as SQL. In DuckDB, `.sql()` takes the values in `params`, one for each `?`, in order.
    """)
    return


@app.cell
def _():
    def find_town(database, town_name):
        return database.sql(
            "SELECT name, county, population FROM towns WHERE name = ?",
            params=[town_name],
        ).pl()

    return (find_town,)


@app.cell
def _(build_database, find_town):
    find_town(build_database(), "x' OR '1'='1")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The result is empty, because no town is named `x' OR '1'='1`. With `Wellesley`, the same function finds Wellesley.

    Any value that comes from outside your code goes into a query as a parameter. The mark depends on the library: `?` in DuckDB and SQLite, `%s` in pymssql.

    Full reference: [SQL handbook, §27, Running SQL from a notebook](/handbooks/sql/04-building-and-loading/#27-running-sql-from-a-notebook)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ✏️ C · Towns in a County

    1. Write a function `find_towns_in(database, county_name)` that returns the towns of one county with their average single-family tax bill, the highest bill first, with `?` for the county. *Check yourself: Norfolk has 28 towns, and Brookline is first, 26,237.*
    2. Call it with `Norfolk' OR '1'='1`. *Check yourself: no rows.*
    3. Ask your agent for the same function, without mentioning `?`. In a markdown cell under its answer, explain whether its query is safe from SQL injection and how you can tell from the code.

    **Going further.** Put a dropdown of the counties above your function with `mo.ui.dropdown`, so that a user picks a county and sees its towns.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Self-check:**

    - [ ] I can explain why a database refuses to delete a row that other rows point at, and delete it in an order that works
    - [ ] I can put statements that belong together in one transaction, and say what happens when one of them fails
    - [ ] I can put a value a user typed into a query with `?`, and explain what an f-string would let that user do
    """)
    return


if __name__ == "__main__":
    app.run()
