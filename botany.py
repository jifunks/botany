from __future__ import division
import time
import pickle
import json
import math
import os.path
import random
import getpass
import threading
import errno
import uuid
from operator import itemgetter
from menu_screen import *

# development plan

# build plant lifecycle just stepping through
#   - What else should it do during life? growth alone is not all that
#   interesting.
#   - how long should each stage last ? thinking realistic lmao
#   seed -> seedling -> sprout -> young plant -> mature plant -> flower ->
#   pollination -> fruit -> seeds
#   - TODO: pollination and end of life
#
# interaction
#   - look at plant, how do you feel? (also gets rid of pests)
#
# events
# - heatwave
# - rain
# - bugs
#
# build multiplayer
# neighborhood system
# - create plant id (sort of like userid)
# - list sorted by plantid that wraps so everybody has 2 neighbors :)
# - can water neighbors plant once (have to choose which)
# - pollination - seed is combination of your plant and neighbor plant
#   - create rarer species by diff gens
# - if neighbor plant dies, node will be removed from list
#
# garden system
# - can plant your plant in the garden to start a new plant

# build ascii trees


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
        10: 'cannabis',
        11: 'pansy',
        12: 'iris',
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

    def __init__(self, this_filename):
        # Constructor
        self.plant_id = str(uuid.uuid4())
        self.stage = 0
        self.mutation = 0
        self.species = random.randint(0,len(self.species_dict)-1)
        self.color = random.randint(0,len(self.color_dict)-1)
        self.rarity = self.rarity_check()
        self.ticks = 0
        self.age_formatted = "0"
        self.dead = False
        self.owner = getpass.getuser()
        self.file_name = this_filename
        self.start_time = int(time.time())
        self.last_time = int(time.time())
        # must water plant first day
        self.watered_timestamp = int(time.time())-(24*3600)-1
        # self.watered_timestamp = int(time.time()) # debug
        self.watered_24h = False

    def new_seed(self,this_filename):
        # Creates life after death
        self.__init__(this_filename)

    def rarity_check(self):
        # Generate plant rarity
        CONST_RARITY_MAX = 256.0
        rare_seed = random.randint(1,CONST_RARITY_MAX)
        common_range =    round((2/3)*CONST_RARITY_MAX)
        uncommon_range =  round((2/3)*(CONST_RARITY_MAX-common_range))
        rare_range =      round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range))
        legendary_range = round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range-rare_range))
        # godly_range =     round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range-rare_range-legendary_range))

        common_max = common_range
        uncommon_max = common_max + uncommon_range
        rare_max = uncommon_max + rare_range
        legendary_max = rare_max + legendary_range
        godly_max = CONST_RARITY_MAX

        if   0 <= rare_seed <= common_max:
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

    def growth(self):
        # Increase plant growth stage
        if self.stage < (len(self.stage_dict)-1):
            self.stage += 1
            # do stage growth stuff
        else:
            # do stage 5 stuff (after fruiting)
            1==1

    def water(self):
        # Increase plant growth stage
        # TODO: overwatering? if more than once a day it dies?
        if not self.dead:
            self.watered_timestamp = int(time.time())
            self.watered_24h = True


    def dead_check(self):
        time_delta_watered = int(time.time()) - self.watered_timestamp
        # if it has been >5 days since watering, sorry plant is dead :(
        if time_delta_watered > (5 * (24 * 3600)):
            self.dead = True
        return self.dead

    def kill_plant(self):
        self.dead = True

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
        # TODO: when out of debug this needs to be set to high number (1000
        # even maybe)
        CONST_MUTATION_RARITY = 10 # Increase this # to make mutation rarer (chance 1 out of x)
        mutation_seed = random.randint(1,CONST_MUTATION_RARITY)
        if mutation_seed == CONST_MUTATION_RARITY:
            # mutation gained!
            mutation = random.randint(0,len(self.mutation_dict)-1)
            if self.mutation == 0:
                self.mutation = mutation
                return True
        else:
            return False

    def parse_plant(self):
        # reads plant info (maybe want to reorg this into a different class
        # with the reader dicts...)
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

    def start_life(self):
       # runs life on a thread
       thread = threading.Thread(target=self.life, args=())
       thread.daemon = True
       thread.start()

    def life(self):
        # I've created life :)
        # TODO: change out of debug
        life_stages = (5, 15, 30, 45, 60)
        # day = 3600*24
        # life_stages = (1*day, 2*day, 3*day, 4*day, 5*day)
        # leave this untouched bc it works for now
        while True:
            time.sleep(1)
            if not self.dead:
                if self.watered_24h:
                    self.ticks += 1
                    if self.stage < len(self.stage_dict)-1:
                        if self.ticks >= life_stages[self.stage]:
                            self.growth()
                    if self.mutate_check():
                        1==1
            if self.water_check():
                1==1
            if self.dead_check():
                1==1
            # TODO: event check

class DataManager(object):
    # handles user data, puts a .botany dir in user's home dir (OSX/Linux)
    # TODO: windows... lol
    user_dir = os.path.expanduser("~")
    botany_dir = os.path.join(user_dir,'.botany')
    game_dir = os.path.dirname(os.path.realpath(__file__))

    this_user = getpass.getuser()
    savefile_name = this_user + '_plant.dat'
    savefile_path = os.path.join(botany_dir,savefile_name)
    garden_file_path = os.path.join(game_dir,'garden_file.dat')

    def __init__(self):
        self.this_user = getpass.getuser()
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
        # .1 second updates to minimize race condition
        # TODO: improve how this is handled to eliminate race condition
        while True:
            is_dead = this_plant.dead_check()
            if is_dead:
                self.save_plant(this_plant)
                self.data_write_json(this_plant)
                self.garden_update(this_plant)
            time.sleep(.1)

    def autosave(self, this_plant):
        # running on thread
        while True:
            self.save_plant(this_plant)
            self.data_write_json(this_plant)
            self.garden_update(this_plant)
            # TODO: change after debug
            #time.sleep(60)
            # TODO: if plant dies it should force save.
            time.sleep(5)

    def load_plant(self):
        # load savefile
        with open(self.savefile_path, 'rb') as f:
            this_plant = pickle.load(f)

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

    def garden_update(self, this_plant):
        # garden is a dict of dicts
        # garden contains one entry for each plant id

        age_formatted = self.plant_age_convert(this_plant)
        this_plant_id = this_plant.plant_id
        plant_info = {
                "owner":this_plant.owner,
                "description":this_plant.parse_plant(),
                "age":age_formatted,
                "score":this_plant.ticks,
                "dead":this_plant.dead,
        }

        if os.path.isfile(self.garden_file_path):
            # garden file exists: load data
            with open(self.garden_file_path, 'rb') as f:
                this_garden = pickle.load(f)
            new_file_check = False
            # TODO: it would be smart to lock this file down somehow, write to
            # it only through the software (to prevent tampering)
            os.chmod(self.garden_file_path, 0666)
        else:
            # create empty garden list
            this_garden = {}
            new_file_check = True
        # if current plant ID isn't in garden list
        if this_plant.plant_id not in this_garden:
            this_garden[this_plant_id] = plant_info
        # if plant ticks for id is greater than current ticks of plant id
        else:
            current_plant_ticks = this_garden[this_plant_id]["score"]
            if this_plant.ticks > current_plant_ticks:
                this_garden[this_plant_id] = plant_info
        with open(self.garden_file_path, 'wb') as f:
            pickle.dump(this_garden, f, protocol=2)

        # create json file from plant_info
        garden_json_path = os.path.join(self.game_dir,'garden_file.json')
        with open(garden_json_path, 'w') as outfile:
            json.dump(this_garden, outfile)

        return new_file_check

    def save_plant(self, this_plant):
        # create savefile
        this_plant.last_time = int(time.time())
        with open(self.savefile_path, 'wb') as f:
            pickle.dump(this_plant, f, protocol=2)

    def data_write_json(self, this_plant):
        # create personal json file for user to use outside of the game (website?)
        json_file = os.path.join(self.botany_dir,self.this_user + '_plant_data.json')
        json_leaderboard = os.path.join(self.game_dir + '_garden.json')
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
        }
        with open(json_file, 'w') as outfile:
            json.dump(plant_info, outfile)

        # update leaderboard 'garden' for display in game
        # also should be a pickle file bc... let's be honest ppl want to cheat

if __name__ == '__main__':
    my_data = DataManager()
    # if plant save file exists
    if my_data.check_plant():
        my_plant = my_data.load_plant()
    # otherwise create new plant
    else:
        #TODO: onboarding, select seed, select whatever else
        my_plant = Plant(my_data.savefile_path)
        my_data.data_write_json(my_plant)
    my_plant.start_life()
    my_data.start_threads(my_plant)
botany_menu = CursedMenu(my_plant,my_data.garden_file_path)
    botany_menu.show(["water","look","garden","instructions"], title=' botany ', subtitle='options')
    my_data.save_plant(my_plant)
    my_data.data_write_json(my_plant)
    my_data.garden_update(my_plant)
