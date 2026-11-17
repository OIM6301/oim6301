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
app = marimo.App(layout_file="layouts/shows-db-demo.slides.json", width="medium", sql_output="polars")


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

    The database behind the two pages you designed on paper: `shows.db`, built from IMDb's data. The first run downloads it into the `data` folder. It is a SQLite file; DuckDB opens it through its `sqlite` extension, which it also downloads the first time.
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
    ## Which year had the most new shows?
    """)
    return


@app.cell
def _(con):
    con.sql("""
        SELECT year, count(*) AS shows
        FROM shows
        GROUP BY year
        ORDER BY shows DESC
        LIMIT 5
    """).pl()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## One star stored twice on one show

    `stars` has no primary key, so nothing stops a pair from being stored twice.
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


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## An index

    We find the stars of The Office twice: first by reading every row of `stars`, then through an index on `stars.show_id`. SQLite runs both, on a copy of `shows.db`, so the index never reaches the file in `data`.
    """)
    return


@app.cell
def _(shows_db):
    import shutil
    import tempfile
    from pathlib import Path

    demo_db = Path(tempfile.mkdtemp()) / "shows-copy.db"
    shutil.copy(shows_db, demo_db)
    demo_db.name
    return (demo_db,)


@app.cell
def _(demo_db, mo):
    import sqlite3

    sqlite_con = sqlite3.connect(demo_db)
    office_id = sqlite_con.execute(
        "SELECT id FROM shows WHERE title = 'The Office' AND year = 2005"
    ).fetchone()[0]
    star_rows = sqlite_con.execute("SELECT count(*) FROM stars").fetchone()[0]
    mo.md(f"`stars` has **{star_rows:,}** rows. The Office (2005) is show {office_id}.")
    return sqlite_con, office_id


@app.cell
def _():
    import statistics
    import time

    def time_query(sqlite_con, sql, params):
        # The middle of 20 runs, in milliseconds.
        runs = []
        for _ in range(20):
            start = time.perf_counter()
            sqlite_con.execute(sql, params).fetchall()
            runs.append((time.perf_counter() - start) * 1000)
        return statistics.median(runs)

    find_stars = "SELECT person_id FROM stars WHERE show_id = ?"
    return find_stars, time_query


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Without an index

    SQLite reads every row of `stars` and keeps the ones for The Office. `EXPLAIN QUERY PLAN` says how it will find the rows.
    """)
    return


@app.cell
def _(sqlite_con, find_stars, mo, office_id, time_query):
    plan_before = sqlite_con.execute("EXPLAIN QUERY PLAN " + find_stars, [office_id]).fetchall()[0][-1]
    stars_found = len(sqlite_con.execute(find_stars, [office_id]).fetchall())
    before_ms = time_query(sqlite_con, find_stars, [office_id])
    mo.md(f"Plan: `{plan_before}`. Found {stars_found} stars in **{before_ms:.2f} ms**.")
    return (before_ms,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### With an index

    The index lists the values of `show_id` in order, each pointing to its rows. Building it takes a moment, and the file grows.
    """)
    return


@app.cell
def _(before_ms, sqlite_con, demo_db, find_stars, mo, office_id, time_query):
    size_before = demo_db.stat().st_size
    sqlite_con.execute("CREATE INDEX stars_by_show ON stars (show_id)")
    sqlite_con.commit()
    size_after = demo_db.stat().st_size
    plan_after = sqlite_con.execute("EXPLAIN QUERY PLAN " + find_stars, [office_id]).fetchall()[0][-1]
    after_ms = time_query(sqlite_con, find_stars, [office_id])
    mo.md(
        f"Plan: `{plan_after}`. The same query in **{after_ms:.3f} ms**, "
        f"about {before_ms / after_ms:,.0f} times faster. "
        f"The file grew from {size_before / 1e6:.1f} MB to {size_after / 1e6:.1f} MB."
    )
    return


if __name__ == "__main__":
    app.run()
