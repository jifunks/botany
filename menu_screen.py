import curses, os, traceback, threading, time, datetime, pickle, operator, random

class CursedMenu(object):
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
        self.infotoggle = 0
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
        self.show(["water","look","garden","instructions"], title=' botany ', subtitle='options')

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
        # TODO: display refresh is hacky. Could be more precise
        self.screen.refresh()
        try:
            self.draw_default()
            self.screen.refresh()
        except Exception as exception:
            # Makes sure data is saved in event of a crash due to window resizing
            self.screen.clear()
            self.screen.addstr(0,0,"Enlarge terminal!")
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
            self.screen.addstr(0,0,"Enlarge terminal!")
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
            self.screen.addstr(ypos+y,xpos,line, curses.A_NORMAL)
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
        elif this_plant.stage >= 2:
            # this_filename = plant_art_dict[this_plant.species]+str(this_plant.stage)+'.txt'
            this_filename = plant_art_dict[this_plant.species]+'1.txt'
            self.ascii_render(this_filename, ypos, xpos)

    def draw_default(self):
        # draws default menu
        clear_bar = " " * (int(self.maxx*2/3))
        self.screen.addstr(2,2, self.title, curses.A_STANDOUT) # Title for this menu
        self.screen.addstr(4,2, self.subtitle, curses.A_BOLD) #Subtitle for this menu
        # clear menu on screen
        for index in range(len(self.options)+1):
            self.screen.addstr(5+index,4, clear_bar, curses.A_NORMAL)
        # display all the menu items, showing the 'pos' item highlighted
        for index in range(len(self.options)):
            textstyle = self.normal
            if index == self.selected:
                textstyle = self.highlighted
            self.screen.addstr(5+index,4, clear_bar, curses.A_NORMAL)
            self.screen.addstr(5+index,4, "%d - %s" % (index+1, self.options[index]), textstyle)

        self.screen.addstr(11,2, clear_bar, curses.A_NORMAL)
        self.screen.addstr(12,2, clear_bar, curses.A_NORMAL)
        self.screen.addstr(11,2, "plant: ", curses.A_DIM)
        self.screen.addstr(11,9, self.plant_string, curses.A_NORMAL)
        self.screen.addstr(12,2, "score: ", curses.A_DIM)
        self.screen.addstr(12,9, self.plant_ticks, curses.A_NORMAL)

        if not self.plant.dead:
            if int(time.time()) <= self.plant.watered_timestamp + 24*3600:
                self.screen.addstr(5,13, clear_bar, curses.A_NORMAL)
                self.screen.addstr(5,13, " - plant watered today :)", curses.A_NORMAL)
            else:
                self.screen.addstr(5,13, clear_bar, curses.A_NORMAL)
        else:
            self.screen.addstr(5,13, clear_bar, curses.A_NORMAL)
            self.screen.addstr(5,13, " - you can't water a dead plant :(", curses.A_NORMAL)

        # This draws cute ascii from files
        self.draw_plant_ascii(self.plant)
        # self.ascii_render("sun.txt",-2,self.maxx-14)

    def update_plant_live(self):
        # updates plant data on menu screen, live!
        # will eventually use this to display ascii art...
        while not self.exit:
            self.plant_string = self.plant.parse_plant()
            self.plant_ticks = str(self.plant.ticks)
            if self.initialized:
                self.update_options()
                self.draw()
            time.sleep(1)

    def get_user_input(self):
        # gets the user's input and acts appropriately
        try:
            user_in = self.screen.getch() # Gets user input
        except Exception as e:
            self.__exit__()
        # DEBUG KEYS
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
        down_keys = [curses.KEY_DOWN, 14, 106]
        up_keys = [curses.KEY_UP, 16, 107]
        if user_in in down_keys: # down arrow
            self.selected += 1
        if user_in in up_keys: # up arrow
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
                    plant_table += str(this_plant["score"]) + "p - "
                    plant_table += this_plant["description"] + "\n"
        return plant_table

    def draw_garden(self):
        # draws neighborhood
        clear_bar = " " * (self.maxx-2) + "\n"
        clear_block = clear_bar * 5
        control_keys = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]
        # load data
        with open(self.garden_file_path, 'rb') as f:
            this_garden = pickle.load(f)
        # format data
        if self.infotoggle != 2:
            for y, line in enumerate(clear_block.splitlines(), 2):
                self.screen.addstr(y+12, 2, line)
                self.screen.refresh()
            plant_table_formatted = self.format_garden_data(this_garden)
            self.infotoggle = 2
        else:
            plant_table_formatted = clear_bar
            for plant in this_garden:
                if not this_garden[plant]["dead"]:
                    plant_table_formatted += clear_bar
            self.infotoggle = 0

        for y, line in enumerate(plant_table_formatted.splitlines(), 2):
            self.screen.addstr(y+12, 2, line)
        self.screen.refresh()

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
            ],
                1:[
            "The seedling fills you with hope.",
            "The seedling shakes in the wind.",
            "You can make out a tiny leaf - or is that a thorn?",
            "You can feel the seedling looking back at you.",
            "You kiss your seedling good night.",
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
            ],
                3:[
            "Your " + this_species + " is growing nicely!",
            "You're proud of the dedication it took to grow your " + this_species + ".",
            "The " + this_species + " looks good.",
            "You think about how good this " + this_species + " will look.",
            "The buds of your " + this_species + " are about to bloom.",
            "You play your favorite song for your " + this_species + ".",
            ],
                4:[
            "The " + this_color + " flowers look nice on your " + this_species +"!",
            "The " + this_color + " flowers have bloomed and fill you with positivity.",
            "The " + this_color + " flowers of your " + this_species + " remind you of your childhood.",
            "The " + this_color + " flowers of your " + this_species + " smell amazing.",
            "The " + this_species + " has grown beautiful " + this_color + " flowers.",
            "The " + this_color + " petals remind you of that favorite shirt you lost.",
            "The " + this_color + " flowers remind you of your crush.",
            ],
                5:[
            "You fondly remember all of the time you spent caring for your " + this_species + ".",
            "Seed pods have grown on your " + this_species + ".",
            "The " + this_species + " fills you with love.",
            "Your " + this_species + " reminds you of your childhood backyard.",
            "The " + this_species + " reminds you of your family.",
            "The " + this_species + " reminds you of a forgotten memory.",
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
        # load data
        # format data
        if self.infotoggle != 1:
            # TODO: when garden grows this won't clear everything.
            # for example if there are 9 people in garden it won't clear all
            # of them
            output_string = clear_bar * (self.maxy - 15)
            for y, line in enumerate(output_string.splitlines(), 2):
                self.screen.addstr(y+12, 2, line)
            self.screen.refresh()
            output_string = self.get_plant_description(this_plant)
            self.infotoggle = 1
        else:
            output_string = clear_bar * 3
            self.infotoggle = 0

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
        '''this is where you do things with the request'''
        if request == None: return
        if request == "start over":
            self.plant.start_over()
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

