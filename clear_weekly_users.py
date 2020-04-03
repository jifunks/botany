import os
import sqlite3

game_dir = os.path.dirname(os.path.realpath(__file__))
garden_db_path = os.path.join(game_dir, 'sqlite/garden_db.sqlite')
conn = sqlite3.connect(garden_db_path)
c = conn.cursor()
c.execute("DELETE FROM visitors")
print("Cleared weekly users")
conn.commit()
conn.close()
