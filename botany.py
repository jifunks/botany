#!/usr/bin/python2

from __future__ import division
import time
import pickle
import json
import os
import random
import getpass
import threading
import errno
import uuid
import sqlite3
from menu_screen import *

# TODO:
# - Switch from personal data file to table in DB
# - Table in DB would allow others to modify (personal files might be
# permission locked)
# - this is a good idea.

class Plant(object):
    # This is your plant!
    stage_dict = {
        0: 'seed',
        1: 'seedling',
        2: 'young',
        3: 'mature',
        4: 'flowering',
        5: 'seed-bearing',
    }

    color_dict = {
        0: 'red',
        1: 'orange',
        2: 'yellow',
        3: 'green',
        4: 'blue',
        5: 'indigo',
        6: 'violet',
        7: 'white',
        8: 'black',
        9: 'gold',
        10: 'rainbow',
    }

    rarity_dict = {
        0: 'common',
        1: 'uncommon',
        2: 'rare',
        3: 'legendary',
        4: 'godly',
    }

    species_dict = {
        0: 'poppy',
        1: 'cactus',
        2: 'aloe',
        3: 'venus flytrap',
        4: 'jade plant',
        5: 'fern',
        6: 'daffodil',
        7: 'sunflower',
        8: 'baobab',
        9: 'lithops',
        10: 'hemp',
        11: 'pansy',
        12: 'iris',
        13: 'agave',
        14: 'ficus',
        15: 'moss',
        16: 'sage',
        17: 'snapdragon',
        18: 'columbine',
        19: 'brugmansia',
        20: 'palm',
    }

    mutation_dict = {
        0: '',
        1: 'humming',
        2: 'noxious',
        3: 'vorpal',
        4: 'glowing',
        5: 'electric',
        6: 'icy',
        7: 'flaming',
        8: 'psychic',
        9: 'screaming',
        10: 'chaotic',
        11: 'hissing',
        12: 'gelatinous',
        13: 'deformed',
        14: 'shaggy',
        15: 'scaly',
        16: 'depressed',
        17: 'anxious',
        18: 'metallic',
        19: 'glossy',
        20: 'psychedelic',
        21: 'bonsai',
        22: 'foamy',
        23: 'singing',
        24: 'fractal',
        25: 'crunchy',
        26: 'goth',
        27: 'oozing',
        28: 'stinky',
        29: 'aromatic',
        30: 'juicy',
        31: 'smug',
        32: 'vibrating',
        33: 'lithe',
        34: 'chalky',
        35: 'naive',
        36: 'ersatz',
        37: 'disco',
        38: 'levitating',
        39: 'colossal',
    }

    def __init__(self, this_filename, generation=1):
        # Constructor
        self.plant_id = str(uuid.uuid4())
        self.life_stages = (3600*24, (3600*24)*3, (3600*24)*10, (3600*24)*20, (3600*24)*30)
        self.stage = 0
        self.mutation = 0
        self.species = random.randint(0,len(self.species_dict)-1)
        self.color = random.randint(0,len(self.color_dict)-1)
        self.rarity = self.rarity_check()
        self.ticks = 0
        self.age_formatted = "0"
        self.generation = generation
        self.dead = False
        self.write_lock = False
        self.owner = getpass.getuser()
        self.file_name = this_filename
        self.start_time = int(time.time())
        self.last_time = int(time.time())
        # must water plant first day
        self.watered_timestamp = int(time.time())-(24*3600)-1
        self.watered_24h = False

    def migrate_properties(self):
        # Migrates old data files to new
        if not hasattr(self, 'generation'):
            self.generation = 1

    def parse_plant(self):
        # Converts plant data to human-readable format
        output = ""
        if self.stage >= 3:
            output += self.rarity_dict[self.rarity] + " "
        if self.mutation != 0:
            output += self.mutation_dict[self.mutation] + " "
        if self.stage >= 4:
            output += self.color_dict[self.color] + " "
        output += self.stage_dict[self.stage] + " "
        if self.stage >= 2:
            output += self.species_dict[self.species] + " "
        return output.strip()

    def rarity_check(self):
        # Generate plant rarity
        CONST_RARITY_MAX = 256.0
        rare_seed = random.randint(1,CONST_RARITY_MAX)
        common_range =    round((2/3)*CONST_RARITY_MAX)
        uncommon_range =  round((2/3)*(CONST_RARITY_MAX-common_range))
        rare_range =      round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range))
        legendary_range = round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range-rare_range))

        common_max = common_range
        uncommon_max = common_max + uncommon_range
        rare_max = uncommon_max + rare_range
        legendary_max = rare_max + legendary_range
        godly_max = CONST_RARITY_MAX

        if 0 <= rare_seed <= common_max:
            rarity = 0
        elif common_max < rare_seed <= uncommon_max:
            rarity = 1
        elif uncommon_max < rare_seed <= rare_max:
            rarity = 2
        elif rare_max < rare_seed <= legendary_max:
            rarity = 3
        elif legendary_max < rare_seed <= godly_max:
            rarity = 4
        return rarity

    def dead_check(self):
        # if it has been >5 days since watering, sorry plant is dead :(
        time_delta_watered = int(time.time()) - self.watered_timestamp
        if time_delta_watered > (5 * (24 * 3600)):
            self.dead = True
        return self.dead

    def water_check(self):
        # if plant has been watered in 24h then it keeps growing
        # time_delta_watered is difference from now to last watered
        self.time_delta_watered = int(time.time()) - self.watered_timestamp
        if self.time_delta_watered <= (24 * 3600):
            return True
        else:
            self.watered_24h = False
            return False

    def mutate_check(self):
        # Create plant mutation
        # Increase this # to make mutation rarer (chance 1 out of x each second)
        CONST_MUTATION_RARITY = 20000
        mutation_seed = random.randint(1,CONST_MUTATION_RARITY)
        if mutation_seed == CONST_MUTATION_RARITY:
            # mutation gained!
            mutation = random.randint(0,len(self.mutation_dict)-1)
            if self.mutation == 0:
                self.mutation = mutation
                return True
        else:
            return False

    def growth(self):
        # Increase plant growth stage
        if self.stage < (len(self.stage_dict)-1):
            self.stage += 1

    def water(self):
        # Increase plant growth stage
        if not self.dead:
            self.watered_timestamp = int(time.time())
            self.watered_24h = True

    def start_over(self):
        # After plant reaches final stage, given option to restart
        # increment generation only if previous stage is final stage and plant
        # is alive
        if not self.dead:
            next_generation = self.generation + 1
        else:
            # Should this reset to 1? Seems unfair.. for now generations will
            # persist through death.
            next_generation = self.generation

        self.write_lock = True
        self.kill_plant()
        while self.write_lock:
            # Wait for garden writer to unlock
            # garden db needs to update before allowing the user to reset
            pass
        if not self.write_lock:
            self.__init__(self.file_name, next_generation)

    def kill_plant(self):
        self.dead = True

    def unlock_new_creation(self):
        self.write_lock = False

    def start_life(self):
       # runs life on a thread
       thread = threading.Thread(target=self.life, args=())
       thread.daemon = True
       thread.start()

    def life(self):
        # I've created life :)
        while True:
            if not self.dead:
                if self.watered_24h:
                    self.ticks += 1
                    if self.stage < len(self.stage_dict)-1:
                        if self.ticks >= self.life_stages[self.stage]:
                            self.growth()
                    if self.mutate_check():
                        pass
            if self.water_check():
                # Do something
                pass
            if self.dead_check():
                # Do something else
                pass
            # TODO: event check
            generation_bonus = 0.2 * (self.generation - 1)
            adjusted_sleep_time = 1 / (1 + generation_bonus)
            time.sleep(adjusted_sleep_time)

class DataManager(object):
    # handles user data, puts a .botany dir in user's home dir (OSX/Linux)
    # handles shared data with sqlite db

    user_dir = os.path.expanduser("~")
    botany_dir = os.path.join(user_dir,'.botany')
    game_dir = os.path.dirname(os.path.realpath(__file__))
    this_user = getpass.getuser()

    savefile_name = this_user + '_plant.dat'
    savefile_path = os.path.join(botany_dir, savefile_name)
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
        # running on thread, saves plant every 5s
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

    def update_garden_db(self, this_plant):
        # insert or update this plant id's entry in DB
        self.init_database()
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
        with open(self.savefile_path, 'wb') as f:
            pickle.dump(this_plant, f, protocol=2)

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
                "stage": this_plant.stage_dict[this_plant.stage],
                "generation": this_plant.generation,
        }
        if this_plant.stage >= 3:
            plant_info["rarity"] = this_plant.rarity_dict[this_plant.rarity]
        if this_plant.mutation != 0:
            plant_info["mutation"] = this_plant.mutation_dict[this_plant.mutation]
        if this_plant.stage >= 4:
            plant_info["color"] = this_plant.color_dict[this_plant.color]
        if this_plant.stage >= 2:
            plant_info["species"] = this_plant.species_dict[this_plant.species]

        with open(json_file, 'w') as outfile:
            json.dump(plant_info, outfile)

    def harvest_plant(self, this_plant):
        # TODO: could just use a sqlite query to retrieve all of user's dead
        # plants

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
        with open(self.harvest_file_path, 'wb') as f:
            pickle.dump(this_harvest, f, protocol=2)
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
    my_plant.start_life()
    my_data.start_threads(my_plant)
    botany_menu = CursedMenu(my_plant,my_data)
    my_data.save_plant(my_plant)
    my_data.data_write_json(my_plant)
    my_data.update_garden_db(my_plant)
