import curses
import math
import os
import traceback
import threading
import time
import random

class CursedMenu(object):
    #TODO: name your plant
    '''A class which abstracts the horrors of building a curses-based menu system'''
    def __init__(self, this_plant, this_data):
        '''Initialization'''
        self.initialized = False
        self.screen = curses.initscr()
        curses.noecho()
        curses.raw()
        curses.start_color()
        curses.curs_set(0)
        self.screen.keypad(1)
        self.plant = this_plant
        self.user_data = this_data
        self.plant_string = self.plant.parse_plant()
        self.plant_ticks = str(self.plant.ticks)
        self.exit = False
        self.infotoggle = 0
        self.maxy, self.maxx = self.screen.getmaxyx()
        # Highlighted and Normal line definitions
        self.define_colors()
        self.highlighted = curses.color_pair(1)
        self.normal = curses.A_NORMAL
        # Threaded screen update for live changes
        screen_thread = threading.Thread(target=self.update_plant_live, args=())
        screen_thread.daemon = True
        screen_thread.start()
        self.screen.clear()
        self.show(["water","look","garden","instructions"], title=' botany ', subtitle='options')

    def define_colors(self):
        # set curses color pairs manually
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_CYAN, curses.COLOR_BLACK)

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
            if "harvest" not in self.options:
                self.options.insert(-1,"harvest")
        else:
            if self.plant.stage == 5:
                if "harvest" not in self.options:
                    self.options.insert(-1,"harvest")
            else:
                if "harvest" in self.options:
                    self.options.remove("harvest")

    def set_options(self, options):
        # Validates that the last option is "exit"
        if options[-1] is not 'exit':
            options.append('exit')
        self.options = options

    def draw(self):
        # Draw the menu and lines
        self.screen.refresh()
        try:
            self.draw_default()
            self.screen.refresh()
        except Exception as exception:
            # Makes sure data is saved in event of a crash due to window resizing
            self.screen.clear()
            self.screen.addstr(0, 0, "Enlarge terminal!", curses.A_NORMAL)
            self.screen.refresh()
            self.__exit__()
            traceback.print_exc()

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
            self.screen.clear()
            self.screen.addstr(0, 0, "Enlarge terminal!", curses.A_NORMAL)
            self.screen.refresh()
            self.__exit__()
            #traceback.print_exc()

    def ascii_render(self, filename, ypos, xpos):
        # Prints ASCII art from file at given coordinates
        this_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"art")
        this_filename = os.path.join(this_dir,filename)
        this_file = open(this_filename,"r")
        this_string = this_file.readlines()
        this_file.close()
        for y, line in enumerate(this_string, 2):
            self.screen.addstr(ypos+y, xpos, line, curses.A_NORMAL)
        # self.screen.refresh()

    def draw_plant_ascii(self, this_plant):
        ypos = 1
        xpos = int((self.maxx-37)/2 + 25)
        plant_art_dict = {
            0: 'poppy',
            1: 'cactus',
            2: 'aloe',
            3: 'flytrap',
            4: 'jadeplant',
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

        if this_plant.stage == 0:
            self.ascii_render('seed.txt', ypos, xpos)
        elif this_plant.stage == 1:
            self.ascii_render('seedling.txt', ypos, xpos)
        elif this_plant.stage == 2:
            this_filename = plant_art_dict[this_plant.species]+'1.txt'
            self.ascii_render(this_filename, ypos, xpos)
        elif this_plant.stage == 3 or this_plant.stage == 5:
            this_filename = plant_art_dict[this_plant.species]+'2.txt'
            self.ascii_render(this_filename, ypos, xpos)
        elif this_plant.stage == 4:
            this_filename = plant_art_dict[this_plant.species]+'3.txt'
            self.ascii_render(this_filename, ypos, xpos)

    def draw_default(self):
        # draws default menu
        clear_bar = " " * (int(self.maxx*2/3))
        self.screen.addstr(2, 2, self.title, curses.A_STANDOUT) # Title for this menu
        self.screen.addstr(4, 2, self.subtitle, curses.A_BOLD) #Subtitle for this menu
        # clear menu on screen
        for index in range(len(self.options)+1):
            self.screen.addstr(5+index, 4, clear_bar, curses.A_NORMAL)
        # display all the menu items, showing the 'pos' item highlighted
        for index in range(len(self.options)):
            textstyle = self.normal
            if index == self.selected:
                textstyle = self.highlighted
            self.screen.addstr(5+index ,4, clear_bar, curses.A_NORMAL)
            self.screen.addstr(5+index ,4, "%d - %s" % (index+1, self.options[index]), textstyle)

        self.screen.addstr(11, 2, clear_bar, curses.A_NORMAL)
        self.screen.addstr(12, 2, clear_bar, curses.A_NORMAL)
        self.screen.addstr(11, 2, "plant: ", curses.A_DIM)
        self.screen.addstr(11, 9, self.plant_string, curses.A_NORMAL)
        self.screen.addstr(12, 2, "score: ", curses.A_DIM)
        self.screen.addstr(12, 9, self.plant_ticks, curses.A_NORMAL)

        # display fancy water gauge
        if not self.plant.dead:
            water_gauge_str = self.water_gauge()
            self.screen.addstr(5,14, water_gauge_str, curses.A_NORMAL)
        else:
            self.screen.addstr(5,13, clear_bar, curses.A_NORMAL)
            self.screen.addstr(5,13, " (   RIP   )", curses.A_NORMAL)

        # draw cute ascii from files
        self.draw_plant_ascii(self.plant)

    def water_gauge(self):
        # build nice looking water gauge
        water_left_pct = 1 - ((time.time() - self.plant.watered_timestamp)/86400)
        # don't allow negative value
        water_left_pct = max(0, water_left_pct)
        water_left = int(math.ceil(water_left_pct * 10))
        water_string = "(" + (")" * water_left) + ("." * (10 - water_left)) + ") " + str(int(water_left_pct * 100)) + "% "
        return water_string


    def update_plant_live(self):
        # updates plant data on menu screen, live!
        while not self.exit:
            self.plant_string = self.plant.parse_plant()
            self.plant_ticks = str(self.plant.ticks)
            if self.initialized:
                self.update_options()
                self.draw()
            time.sleep(1)

    def get_user_input(self):
        # gets the user's input
        try:
            user_in = self.screen.getch() # Gets user input
        except Exception as e:
            self.__exit__()
        ## DEBUG KEYS - enable these lines to see curses key codes
        # self.screen.addstr(1, 1, str(user_in), curses.A_NORMAL)
        # self.screen.refresh()

        # Resize sends curses.KEY_RESIZE, update display
        if user_in == curses.KEY_RESIZE:
            self.maxy,self.maxx = self.screen.getmaxyx()
            self.screen.clear()
            self.screen.refresh()

        # enter and exit Keys are special cases
        if user_in == 10:
            return self.options[self.selected]
        if user_in == 27:
            return self.options[-1]

        # this is a number; check to see if we can set it
        if user_in >= ord('1') and user_in <= ord(str(min(9,len(self.options)+1))):
            self.selected = user_in - ord('0') - 1 # convert keypress back to a number, then subtract 1 to get index
            return

        # increment or Decrement
        down_keys = [curses.KEY_DOWN, 14, ord('j')]
        up_keys = [curses.KEY_UP, 16, ord('k')]

        if user_in in down_keys: # down arrow
            self.selected += 1
        if user_in in up_keys: # up arrow
            self.selected -=1

        # modulo to wrap menu cursor
        self.selected = self.selected % len(self.options)
        return

    def format_garden_data(self,this_garden):
        # Returns list of lists (pages) of garden entries
        plant_table = ""
        for plant_id in this_garden:
            if this_garden[plant_id]:
                if not this_garden[plant_id]["dead"]:
                    this_plant = this_garden[plant_id]
                    entry = "{:14} - {:>16} - {:>7}p - {}\n".format(
                        this_plant["owner"],
                        this_plant["age"],
                        this_plant["score"],
                        this_plant["description"]
                    )
                    plant_table += entry
        # build list of n entries per page
        entries_per_page = self.maxy - 16
        garden_list = plant_table.splitlines()
        paginated_list = [garden_list[i:i+entries_per_page] for i in range(0,len(garden_list),entries_per_page)]
        return paginated_list

    def draw_garden(self):
        # draws community garden
        # load data from sqlite db
        this_garden = self.user_data.retrieve_garden_from_db()
        # format data
        self.clear_info_pane()
        plant_table_pages = []
        if self.infotoggle != 2:
            # if infotoggle isn't 2, the screen currently displays other stuff
            plant_table_pages = self.format_garden_data(this_garden)
            self.infotoggle = 2
        else:
            # the screen IS currently showing the garden (1 page), make the
            # text a bunch of blanks to clear it out
            self.infotoggle = 0

        # print garden information OR clear it
        for page_num, page in enumerate(plant_table_pages, 1):
            # Print page text
            self.draw_info_text(page)
            if len(plant_table_pages) > 1:
                # Multiple pages, paginate and require keypress
                page_text = "(%d/%d) --- press any key ---" % (page_num, len(plant_table_pages))
                self.screen.addstr(self.maxy-2, 2, page_text)
                self.screen.getch()
                self.screen.refresh()
                # Clear page before drawing next
                self.clear_info_pane()
                self.infotoggle = 0

    def get_plant_description(self, this_plant):
        output_text = ""
        this_species = this_plant.species_dict[this_plant.species]
        this_color = this_plant.color_dict[this_plant.color]
        this_stage = this_plant.stage

        stage_descriptions = {
                0:[
            "You're excited about your new seed.",
            "You wonder what kind of plant your seed will grow into.",
            "You're ready for a new start with this plant.",
            "You're tired of waiting for your seed to grow.",
            "You wish your seed could tell you what it needs.",
            "You can feel the spirit inside your seed.",
            "These pretzels are making you thirsty.",
            "Way to plant, Ann!",
            "'To see things in the seed, that is genius' - Lao Tzu",
            ],
                1:[
            "The seedling fills you with hope.",
            "The seedling shakes in the wind.",
            "You can make out a tiny leaf - or is that a thorn?",
            "You can feel the seedling looking back at you.",
            "You blow a kiss to your seedling.",
            "You think about all the seedlings who came before it.",
            "You and your seedling make a great team.",
            "Your seedling grows slowly and quietly.",
            "You meditate on the paths your plant's life could take.",
            ],
                2:[
            "The " + this_species + " makes you feel relaxed.",
            "You sing a song to your " + this_species + ".",
            "You quietly sit with your " + this_species + " for a few minutes.",
            "Your " + this_species + " looks pretty good.",
            "You play loud techno to your " + this_species + ".",
            "You play piano to your " + this_species + ".",
            "You play rap music to your " + this_species + ".",
            "You whistle a tune to your " + this_species + ".",
            "You read a poem to your " + this_species + ".",
            "You tell a secret to your " + this_species + ".",
            "You play your favorite record for your " + this_species + ".",
            ],
                3:[
            "Your " + this_species + " is growing nicely!",
            "You're proud of the dedication it took to grow your " + this_species + ".",
            "You take a deep breath with your " + this_species + ".",
            "You think of all the words that rhyme with " + this_species + ".",
            "The " + this_species + " looks full of life.",
            "The " + this_species + " inspires you.",
            "Your " + this_species + " makes you forget about your problems.",
            "Your " + this_species + " gives you a reason to keep going.",
            "Looking at your " + this_species + " helps you focus on what matters.",
            "You think about how nice this " + this_species + " looks here.",
            "The buds of your " + this_species + " might bloom soon.",
            ],
                4:[
            "The " + this_color + " flowers look nice on your " + this_species +"!",
            "The " + this_color + " flowers have bloomed and fill you with positivity.",
            "The " + this_color + " flowers remind you of your childhood.",
            "The " + this_color + " flowers remind you of spring mornings.",
            "The " + this_color + " flowers remind you of a forgotten memory.",
            "The " + this_color + " flowers remind you of your happy place.",
            "The aroma of the " + this_color + " flowers energize you.",
            "The " + this_species + " has grown beautiful " + this_color + " flowers.",
            "The " + this_color + " petals remind you of that favorite shirt you lost.",
            "The " + this_color + " flowers remind you of your crush.",
            "You smell the " + this_color + " flowers and are filled with peace.",
            ],
                5:[
            "You fondly remember the time you spent caring for your " + this_species + ".",
            "Seed pods have grown on your " + this_species + ".",
            "You feel like your " + this_species + " appreciates your care.",
            "The " + this_species + " fills you with love.",
            "You're ready for whatever comes after your " + this_species + ".",
            "You're excited to start growing your next plant.",
            "You reflect on when your " + this_species + " was just a seedling.",
            "You grow nostalgic about the early days with your " + this_species + ".",
            ],
                99:[
            "You wish you had taken better care of your plant.",
            "If only you had watered your plant more often..",
            "Your plant is dead, there's always next time.",
            "You cry over the withered leaves of your plant.",
            "Your plant died. Maybe you need a fresh start.",
            ],
        }
        # self.life_stages is tuple containing length of each stage
        # (seed, seedling, young, mature, flowering)
        if this_plant.dead:
            this_stage = 99

        this_stage_descriptions = stage_descriptions[this_stage]
        description_num = random.randint(0,len(this_stage_descriptions) - 1)
        # If not fully grown
        if this_stage <= 4:
            # Growth hint
            if this_stage >= 1:
                last_growth_at = this_plant.life_stages[this_stage - 1]
            else:
                last_growth_at = 0
            ticks_since_last = this_plant.ticks - last_growth_at
            ticks_between_stage = this_plant.life_stages[this_stage] - last_growth_at
            if ticks_since_last >= ticks_between_stage * 0.8:
                output_text += "You notice your plant looks different.\n"

        output_text += this_stage_descriptions[description_num] + "\n"

        # if seedling
        if this_stage == 1:
            species_options = [this_plant.species_dict[this_plant.species],
                    this_plant.species_dict[(this_plant.species+3) % len(this_plant.species_dict)],
                    this_plant.species_dict[(this_plant.species-3) % len(this_plant.species_dict)]]
            random.shuffle(species_options)
            plant_hint = "It could be a(n) " + species_options[0] + ", " + species_options[1] + ", or " + species_options[2]
            output_text += plant_hint + ".\n"

        # if young plant
        if this_stage == 2:
            if this_plant.rarity >= 2:
                rarity_hint = "You feel like your plant is special."
                output_text += rarity_hint + ".\n"

        # if mature plant
        if this_stage == 3:
            color_options = [this_plant.color_dict[this_plant.color],
                    this_plant.color_dict[(this_plant.color+3) % len(this_plant.color_dict)],
                    this_plant.color_dict[(this_plant.color-3) % len(this_plant.color_dict)]]
            random.shuffle(color_options)
            plant_hint = "You can see the first hints of " + color_options[0] + ", " + color_options[1] + ", or " + color_options[2]
            output_text += plant_hint + ".\n"

        return output_text

    def draw_plant_description(self, this_plant):
        # If menu is currently showing something other than the description
        self.clear_info_pane()
        if self.infotoggle != 1:
            # get plant description before printing
            output_string = self.get_plant_description(this_plant)
            growth_multiplier = 1 + (0.2 * (this_plant.generation-1))
            output_string += "Generation: {}\nGrowth rate: {}".format(self.plant.generation, growth_multiplier)
            self.draw_info_text(output_string)
            self.infotoggle = 1
        else:
            # otherwise just set toggle
            self.infotoggle = 0

    def draw_instructions(self):
        # Draw instructions on screen
        self.clear_info_pane()
        if self.infotoggle != 4:
            instructions_txt = ("welcome to botany. you've been given a seed\n"
                                "that will grow into a beautiful plant. check\n"
                                "in and water your plant every 24h to keep it\n"
                                "growing. 5 days without water = death. your\n"
                                "plant depends on you to live! more info is\n"
                                "available in the readme :)\n"
                                "                               cheers,\n"
                                "                               curio\n"
                                )
            self.draw_info_text(instructions_txt)
            self.infotoggle = 4
        else:
            self.infotoggle = 0

    def clear_info_pane(self):
        # Clears bottom part of screen
        clear_bar = " " * (self.maxx-2) + "\n"
        clear_block = clear_bar * (self.maxy - 15)
        for y, line in enumerate(clear_block.splitlines(), 2):
            self.screen.addstr(y+12, 2, line, curses.A_NORMAL)
        self.screen.refresh()

    def draw_info_text(self, info_text):
        # print lines of text to info pane at bottom of screen
        if type(info_text) is str:
            info_text = info_text.splitlines()

        for y, line in enumerate(info_text, 2):
            self.screen.addstr(y+12, 2, line, curses.A_NORMAL)
        self.screen.refresh()

    def harvest_confirmation(self):
        self.clear_info_pane()
        # get plant description before printing
        max_stage = len(self.plant.stage_dict) - 1
        harvest_text = ""
        if not self.plant.dead:
            if self.plant.stage == max_stage:
                harvest_text += "Congratulations! You raised your plant to its final stage of growth.\n"
                harvest_text += "Your next plant will grow at a speed of: {}x\n".format(1 + (0.2 * self.plant.generation))
        harvest_text += "If you harvest your plant you'll start over from a seed.\nContinue? (Y/n)"
        self.draw_info_text(harvest_text)
        try:
            user_in = self.screen.getch() # Gets user input
        except Exception as e:
            self.__exit__()

        if user_in == ord('Y'):
            self.plant.start_over()
        else:
            pass
        self.clear_info_pane()

    def handle_request(self, request):
        # Menu options call functions here
        if request == None: return
        if request == "harvest":
            self.harvest_confirmation()
        if request == "water":
            self.plant.water()
        if request == "look":
            try:
                self.draw_plant_description(self.plant)
            except Exception as exception:
                self.screen.refresh()
                # traceback.print_exc()
        if request == "instructions":
            try:
                self.draw_instructions()
            except Exception as exception:
                self.screen.refresh()
                # traceback.print_exc()
        if request == "garden":
            try:
                self.draw_garden()
            except Exception as exception:
                self.screen.refresh()
                # traceback.print_exc()

    def __exit__(self):
        self.exit = True
        curses.curs_set(2)
        curses.endwin()
        os.system('clear')

