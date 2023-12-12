#!/usr/bin/env python3

import time
import pickle
import json
import os
import getpass
import threading
import errno
import sqlite3
import menu_screen as ms
from plant import Plant

# TODO:
# - switch from personal data file to row in DB
# - is threading necessary?
# - use a different curses window for plant, menu, info window, score

# notes from vilmibm

# there are threads.
# - life thread. sleeps a variable amount of time based on generation bonus. increases tick count (ticks == score).
# - screen: sleeps 1s per loop. draws interface (including plant). for seeing score/plant change without user input.
# meanwhile, the main thread handles input and redraws curses as needed.

# affordance index
# - main screen
#  navigable menu, plant, score, etc
# - water
#  render a visualization of moistness; allow to water
# - look
#  print a description of plant with info below rest of UI
# - garden
#  runs a paginated view of every plant on the computer below rest of UI. to return to menu navigation must hit q.
# - visit
#  runs a prompt underneath UI where you can see who recently visited you and type in a name to visit. must submit the prompt to get back to menu navigation.
# - instructions
#  prints some explanatory text below the UI
# - exit
#  quits program

# part of the complexity of all this is everything takes place in one curses window; thus, updates must be manually synchronized across the various logical parts of the screen.
# ideally, multiple windows would be used:
# - the menu. it doesn't change unless the plant dies OR the plant hits stage 5, then "harvest" is dynamically added.
# - the plant viewer. this is updated in "real time" as the plant grows.
# - the status display: score and plant description
# - the infow window. updated by visit/garden/instructions/look

class DataManager(object):
    # handles user data, puts a .botany dir in user's home dir (OSX/Linux)
    # handles shared data with sqlite db
    # TODO: .dat save should only happen on mutation, water, death, exit,
    # harvest, otherwise
    # data hasn't changed...
    # can write json whenever bc this isn't ever read for data within botany

    user_dir = os.path.expanduser("~")
    botany_dir = os.path.join(user_dir,'.botany')
    game_dir = os.path.dirname(os.path.realpath(__file__))
    this_user = getpass.getuser()

    savefile_name = this_user + '_plant.dat'
    savefile_path = os.path.join(botany_dir, savefile_name)
    #set this.savefile_path to guest_garden path

    garden_db_path = os.path.join(game_dir, 'sqlite/garden_db.sqlite')
    garden_json_path = os.path.join(game_dir, 'garden_file.json')
    harvest_file_path = os.path.join(botany_dir, 'harvest_file.dat')
    harvest_json_path = os.path.join(botany_dir, 'harvest_file.json')

    def __init__(self):
        self.this_user = getpass.getuser()
        # check if instance is already running
        # check for .botany dir in home
        try:
            os.makedirs(self.botany_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        self.savefile_name = self.this_user + '_plant.dat'

    def check_plant(self):
        # check for existing save file
        if os.path.isfile(self.savefile_path) and os.path.getsize(self.savefile_path) > 0:
            return True
        else:
            return False

    def load_plant(self):
        # load savefile
        with open(self.savefile_path, 'rb') as f:
            this_plant = pickle.load(f)

        # migrate data structure to create data for empty/nonexistent plant
        # properties
        this_plant.migrate_properties()

        # get status since last login
        is_watered = this_plant.water_check()
        is_dead = this_plant.dead_check()

        if not is_dead:
            if is_watered:
                time_delta_last = int(time.time()) - this_plant.last_time
                ticks_to_add = min(time_delta_last, 24*3600)
                this_plant.time_delta_watered = 0
                self.last_water_gain = time.time()
            else:
                ticks_to_add = 0
            this_plant.ticks += ticks_to_add * round(0.2 * (this_plant.generation - 1) + 1, 1)
        return this_plant

    def plant_age_convert(self,this_plant):
        # human-readable plant age
        age_seconds = int(time.time()) - this_plant.start_time
        days, age_seconds = divmod(age_seconds, 24 * 60 * 60)
        hours, age_seconds = divmod(age_seconds, 60 * 60)
        minutes, age_seconds = divmod(age_seconds, 60)
        age_formatted = ("%dd:%dh:%dm:%ds" % (days, hours, minutes, age_seconds))
        return age_formatted

    def init_database(self):
        # check if dir exists, create sqlite directory and set OS permissions to 777
        sqlite_dir_path = os.path.join(self.game_dir,'sqlite')
        if not os.path.exists(sqlite_dir_path):
            os.makedirs(sqlite_dir_path)
            os.chmod(sqlite_dir_path, 0o777)
        conn = sqlite3.connect(self.garden_db_path)
        init_table_string = """CREATE TABLE IF NOT EXISTS garden (
        plant_id tinytext PRIMARY KEY,
        owner text,
        description text,
        age text,
        score integer,
        is_dead numeric
        )"""

        c = conn.cursor()
        c.execute(init_table_string)
        conn.close()

        # init only, creates and sets permissions for garden db and json
        if os.stat(self.garden_db_path).st_uid == os.getuid():
            os.chmod(self.garden_db_path, 0o666)
            open(self.garden_json_path, 'a').close()
            os.chmod(self.garden_json_path, 0o666)

    def migrate_database(self):
        conn = sqlite3.connect(self.garden_db_path)
        migrate_table_string = """CREATE TABLE IF NOT EXISTS visitors (
        id integer PRIMARY KEY,
        garden_name text,
        visitor_name text,
        weekly_visits integer
        )"""
        c = conn.cursor()
        c.execute(migrate_table_string)
        conn.close()
        return True

    def update_garden_db(self, this_plant):
        # insert or update this plant id's entry in DB
        self.init_database()
        self.migrate_database()
        age_formatted = self.plant_age_convert(this_plant)
        conn = sqlite3.connect(self.garden_db_path)
        c = conn.cursor()
        # try to insert or replace
        update_query = """INSERT OR REPLACE INTO garden (
                    plant_id, owner, description, age, score, is_dead
                    ) VALUES (
                    '{pid}', '{pown}', '{pdes}', '{page}', {psco}, {pdead}
                    )
                    """.format(pid = this_plant.plant_id,
                            pown = this_plant.owner,
                            pdes = this_plant.parse_plant(),
                            page = age_formatted,
                            psco = str(this_plant.ticks),
                            pdead = int(this_plant.dead))
        c.execute(update_query)
        # clean other instances of user
        clean_query = """UPDATE garden set is_dead = 1
                   where owner = '{pown}'
                   and plant_id <> '{pid}'
                   """.format(pown = this_plant.owner,
                              pid = this_plant.plant_id)
        c.execute(clean_query)
        conn.commit()
        conn.close()

    def retrieve_garden_from_db(self):
        # Builds a dict of dicts from garden sqlite db
        garden_dict = {}
        conn = sqlite3.connect(self.garden_db_path)
        # Need to allow write permissions by others
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM garden ORDER BY owner')
        tuple_list = c.fetchall()
        conn.close()
        # Building dict from table rows
        for item in tuple_list:
            garden_dict[item[0]] = {
                "owner":item[1],
                "description":item[2],
                "age":item[3],
                "score":item[4],
                "dead":item[5],
            }
        return garden_dict

    def update_garden_json(self):
        this_garden = self.retrieve_garden_from_db()
        with open(self.garden_json_path, 'w') as outfile:
            json.dump(this_garden, outfile)
        pass

    def save_plant(self, this_plant):
        # create savefile
        this_plant.last_time = int(time.time())
        temp_path = self.savefile_path + ".temp"
        with open(temp_path, 'wb') as f:
            pickle.dump(this_plant, f, protocol=2)
        os.rename(temp_path, self.savefile_path)

    def data_write_json(self, this_plant):
        # create personal json file for user to use outside of the game (website?)
        json_file = os.path.join(self.botany_dir,self.this_user + '_plant_data.json')
        # also updates age
        age_formatted = self.plant_age_convert(this_plant)
        plant_info = {
                "owner":this_plant.owner,
                "description":this_plant.parse_plant(),
                "age":age_formatted,
                "score":this_plant.ticks,
                "is_dead":this_plant.dead,
                "last_watered":this_plant.watered_timestamp,
                "file_name":this_plant.file_name,
                "stage": this_plant.stage_list[this_plant.stage],
                "generation": this_plant.generation,
        }
        if this_plant.stage >= 3:
            plant_info["rarity"] = this_plant.rarity_list[this_plant.rarity]
        if this_plant.mutation != 0:
            plant_info["mutation"] = this_plant.mutation_list[this_plant.mutation]
        if this_plant.stage >= 4:
            plant_info["color"] = this_plant.color_list[this_plant.color]
        if this_plant.stage >= 2:
            plant_info["species"] = this_plant.species_list[this_plant.species]

        with open(json_file, 'w') as outfile:
            json.dump(plant_info, outfile)

    def harvest_plant(self, this_plant):
        # TODO: plant history feature -  could just use a sqlite query to retrieve all of user's dead plants

        # harvest is a dict of dicts
        # harvest contains one entry for each plant id
        age_formatted = self.plant_age_convert(this_plant)
        this_plant_id = this_plant.plant_id
        plant_info = {
                "description":this_plant.parse_plant(),
                "age":age_formatted,
                "score":this_plant.ticks,
        }
        if os.path.isfile(self.harvest_file_path):
            # harvest file exists: load data
            with open(self.harvest_file_path, 'rb') as f:
                this_harvest = pickle.load(f)
            new_file_check = False
        else:
            this_harvest = {}
            new_file_check = True

        this_harvest[this_plant_id] = plant_info

        # dump harvest file
        temp_path = self.harvest_file_path + ".temp"
        with open(temp_path, 'wb') as f:
            pickle.dump(this_harvest, f, protocol=2)
        os.rename(temp_path, self.harvest_file_path)
        # dump json file
        with open(self.harvest_json_path, 'w') as outfile:
            json.dump(this_harvest, outfile)

        return new_file_check

if __name__ == '__main__':
    my_data = DataManager()
    # if plant save file exists
    if my_data.check_plant():
        my_plant = my_data.load_plant()
    # otherwise create new plant
    else:
        my_plant = Plant(my_data.savefile_path)
        my_data.data_write_json(my_plant)
    # my_plant is either a fresh plant or an existing plant at this point
    my_plant.start_life(my_data)

    try:
        botany_menu = ms.CursedMenu(my_plant,my_data)
        my_data.save_plant(my_plant)
        my_data.data_write_json(my_plant)
        my_data.update_garden_db(my_plant)
    finally:
        ms.cleanup()
