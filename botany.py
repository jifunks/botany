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
from menu_screen import *
# ideas go here
# lifecycle of a plant
# seed -> seedling -> sprout -> young plant -> mature plant -> flower ->
# pollination -> fruit -> seeds

# neighboring plants can cross pollinate for different plants
# health based on checkups and watering

# development plan
# build plant lifecycle just stepping through
#   - What else should it do during life? growth alone is not all that
#   interesting.
#   - how long should each stage last ? thinking realistic lmao

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


# def display_update:
#     myscreen = curses.initscr()
#
#     myscreen.border(0)
#     myscreen.addstr(1, 2, "you've planted a seed")
#     myscreen.refresh()
#
#     for i in range(1,20):
#         myscreen.addstr(i, 2, str(i))
#         time.sleep(1)
#         myscreen.refresh()
#
#     myscreen.getch()
#
#     curses.endwin()


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
    }

    def __init__(self, this_filename):
        # Constructor
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
        self.watered_timestamp = int(time.time())-(24*3601)
        # self.watered_timestamp = int(time.time()) # debug
        self.watered_times = 0
        self.watered_24h = False

    def rarity_check(self):
        # Generate plant rarity
        CONST_RARITY_MAX = 256.0
        rare_seed = random.randint(1,CONST_RARITY_MAX)
        common_range =    round((2/3)*CONST_RARITY_MAX)
        uncommon_range =  round((2/3)*(CONST_RARITY_MAX-common_range))
        rare_range =      round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range))
        legendary_range = round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range-rare_range))
        # godly_range =     round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range-rare_range-legendary_range))

        # print common_range, uncommon_range, rare_range, legendary_range, godly_range

        common_max = common_range
        uncommon_max = common_max + uncommon_range
        rare_max = uncommon_max + rare_range
        legendary_max = rare_max + legendary_range
        godly_max = CONST_RARITY_MAX

        # print common_max, uncommon_max, rare_max, legendary_max, godly_max
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
            #TODO: this should only be allowed once a day
            self.watered_times += 1
            self.watered_24h = True

    def convert_seconds(self,seconds):
        days, seconds = divmod(seconds, 24 * 60 * 60)
        hours, seconds = divmod(seconds, 60 * 60)
        minutes, seconds = divmod(seconds, 60)
        return days, hours, minutes, seconds

    def dead_check(self):
        # also updates age
        d,h,m,s = self.convert_seconds(self.ticks)
        self.age_formatted = ("%dd:%dh:%dm:%ds" % (d, h, m, s)) 
        time_delta_watered = int(time.time()) - self.watered_timestamp
        # if it has been >5 days since watering, sorry plant is dead :(
        # if time_delta_watered > 5: #debug
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
        # TODO: when out of debug this needs to be set to high number (1000
        # even maybe)
        CONST_MUTATION_RARITY = 10 # Increase this # to make mutation rarer (chance 1 out of x)
        mutation_seed = random.randint(1,CONST_MUTATION_RARITY)
        if mutation_seed == CONST_MUTATION_RARITY:
            # mutation gained!
            mutation = random.randint(0,len(self.mutation_dict)-1)
            if self.mutation == 0:
                self.mutation = mutation
                #print "mutation!"
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
        # print output
        return output

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
        while (not self.dead):
            time.sleep(1)
            if self.watered_24h:
                self.ticks += 1
                if self.stage < len(self.stage_dict)-1:
                    if self.ticks >= life_stages[self.stage]:
                        self.growth()
                        #print self.parse_plant()
            if self.mutate_check():
                1==1
            if self.dead_check():
                1==1
            if self.water_check():
                1==1
            # TODO: event check

class DataManager(object):
    # handles user data, puts a .botany dir in user's home dir (OSX/Linux)
    # TODO: windows... lol
    user_dir = os.path.expanduser("~")
    botany_dir = os.path.join(user_dir,'.botany')
    this_user = getpass.getuser()
    savefile_name = this_user + '_plant.dat'
    savefile_path = os.path.join(botany_dir,savefile_name)

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

    def save_plant(self, this_plant):
        # create savefile
        this_plant.last_time = int(time.time())
        with open(self.savefile_path, 'wb') as f:
            pickle.dump(this_plant, f, protocol=2)

    def load_plant(self):
        # load savefile
        # need to calculate lifetime ticks to determine stage of life
        with open(self.savefile_path, 'rb') as f:
            this_plant = pickle.load(f)
        # compare timestamp of signout to timestamp now
        is_dead = this_plant.dead_check()
        is_watered = this_plant.water_check()

        # if it has been >5 days since watering, sorry plant is dead :(
        if not is_dead:
            if is_watered:
                #need to use time AWAY (i.e. this_plant.last_time)
                time_delta_last = int(time.time()) - this_plant.last_time
                ticks_to_add = min(time_delta_last, 24*3600)
                this_plant.time_delta_watered = 0
                self.last_water_gain = time.time()
            else:
                ticks_to_add = 0
            this_plant.ticks += ticks_to_add

        return this_plant

    def data_write_json(self, this_plant):
        # create json file for user to use outside of the game (website?)
        json_file = os.path.join(self.botany_dir,self.this_user + '_plant_data.json')
        with open(json_file, 'w') as outfile:
            json.dump(this_plant.__dict__, outfile)

if __name__ == '__main__':
    my_data = DataManager()
    # if plant save file exists
    if my_data.check_plant():
        #print "Welcome back, " + getpass.getuser()
        my_plant = my_data.load_plant()
        #print my_plant.parse_plant()
    # otherwise create new plant
    else:
        #print "Welcome, " + getpass.getuser()
        #TODO: onboarding, select seed, select whatever else
        my_plant = Plant(my_data.savefile_path)
    my_plant.start_life()
    #print "Your plant is living :)"
    botany_menu = CursedMenu(my_plant)
    botany_menu.show([1,"water","look","instructions"], title=' botany ', subtitle='Options')
    #raw_input('Press return to save and exit...\n')
    my_data.save_plant(my_plant)
    my_data.data_write_json(my_plant)
    #print "end"

