# /// script
# requires-python = ">=3.12,<3.15"
# dependencies = [
#     "marimo",
# ]
# ///
"""An index, timed.
"""

import marimo

__generated_with = "0.25.1"
app = marimo.App(layout_file="layouts/index-demo.slides.json", width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    import shutil
    import sqlite3
    import statistics
    import tempfile
    import time
    from pathlib import Path

    return Path, shutil, sqlite3, statistics, tempfile, time


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # An Index

    We find the stars of The Office twice in `shows.db`: first by reading every row of `stars`, then through an index on `stars.show_id`.
    """)
    return


@app.cell
def _(Path, mo, shutil, tempfile):
    # shows.db from CS50, downloaded into the data folder the first time.
    # The demo works on a copy, so the index never reaches data/shows.db.
    import io
    import urllib.request
    import zipfile

    shows_db = mo.notebook_dir().parent / "data" / "shows.db"
    if not shows_db.exists():
        shows_db.parent.mkdir(exist_ok=True)
        with urllib.request.urlopen("https://cdn.cs50.net/2024/fall/lectures/7/src7.zip", timeout=120) as _reply:
            _archive = zipfile.ZipFile(io.BytesIO(_reply.read()))
        shows_db.write_bytes(_archive.read("src7/imdb/shows.db"))
    demo_db = Path(tempfile.mkdtemp()) / "shows-copy.db"
    shutil.copy(shows_db, demo_db)
    demo_db.name
    return (demo_db,)


@app.cell
def _(demo_db, mo, sqlite3):
    con = sqlite3.connect(demo_db)
    office_id = con.execute(
        "SELECT id FROM shows WHERE title = 'The Office' AND year = 2005"
    ).fetchone()[0]
    star_rows = con.execute("SELECT count(*) FROM stars").fetchone()[0]
    mo.md(f"`stars` has **{star_rows:,}** rows. The Office (2005) is show {office_id}.")
    return con, office_id


@app.cell
def _(statistics, time):
    def time_query(con, sql, params):
        # The middle of 20 runs, in milliseconds.
        runs = []
        for _ in range(20):
            start = time.perf_counter()
            con.execute(sql, params).fetchall()
            runs.append((time.perf_counter() - start) * 1000)
        return statistics.median(runs)

    find_stars = "SELECT person_id FROM stars WHERE show_id = ?"
    return find_stars, time_query


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Without an index

    SQLite reads every row of `stars` and keeps the ones for The Office. `EXPLAIN QUERY PLAN` says how it will find the rows.
    """)
    return


@app.cell
def _(con, find_stars, mo, office_id, time_query):
    plan_before = con.execute("EXPLAIN QUERY PLAN " + find_stars, [office_id]).fetchall()[0][-1]
    stars_found = len(con.execute(find_stars, [office_id]).fetchall())
    before_ms = time_query(con, find_stars, [office_id])
    mo.md(f"Plan: `{plan_before}`. Found {stars_found} stars in **{before_ms:.2f} ms**.")
    return (before_ms,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## With an index

    The index lists the values of `show_id` in order, each pointing to its rows. Building it takes a moment, and the file grows.
    """)
    return


@app.cell
def _(before_ms, con, demo_db, find_stars, mo, office_id, time_query):
    size_before = demo_db.stat().st_size
    con.execute("CREATE INDEX stars_by_show ON stars (show_id)")
    con.commit()
    size_after = demo_db.stat().st_size
    plan_after = con.execute("EXPLAIN QUERY PLAN " + find_stars, [office_id]).fetchall()[0][-1]
    after_ms = time_query(con, find_stars, [office_id])
    mo.md(
        f"Plan: `{plan_after}`. The same query in **{after_ms:.3f} ms**, "
        f"about {before_ms / after_ms:,.0f} times faster. "
        f"The file grew from {size_before / 1e6:.1f} MB to {size_after / 1e6:.1f} MB."
    )
    return


if __name__ == "__main__":
    app.run()
