from __future__ import division
import time
import pickle
import curses
import json
import math
import os.path
import random
import threading

# ideas go here
# lifecycle of a plant
# seed -> seedling -> sprout -> young plant -> mature plant -> flower ->
# pollination -> fruit -> seeds

# mutations over time to yield different things? idk
# neighboring plants can cross pollinate for different plants
# health based on checkups and watering

# development plan
# build plant lifecycle just stepping through
#   - What else should it do during life? growth alone is not all that
#   interesting.
#   - how long should each stage last ? thinking realistic lmao

# interaction
#   - watering?
#   - look at plant, how do you feel?
#   - fertilize?

# build time system
# build persistence across sessions

# build ascii trees
# build gui?

# build multiplayer

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


class Plant:
    stage_dict = {
        0: 'seed',
        1: 'seedling',
        2: 'young',
        3: 'mature',
        4: 'flowering',
        5: 'fruiting',
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
        10: 'chaos',
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

    def __init__(self):
        self.stage = 0
        self.mutation = 0
        self.species = random.randint(0,len(self.species_dict)-1)
        self.color = random.randint(0,len(self.color_dict)-1)
        self.rarity = self.rarity_check()
        self.ticks = 0

    def rarity_check(self):
        CONST_RARITY_MAX = 256.0
        rare_seed = random.randint(1,CONST_RARITY_MAX)
        common_range =    round((2/3)*CONST_RARITY_MAX)
        uncommon_range =  round((2/3)*(CONST_RARITY_MAX-common_range))
        rare_range =      round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range))
        legendary_range = round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range-rare_range))
        godly_range =     round((2/3)*(CONST_RARITY_MAX-common_range-uncommon_range-rare_range-legendary_range))

        # print common_range, uncommon_range, rare_range, legendary_range, godly_range

        common_max = common_range
        uncommon_max = common_max + uncommon_range
        rare_max = uncommon_max + rare_range
        legendary_max = rare_max + legendary_range
        godly_max = legendary_max + godly_range

        # print common_max, uncommon_max, rare_max, legendary_max, godly_max
        if   0 <= rare_seed <= common_max:
            rarity = 0
        elif common_max < rare_seed <= uncommon_max:
            rarity = 1
        elif uncommon_max < rare_seed <= rare_max:
            rarity = 2
        elif rare_max < rare_seed <= legendary_max:
            rarity = 3
        elif legendary_max < rare_seed <= CONST_RARITY_MAX:
            rarity = 4
        return rarity

    def growth(self):
        if self.stage < (len(self.stage_dict)-1):
            self.stage += 1
            # do stage growth stuff
            CONST_MUTATION_RARITY = 9 # Increase this # to make mutation rarer (chance 1 out of x)
            mutation_seed = random.randint(0,CONST_MUTATION_RARITY)
            if mutation_seed == CONST_MUTATION_RARITY:
                mutation = random.randint(0,len(self.mutation_dict)-1)
                if self.mutation == 0:
                    self.mutation = mutation
        else:
            # do stage 5 stuff (after fruiting)
            1==1
    def parse_plant(self):
        if self.mutation == 0:
            print self.rarity_dict[self.rarity] +" "+ self.color_dict[self.color] +" "+ self.stage_dict[self.stage] +" "+ self.species_dict[self.species]
        else:
            print self.rarity_dict[self.rarity] +" "+ self.mutation_dict[self.mutation] +" "+ self.color_dict[self.color] +" "+ self.stage_dict[self.stage] +" "+ self.species_dict[self.species]

    def live(self):
        # I've created life :)
        # life_stages = (5, 15, 30, 45, 60)
        life_stages = (5, 10, 15, 20, 25)
        self.parse_plant()
        while self.ticks <= 100:
            time.sleep(1)
            self.ticks += 1
            print self.ticks
            if self.stage < len(self.stage_dict)-1:
                if self.ticks == life_stages[self.stage]:
                    self.growth()
                    self.parse_plant()

if __name__ == '__main__':
    my_plant = Plant()
    print my_plant.stage, my_plant.species, my_plant.color, my_plant.rarity, my_plant.mutation
    # while my_plant.stage < len(my_plant.stage_dict):
    #     raw_input("...")
    #     my_plant.parse_plant()
    #     my_plant.growth()
    my_plant.live()
    print "end"
