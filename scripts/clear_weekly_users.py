#!/usr/bin/env python3

import os
import sqlite3

from sys import argv

argc = len(argv)

game_dir = "/usr/share/botany"
garden_db_path = os.path.join(game_dir, 'sqlite/garden_db.sqlite') if argc <= 1 else argv[1]

conn = sqlite3.connect(garden_db_path)
c = conn.cursor()
c.execute("DELETE FROM visitors")
print("Cleared weekly users")
conn.commit()
conn.close()
