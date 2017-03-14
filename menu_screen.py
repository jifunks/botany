import curses, os, traceback, threading, time, datetime, pickle, operator, random

class CursedMenu(object):
    #TODO: create a side panel with log of events..?
    #TODO: name your plant
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
        self.gardenmenutoggle = False
        self.looktoggle = False
        self.maxy, self.maxx = self.screen.getmaxyx()
        # Highlighted and Normal line definitions
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        self.highlighted = curses.color_pair(1)
        self.normal = curses.A_NORMAL
        # Threaded screen update for live changes
        screen_thread = threading.Thread(target=self.update_plant_live, args=())
        screen_thread.daemon = True
        screen_thread.start()
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
            # if "start over" in self.options:
            #     self.options.remove("start over")
            if "start over" not in self.options:
                self.options.insert(-1,"start over")
        else:
            # TODO: remove after debug or bury in settings
            if self.plant.stage == 5:
                if "start over" not in self.options:
                    self.options.insert(-1,"start over")
            else:
                if "start over" in self.options:
                    self.options.remove("start over")

    def set_options(self, options):
        # Validates that the last option is "exit"
        if options[-1] is not 'exit':
            options.append('exit')
        self.options = options

    def draw(self):
        # Draw the menu and lines
        # TODO: this needs to either display the default menu screen or the
        # garden/leaderboard thing  based on self.gardenmenutoggle
        # TODO: display refresh is hacky. Could be more precise
        self.screen.refresh()
        self.screen.border(0)
        try:
            self.draw_default()
            self.screen.refresh()
        except Exception as exception:
            # Makes sure data is saved in event of a crash due to window resizing
            self.screen.addstr(0,0,"Enlarge terminal!")
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
            self.__exit__()
            traceback.print_exc()

    def draw_default(self):
        # Draws default menu
        clear_bar = " " * (int(self.maxx*2/3))
        self.screen.addstr(2,2, self.title, curses.A_STANDOUT) # Title for this menu
        self.screen.addstr(4,2, self.subtitle, curses.A_BOLD) #Subtitle for this menu
        # Clear menu on screen
        for index in range(len(self.options)+1):
            self.screen.addstr(5+index,4, clear_bar, curses.A_NORMAL)
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

    def update_plant_live(self):
        # Updates plant data on menu screen, live!
        # Will eventually use this to display ascii art...
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

    def format_garden_data(self,this_garden):

        plant_table = ""
        for plant_id in this_garden:
            if this_garden[plant_id]:
                if not this_garden[plant_id]["dead"]:
                    this_plant = this_garden[plant_id]
                    plant_table += this_plant["owner"] + " - "
                    plant_table += this_plant["age"] + " - "
                    plant_table += str(this_plant["score"]) + " points - "
                    plant_table += this_plant["description"] + "\n"
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
            plant_table_formatted = clear_bar
            for plant in this_garden:
                if not this_garden[plant]["dead"]:
                    plant_table_formatted += clear_bar
            self.gardenmenutoggle = not self.gardenmenutoggle

        for y, line in enumerate(plant_table_formatted.splitlines(), 2):
            self.screen.addstr(y+17, 2, line)
        self.screen.refresh()

    def get_plant_description(self, this_plant):
        1==1
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
            ],
                1:[
            "The seedling fills you with hope.",
            "You can make out a tiny leaf - or is that a thorn?",
            "You can feel the seedling looking back at you.",
            "You kiss your seedling good night.",
            "You think about all the seedlings who came before it.",
            "You and your seedling make a great team.",
            ],
                2:[
            "The " + this_species + " makes you feel relaxed.",
            "You sing a song to your " + this_species + ".",
            "You quietly sit with your " + this_species + " for a few minutes.",
            "Your " + this_species + " looks pretty good.",
            "You play loud techno to your " + this_species + ".",
            ],
                3:[
            "Your " + this_species + " is growing nicely!",
            "You're proud of the dedication it took to grow your " + this_species + ".",
            "The " + this_species + " looks good.",
            "You think how good this " + this_species + " would look on steroids.",
            "The buds of your " + this_species + " are about to bloom.",
            ],
                4:[
            "The " + this_color + " flowers look nice on your " + this_species +"!",
            "The " + this_color + " flowers have bloomed and fill you with desire.",
            "The " + this_color + " flowers of your " + this_species + " remind you of your childhood.",
            "The " + this_species + " has grown beautiful " + this_color + " flowers.",
            "The " + this_color + " petals remind you of your favorite shirt.",
            ],
                5:[
            "You fondly remember all of the time you spent caring for your " + this_species + ".",
            "Your " + this_species + " looks old and wise.",
            "Seed pods have grown on your " + this_species + ".",
            "The " + this_species + " fills you with love.",
            "The " + this_species + " reminds you of your first crush.",
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
        # if stage == 0 == seed
        if this_plant.dead:
            this_stage = 99

        this_stage_descriptions = stage_descriptions[this_stage]
        description_num = random.randint(0,len(this_stage_descriptions) - 1)
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

        # issue 1 - referencing anything past 4 on life stages breaks
        # issue 2 - 80% using plant ticks doesn't really work since it shifts
        # each time. need to use the difference between 2 stages, and then
        # plant ticks minus last stage

        if this_stage == 1:
            species_options = [this_plant.species_dict[this_plant.species],
                    this_plant.species_dict[(this_plant.species+3) % len(this_plant.species_dict)],
                    this_plant.species_dict[(this_plant.species-3) % len(this_plant.species_dict)]]
            random.shuffle(species_options)
            plant_hint = "It could be a(n) " + species_options[0] + ", " + species_options[1] + ", or " + species_options[2]
            output_text += plant_hint + ".\n"

        if this_stage == 2:
            # TODO: more descriptive rarity
            if this_plant.rarity >= 2:
                rarity_hint = "You feel like your plant is special."
                output_text += rarity_hint + ".\n"

        if this_stage == 3:
            color_options = [this_plant.color_dict[this_plant.color],
                    this_plant.color_dict[(this_plant.color+3) % len(this_plant.color_dict)],
                    this_plant.color_dict[(this_plant.color-3) % len(this_plant.color_dict)]]
            random.shuffle(color_options)
            plant_hint = "You can see the first hints of " + color_options[0] + ", " + color_options[1] + ", or " + color_options[2]
            output_text += plant_hint + ".\n"

        return output_text

    def draw_plant_description(self, this_plant):
        clear_bar = " " * (self.maxx-2) + "\n"
        control_keys = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]
        # load data
        # format data
        if not self.looktoggle:
            output_string = self.get_plant_description(this_plant)
            self.looktoggle = not self.looktoggle
        else:
            output_string = clear_bar
            output_string += clear_bar*3
            self.looktoggle = not self.looktoggle

        for y, line in enumerate(output_string.splitlines(), 2):
            self.screen.addstr(y+12, 2, line)
        self.screen.refresh()

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
        if request == "start over":
            self.plant.start_over()
        if request == "water":
            self.plant.water()
        if request == "look":
            # try:
            self.draw_plant_description(self.plant)
           #  except Exception as exception:
           #      self.screen.addstr(0,0,"Enlarge terminal!")
           #      self.__exit__()
           #      traceback.print_exc()
        if request == "instructions":
            try:
                self.draw_instructions()
            except Exception as exception:
                # Makes sure data is saved in event of a crash due to window resizing
                self.screen.addstr(0,0,"Enlarge terminal!")
                self.__exit__()
                traceback.print_exc()
        if request == "garden":
            try:
                self.draw_garden()
            except Exception as exception:
                self.screen.addstr(0,0,"Enlarge terminal!")
                self.__exit__()
                traceback.print_exc()

    def __exit__(self):
        self.exit = True
        curses.curs_set(2)
        curses.endwin()
        os.system('clear')

