import pickle
import time
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
#   What else should it do during life? growth alone is not all that
#   interesting.
#   how long should each stage last ? thinking realistic lmao

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
    def __init__(self):
        self.stage = 0
        self.mutation = 0
        self.species = random.randint(0,5)
        self.color = random.randint(0,10)
        self.rarity = self.rarity_check()

    def rarity_check(self):
        # todo: split this by math not literals
        rare_seed = random.randint(0,127)
        if 0<= rare_seed <= 63:
            rarity = 0
        elif 64 <= rare_seed <= 95:
            rarity = 1
        elif 96 <= rare_seed <= 111:
            rarity = 2
        elif 112 <= rare_seed <= 123:
            rarity = 3
        elif 124 <= rare_seed <= 127:
            rarity = 4
        return rarity

    def growth(self):
        if self.stage < 6:
            self.stage += 1
            # do stage growth stuff
            MUTATION_RARITY = 9
            mutation_seed = random.randint(0,MUTATION_RARITY)
            if mutation_seed == MUTATION_RARITY:
                mutation = random.randint(0,3)
                if self.mutation == 0:
                    self.mutation = mutation
        else:
            # do stage 5 stuff (after fruiting)
            1==1
    def parse_plant(self):
        stage_dict = {
            0: 'seed',
            1: 'seedling',
            2: 'young',
            3: 'grown',
            4: 'mature',
            5: 'flowering',
            6: 'fruiting',
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
            3: 'rose',
            4: 'cherry tree',
            5: 'fern',
        }

        mutation_dict = {
            0: '',
            1: 'humming',
            2: 'poisonous',
            3: 'vorpal',
            4: 'glowing'
        }
        if self.mutation == 0:
            print rarity_dict[self.rarity] +" "+ color_dict[self.color] +" "+ stage_dict[self.stage] +" "+ species_dict[self.species]
        else:
            print rarity_dict[self.rarity] +" "+ mutation_dict[self.mutation] +" "+ color_dict[self.color] +" "+ stage_dict[self.stage] +" "+ species_dict[self.species]

if __name__ == '__main__':
    my_plant = Plant()
    print my_plant.stage, my_plant.species, my_plant.color, my_plant.rarity
    while my_plant.stage < 6:
        raw_input("...")
        my_plant.growth()
        my_plant.parse_plant()

    print "end"
