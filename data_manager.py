from __future__ import division
import time
import pickle
import json
import os
import getpass
import threading
import errno
import sqlite3

class DataManager(object):
    # handles user data, puts a .botany dir in user's home dir (OSX/Linux)
    # handles shared data with sqlite db
    # TODO: .dat save should only happen on mutation, water, death, exit,
    # harvest, otherwise
    # data hasn't changed...
    # can write json whenever bc this isn't ever read for data within botany

    def __init__(self, this_user = None):
        self.this_user = this_user
        if this_user is None:
            self.this_user = getpass.getuser()
        self.user_dir = os.path.expanduser("~" + self.this_user)
        self.botany_dir = os.path.join(self.user_dir,'.botany')
        self.game_dir = os.path.dirname(os.path.realpath(__file__))

        self.savefile_name = self.this_user + '_plant.dat'
        self.savefile_path = os.path.join(self.botany_dir, self.savefile_name)
        #set this.savefile_path to guest_garden path

        self.garden_db_path = os.path.join(self.game_dir, 'sqlite/garden_db.sqlite')
        self.garden_json_path = os.path.join(self.game_dir, 'garden_file.json')
        self.harvest_file_path = os.path.join(self.botany_dir, 'harvest_file.dat')
        self.harvest_json_path = os.path.join(self.botany_dir, 'harvest_file.json')

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
        if os.path.isfile(self.savefile_path):
            return True
        else:
            return False

    def start_threads(self,this_plant):
        # creates threads to save files every minute
        death_check_thread = threading.Thread(target=self.death_check_update, args=(this_plant,))
        death_check_thread.daemon = True
        death_check_thread.start()
        autosave_thread = threading.Thread(target=self.autosave, args=(this_plant,))
        autosave_thread.daemon = True
        autosave_thread.start()

    def death_check_update(self,this_plant):
        # .1 second updates and lock to minimize race condition
        while True:
            is_dead = this_plant.dead_check()
            if is_dead:
                self.save_plant(this_plant)
                self.data_write_json(this_plant)
                self.update_garden_db(this_plant)
                self.harvest_plant(this_plant)
                this_plant.unlock_new_creation()
            time.sleep(.1)

    def autosave(self, this_plant):
        # running on thread, saves plant every 5s TODO: this is unnecessary
        # and breaks shit probably
        file_update_count = 0
        while True:
            file_update_count += 1
            self.save_plant(this_plant)
            self.data_write_json(this_plant)
            self.update_garden_db(this_plant)
            if file_update_count == 12:
                # only update garden json every 60s
                self.update_garden_json()
            time.sleep(5)
            file_update_count %= 12

    def load_plant(self):
        # load savefile
        with open(self.savefile_path, 'rb') as f:
            this_plant = pickle.load(f)

        # migrate data structure to create data for empty/nonexistent plant
        # properties
        this_plant.migrate_properties()

        # get status since last login
        is_dead = this_plant.dead_check()
        is_watered = this_plant.water_check()

        if not is_dead:
            if is_watered:
                time_delta_last = int(time.time()) - this_plant.last_time
                ticks_to_add = min(time_delta_last, 24*3600)
                this_plant.time_delta_watered = 0
                self.last_water_gain = time.time()
            else:
                ticks_to_add = 0
            this_plant.ticks += ticks_to_add
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
            os.chmod(sqlite_dir_path, 0777)
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
            os.chmod(self.garden_db_path, 0666)
            open(self.garden_json_path, 'a').close()
            os.chmod(self.garden_json_path, 0666)

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
        # TODO: make sure other instances of user are deleted
        #   Could create a clean db function
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
