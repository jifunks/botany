
from botany import menu_screen as ms
from botany.plant import Plant
from botany.data_manager import DataManager

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



def main():
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

    ms.main(my_plant, my_data)
    my_data.save_plant(my_plant)
    my_data.data_write_json(my_plant)
    my_data.update_garden_db(my_plant)

if __name__ == '__main__':
    main()    
