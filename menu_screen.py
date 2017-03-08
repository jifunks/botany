import curses, os, traceback, threading, time, datetime

class CursedMenu(object):
    #TODO: create a side panel with log of events..?
    # TODO: display that updates on either keypress OR tick
    '''A class which abstracts the horrors of building a curses-based menu system'''
    def __init__(self, this_plant):
        '''Initialization'''
        self.initialized = False
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.start_color()
        curses.curs_set(0)
        self.screen.keypad(1)
        self.plant = this_plant
        self.plant_string = self.plant.parse_plant()
        self.plant_ticks = str(self.plant.ticks)
        self.exit = False
        self.instructiontoggle = False
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

    def show(self, options, title="Title", subtitle="Subtitle"):
        '''Draws a menu with the given parameters'''
        self.set_options(options)
        self.title = title
        self.subtitle = subtitle
        self.selected = 0
        self.initialized = True
        self.draw_menu()

    def set_options(self, options):
        '''Validates that the last option is "Exit"'''
        if options[-1] is not 'Exit':
            options.append('Exit')
        self.options = options


    def draw_menu(self):
        '''Actually draws the menu and handles branching'''
        request = ""
        try:
            while request is not "Exit":
                self.draw()
                request = self.get_user_input()
                self.handle_request(request)
            self.__exit__()

        # Also calls __exit__, but adds traceback after
        except Exception as exception:
            self.__exit__()
            traceback.print_exc()

    def draw(self):
        '''Draw the menu and lines'''
        self.screen.refresh()
        self.screen.border(0)
        self.screen.addstr(2,2, self.title, curses.A_STANDOUT) # Title for this menu
        self.screen.addstr(4,2, self.subtitle, curses.A_BOLD) #Subtitle for this menu
        # Display all the menu items, showing the 'pos' item highlighted
        for index in range(len(self.options)):
            textstyle = self.normal
            if index == self.selected:
                textstyle = self.highlighted
            self.screen.addstr(5+index,4, "%d - %s" % (index+1, self.options[index]), textstyle)

        self.screen.addstr(11,2, self.plant_string, curses.A_NORMAL)
        self.screen.addstr(12,2, self.plant_ticks, curses.A_NORMAL)

        if not self.plant.dead:
            if int(time.time()) <= self.plant.watered_timestamp + 24*3600:
                self.screen.addstr(6,13, " - plant watered today :)", curses.A_NORMAL)
            else:
                self.screen.addstr(6,13, "                         ", curses.A_NORMAL)
        else:
            self.screen.addstr(6,13, " - you can't water a dead plant :(", curses.A_NORMAL)
        try:
            self.screen.refresh()
        except Exception as exception:
            # Makes sure data is saved in event of a crash due to window resizing
            self.__exit__()
            traceback.print_exc()

    def update_plant_live(self):
        # Updates plant data on menu screen, live!
        # Will eventually use this to display ascii art...
        while not self.exit:
            self.plant_string = self.plant.parse_plant()
            self.plant_ticks = str(self.plant.ticks)
            if self.initialized:
                self.draw()
            time.sleep(1)

    def get_user_input(self):
        '''Gets the user's input and acts appropriately'''
        user_in = self.screen.getch() # Gets user input

        '''Enter and Exit Keys are special cases'''
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


    def handle_request(self, request):
        '''This is where you do things with the request'''
        if request is None: return
        if request == "water":
            self.plant.water()
        if request == "instructions":
            if not self.instructiontoggle:
                instructions_txt = """welcome to botany. you've been given a seed
that will grow into a beautiful plant. check
in and water your plant every day to keep it
alive. it depends on you to live! More info
is available in the readme :)
                                   cheers,
                                   curio"""
                self.instructiontoggle = not self.instructiontoggle
            else:
                instructions_txt = """                                           
                                            
                                            
                                            
                                            
                                            
                                            """
                # TODO: 
                self.instructiontoggle = not self.instructiontoggle
                # self.screen.clear()
            for y, line in enumerate(instructions_txt.splitlines(), 2):
                self.screen.addstr(y,self.maxx-50, line)
            #self.screen.addstr(8,15,str(self.plant.ticks), curses.A_STANDOUT) # Title for this menu
            self.screen.refresh()


    def __exit__(self):
        self.exit = True
        curses.curs_set(2)
        curses.endwin()
        os.system('clear')


'''demo'''
# cm = CursedMenu()
# cm.show([1,"water",3], title=' botany ', subtitle='Options')

