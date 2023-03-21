#!/usr/bin/env python3
from botany import *

def ascii_render(filename):
    # Prints ASCII art from file at given coordinates
    this_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"art")
    this_filename = os.path.join(this_dir,filename)
    this_file = open(this_filename,"r")
    this_string = this_file.read()
    this_file.close()
    print(this_string)
 
def draw_plant_ascii(this_plant):
    # this list should be somewhere where it could have been inherited, instead
    # of hardcoded in more than one place...
    plant_art_list = [
        'poppy',
        'cactus',
        'aloe',
        'flytrap',
        'jadeplant',
        'fern',
        'daffodil',
        'sunflower',
        'baobab',
        'lithops',
        'hemp',
        'pansy',
        'iris',
        'agave',
        'ficus',
        'moss',
        'sage',
        'snapdragon',
        'columbine',
        'brugmansia',
        'palm',
        'pachypodium',
    ]
    if this_plant.dead == True:
        ascii_render('rip.txt')
    elif datetime.date.today().month == 10 and datetime.date.today().day == 31:
        ascii_render('jackolantern.txt')
    elif this_plant.stage == 0:
        ascii_render('seed.txt')
    elif this_plant.stage == 1:
        ascii_render('seedling.txt')
    elif this_plant.stage == 2:
        this_filename = plant_art_list[this_plant.species]+'1.txt'
        ascii_render(this_filename)
    elif this_plant.stage == 3 or this_plant.stage == 5:
        this_filename = plant_art_list[this_plant.species]+'2.txt'
        ascii_render(this_filename)
    elif this_plant.stage == 4:
        this_filename = plant_art_list[this_plant.species]+'3.txt'
        ascii_render(this_filename)

if __name__ == '__main__':
    my_data = DataManager()
    # if plant save file exists
    if my_data.check_plant():
        my_plant = my_data.load_plant()
    # otherwise create new plant
    else:
        my_plant = Plant(my_data.savefile_path)
        my_data.data_write_json(my_plant)
    draw_plant_ascii(my_plant)
