#!/usr/bin/env python3
import curses
import datetime
from os import path
from getpass import getuser
import os
from datetime import timezone
import sqlite3
import sys
from time import sleep
from typing import Optional, Tuple, TypeVar

BOTANY_DIR = ".botany"
MIN_SCREEN_WIDTH = 70
MIN_SCREEN_HEIGHT = 20
INTERVAL = 1

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
    at   TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M', 'now', 'localtime'))
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

    # TODO rug sweep curses stuff
    parentwin = curses.initscr()
    parentwin.keypad(True)
    curses.noecho()
    curses.raw()
    if curses.has_colors():
        curses.start_color()
    try:
        curses.curs_set(0)
    except curses.error:
        # Not all terminals support this functionality.
        # When the error is ignored the screen will be slightly uglier but functional
        # so we ignore this error for terminal compatibility.
        pass
    if curses.COLS < MIN_SCREEN_WIDTH:
        return Exception("the terminal window is too narrow")
    if curses.LINES < MIN_SCREEN_HEIGHT:
        return Exception("the terminal window is too short")

    menuwin = curses.newwin(10, 30, 4, 2)
    plantwin = curses.newwin(30, 40, 4, 31)
    scorewin = curses.newwin(2, 30, 15, 2)
    # TODO info area (is this where prompt is rendered?)

    while True:
        c = parentwin.getch()
        if c == -1 or c == ord("q") or c == ord("x") or c == 27:
            break
        sleep(INTERVAL)
    
    try:
        curses.curs_set(2)
    except curses.error:
        # cursor not supported; just ignore
        pass
    curses.endwin()
    os.system('clear')

    return None

if __name__ == "__main__":
    ret = 0
    e = main()
    if e is not None:
        print(e, file=sys.stderr)
        ret = 1
    sys.exit(ret)
