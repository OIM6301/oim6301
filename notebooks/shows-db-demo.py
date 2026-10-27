# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo[sql]",
#     "duckdb",
#     "polars",
#     "pyarrow",
# ]
# ///
"""The TV show catalog, opened.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="medium", sql_output="polars")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import duckdb

    return (duckdb,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # The TV Show Catalog

    The database behind the two pages you designed on paper: `shows.db`, which CS50 built from IMDb's data. The first run downloads it from [CS50's lecture files](https://cdn.cs50.net/2024/fall/lectures/7/src7.zip) into the `data` folder. It is a SQLite file; DuckDB opens it through its `sqlite` extension, which it also downloads the first time.
    """)
    return


@app.cell
def _(mo):
    import io
    import urllib.request
    import zipfile

    shows_db = mo.notebook_dir().parent / "data" / "shows.db"
    if not shows_db.exists():
        shows_db.parent.mkdir(exist_ok=True)
        with urllib.request.urlopen("https://cdn.cs50.net/2024/fall/lectures/7/src7.zip", timeout=120) as _reply:
            _archive = zipfile.ZipFile(io.BytesIO(_reply.read()))
        shows_db.write_bytes(_archive.read("src7/imdb/shows.db"))
    shows_db.name
    return (shows_db,)


@app.cell
def _(duckdb, shows_db):
    con = duckdb.connect()
    con.execute("INSTALL sqlite")
    con.execute("LOAD sqlite")
    con.execute(f"ATTACH '{shows_db}' AS tv (TYPE sqlite, READ_ONLY)")
    con.sql("USE tv")
    return (con,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Rows in each table
    """)
    return


@app.cell
def _(con):
    con.sql("""
        SELECT 'shows' AS table_name, count(*) AS row_count FROM shows
        UNION ALL SELECT 'people', count(*) FROM people
        UNION ALL SELECT 'genres', count(*) FROM genres
        UNION ALL SELECT 'stars', count(*) FROM stars
        UNION ALL SELECT 'writers', count(*) FROM writers
        UNION ALL SELECT 'ratings', count(*) FROM ratings
    """).pl()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## How many shows are called *The Office*?
    """)
    return


@app.cell
def _(con):
    con.sql("""
        SELECT id, title, year, episodes
        FROM shows
        WHERE title = 'The Office'
        ORDER BY year
    """).pl()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Which genres are the most common?
    """)
    return


@app.cell
def _(con):
    con.sql("""
        SELECT genre, count(*) AS shows
        FROM genres
        GROUP BY genre
        ORDER BY shows DESC
        LIMIT 10
    """).pl()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One star stored twice on one show

    `stars` declares no primary key, so nothing stops a pair from being stored twice.
    """)
    return


@app.cell
def _(con):
    con.sql("""
        SELECT shows.title, shows.year, people.name, count(*) AS times
        FROM stars
        JOIN shows ON shows.id = stars.show_id
        JOIN people ON people.id = stars.person_id
        GROUP BY shows.title, shows.year, people.name
        HAVING count(*) > 1
        ORDER BY times DESC, shows.title
        LIMIT 10
    """).pl()
    return


if __name__ == "__main__":
    app.run()
