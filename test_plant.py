"""Regression test: Plant.update_visitor_db must record guest visits.

Before the fix, `plant.py` never imported `sqlite3`, so any guest
watering recorded in ~/.botany/visitors.json crashed the CLI with
`NameError: name 'sqlite3' is not defined` from `update_visitor_db`.
"""
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import plant


def _visitors_db(path):
    conn = sqlite3.connect(str(path))
    conn.execute(
        "CREATE TABLE visitors (id integer PRIMARY KEY, garden_name text,"
        " visitor_name text, weekly_visits integer)"
    )
    conn.commit()
    return conn


def test_update_visitor_db_records_guest_visit(tmp_path, monkeypatch):
    db_path = tmp_path / "garden_db.sqlite"
    seed = _visitors_db(db_path)
    seed.close()

    real_connect = sqlite3.connect

    def fake_connect(path, *args, **kwargs):
        assert str(path).endswith("garden_db.sqlite")
        return real_connect(str(db_path), *args, **kwargs)

    monkeypatch.setattr(plant.sqlite3, "connect", fake_connect)

    guest_book = plant.Plant.__new__(plant.Plant)
    guest_book.owner = "tester"
    guest_book.update_visitor_db(["guest1"])
    guest_book.update_visitor_db(["guest1"])

    rows = real_connect(str(db_path)).execute(
        "SELECT visitor_name, weekly_visits FROM visitors"
    ).fetchall()
    assert rows == [("guest1", 2)]
