#!/usr/bin/env python3
import datetime
from os import path
from getpass import getuser
import os
from datetime import timezone
import sqlite3
import sys
from typing import Optional, Tuple, TypeVar

BOTANY_DIR = ".botany"

dt = datetime.datetime

def now() -> dt:
    return dt.now(timezone.utc)

# flavor dict keys
# - color
# - rarity
# - species
# - mutation
PLOT_SCHEMA = """
CREATE TABLE IF NOT EXISTS plot (
    -- Each row is a plant
    id         INTEGER PRIMARY KEY,
    created    TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M', 'now', 'localtime')),
    watered    TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M', 'now', 'localtime')),
    generation INTEGER,
    flavor     JSON
)
"""

VISITORS_SCHEMA = """
CREATE TABLE IF NOT EXISTS visitors (
    -- Each row is a visit from another user
    id   INTEGER PRIMARY KEY,
    name TEXT,
    when TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M', 'now', 'localtime')),
)
"""

# TODO code for generating a global garden database (finds all most recent plants for users on system and fills a sqlite3 db with computed values)

def mkdir(p: str) -> Optional[Exception]:
    if not path.isdir(p):
        try:
            os.makedirs(p)
        except Exception as e:
            return Exception(f"failed to create {p}: {e}")
    return None

def mkdb(p: str, sql: str) -> Optional[Exception]:
    try:
        conn = sqlite3.connect(p)
        c = conn.cursor()
        c.execute(sql)
        conn.close()
    except Exception as e:
        return Exception(f"failed to initialize {p}: {e}")
    return None
    
def setup() -> Optional[Exception]:
    bdir = path.expanduser(path.join("~", BOTANY_DIR))
    e = mkdir(bdir)
    if e is not None:
        return e

    dbdir = path.join(bdir, "db")
    e = mkdir(dbdir)
    if e is not None:
        return e

    e = mkdb(path.join(bdir, "db/plot.db"), PLOT_SCHEMA)
    if e is not None:
        return e

    e = mkdb(path.join(bdir, "db/visitors.db"), VISITORS_SCHEMA)
    if e is not None:
        return e
    
    return None

def main() -> Optional[Exception]:
    username = getuser()

    e = setup()
    if e is not None:
        return e

    # TODO restore plant from disk
    return None

if __name__ == "__main__":
    ret = 0
    e = main()
    if e is not None:
        print(e)
        ret = 1
    sys.exit(ret)
