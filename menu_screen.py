import curses, os, traceback, threading, time, datetime, pickle

class CursedMenu(object):
    #TODO: create a side panel with log of events..?
    '''A class which abstracts the horrors of building a curses-based menu system'''
    def __init__(self, this_plant, this_garden_file_path):
        '''Initialization'''
        self.initialized = False
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.curs_set(0)
        self.screen.keypad(1)
        self.plant = this_plant
        self.garden_file_path = this_garden_file_path
        self.plant_string = self.plant.parse_plant()
        self.plant_ticks = str(self.plant.ticks)
        self.exit = False
        self.instructiontoggle = False
        #TODO: debugging
        # self.gardenmenutoggle = True
        self.gardenmenutoggle = False
        self.maxy, self.maxx = self.screen.getmaxyx()
        # Highlighted and Normal line definitions
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.highlighted = curses.color_pair(1)
        self.normal = curses.A_NORMAL
        screen_thread = threading.Thread(target=self.update_plant_live, args=())
        screen_thread.daemon = True
        screen_thread.start()
        # TODO: tweaking this to try to get rid of garble bug
        self.screen.clear()

    def show(self, options, title, subtitle):
        # Draws a menu with parameters
        self.set_options(options)
        self.update_options()
        self.title = title
        self.subtitle = subtitle
        self.selected = 0
        self.initialized = True
        self.draw_menu()

    def update_options(self):
        # Makes sure you can get a new plant if it dies
        if self.plant.dead:
            if "kill" in self.options:
                self.options.remove("kill")
            if "new" not in self.options:
                self.options.insert(-1,"new")
        else:
            # TODO: remove after debug or bury in settings
            if "new" in self.options:
                self.options.remove("new")
            if "kill" not in self.options:
                self.options.insert(-1,"kill")

    def set_options(self, options):
        # Validates that the last option is "exit"
        if options[-1] is not 'exit':
            options.append('exit')
        self.options = options

    def draw_menu(self):
        # Actually draws the menu and handles branching
        request = ""
        try:
            while request is not "exit":
                self.draw()
                request = self.get_user_input()
                self.handle_request(request)
            self.__exit__()

        # Also calls __exit__, but adds traceback after
        except Exception as exception:
            self.__exit__()
            traceback.print_exc()

    def draw_default(self):
        # Draws default menu
        clear_bar = " " * (int(self.maxx*2/3))
        self.screen.addstr(2,2, self.title, curses.A_STANDOUT) # Title for this menu
        self.screen.addstr(4,2, self.subtitle, curses.A_BOLD) #Subtitle for this menu
        # Display all the menu items, showing the 'pos' item highlighted
        for index in range(len(self.options)):
            textstyle = self.normal
            if index == self.selected:
                textstyle = self.highlighted
            self.screen.addstr(5+index,4, clear_bar, curses.A_NORMAL)
            self.screen.addstr(5+index,4, "%d - %s" % (index+1, self.options[index]), textstyle)

        self.screen.addstr(11,2, clear_bar, curses.A_NORMAL)
        self.screen.addstr(12,2, clear_bar, curses.A_NORMAL)
        self.screen.addstr(11,2, self.plant_string, curses.A_NORMAL)
        self.screen.addstr(12,2, self.plant_ticks, curses.A_NORMAL)

        if not self.plant.dead:
            if int(time.time()) <= self.plant.watered_timestamp + 24*3600:
                self.screen.addstr(5,13, clear_bar, curses.A_NORMAL)
                self.screen.addstr(5,13, " - plant watered today :)", curses.A_NORMAL)
            else:
                self.screen.addstr(5,13, clear_bar, curses.A_NORMAL)
        else:
            self.screen.addstr(5,13, clear_bar, curses.A_NORMAL)
            self.screen.addstr(5,13, " - you can't water a dead plant :(", curses.A_NORMAL)

    def format_garden_data(self,this_garden):
        plant_table = ""
        # TODO: include only live plants maybe
        for plant_id in this_garden:
            if this_garden[plant_id]:
                if not this_garden[plant_id]["dead"]:
                    this_plant = this_garden[plant_id]
                    plant_table += this_plant["owner"] + " - "
                    plant_table += this_plant["age"] + " - "
                    plant_table += this_plant["description"] + " - "
                    plant_table += str(this_plant["score"]) + "\n"
        return plant_table

    def draw_garden(self):
        # Draws neighborhood
        clear_bar = " " * (self.maxx-2) + "\n"
        control_keys = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]
        # load data
        with open(self.garden_file_path, 'rb') as f:
            this_garden = pickle.load(f)
        # format data
        if not self.gardenmenutoggle:
            plant_table_formatted = self.format_garden_data(this_garden)
            self.gardenmenutoggle = not self.gardenmenutoggle
        else:
            plant_table_formatted = ""
            for line in this_garden:
                plant_table_formatted += clear_bar
            self.gardenmenutoggle = not self.gardenmenutoggle

        for y, line in enumerate(plant_table_formatted.splitlines(), 2):
            self.screen.addstr(y+12, 2, line)
        # TODO: this needs to be updated so that it only draws if the window
        # is big enough.. or try catch it
        self.screen.refresh()

    def draw(self):
        # Draw the menu and lines
        # TODO: this needs to either display the default menu screen or the
        # garden/leaderboard thing  based on self.gardenmenutoggle
        # TODO: display refresh is hacky. Could be more precise
        self.screen.refresh()
        self.screen.border(0)
        # if self.gardenmenutoggle:
        #     self.draw_garden()
        # else:
        #     self.draw_default()
        self.draw_default()
        try:
            self.screen.refresh()
        except Exception as exception:
            # Makes sure data is saved in event of a crash due to window resizing
            self.__exit__()
            traceback.print_exc()

    def update_plant_live(self):
        # Updates plant data on menu screen, live!
        # Will eventually use this to display ascii art...
        # self.set_options(self.options)
        while not self.exit:
            self.plant_string = self.plant.parse_plant()
            self.plant_ticks = str(self.plant.ticks)
            if self.initialized:
                self.update_options()
                self.draw()
            time.sleep(1)

    def get_user_input(self):
        # Gets the user's input and acts appropriately
        user_in = self.screen.getch() # Gets user input

        # Enter and exit Keys are special cases
        if user_in == 10:
            return self.options[self.selected]
        if user_in == 27:
            return self.options[-1]

        # This is a number; check to see if we can set it
        if user_in >= ord('1') and user_in <= ord(str(min(9,len(self.options)+1))):
            self.selected = user_in - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
            return

        # Increment or Decrement
        if user_in == curses.KEY_DOWN: # down arrow
            self.selected += 1
        if user_in == curses.KEY_UP: # up arrow
            self.selected -=1
        self.selected = self.selected % len(self.options)
        return

    def draw_instructions(self):
        if not self.instructiontoggle:
            instructions_txt = """welcome to botany. you've been given a seed
that will grow into a beautiful plant. check
in and water your plant every 24h to keep it
growing. 5 days without water = death. your
plant depends on you to live! more info is
available in the readme :)
                               cheers,
                               curio"""
            self.instructiontoggle = not self.instructiontoggle
        else:
            instructions_txt = """                                           
                                            
                                            
                                            
                                            
                                            
                                            
                                        """
            self.instructiontoggle = not self.instructiontoggle
        for y, line in enumerate(instructions_txt.splitlines(), 2):
            self.screen.addstr(self.maxy-12+y,self.maxx-47, line)
        self.screen.refresh()
    def handle_request(self, request):
        '''This is where you do things with the request'''
        if request == None: return
        if request == "kill":
            self.plant.kill_plant()
        if request == "new":
            self.plant.new_seed(self.plant.file_name)
        if request == "water":
            self.plant.water()
        if request == "instructions":
            self.draw_instructions()
        if request == "garden":
            self.draw_garden()
    def __exit__(self):
        self.exit = True
        curses.curs_set(2)
        curses.endwin()
        os.system('clear')

