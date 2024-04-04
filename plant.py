import random
import os
import json
import threading
import time
import uuid
import getpass

class Plant:
    # This is your plant!
    stage_list = [
        'seed',
        'seedling',
        'young',
        'mature',
        'flowering',
        'seed-bearing',
    ]

    color_list = [
        'red',
        'orange',
        'yellow',
        'green',
        'blue',
        'indigo',
        'violet',
        'white',
        'black',
        'gold',
        'rainbow',
    ]

    rarity_list = [
        'common',
        'uncommon',
        'rare',
        'legendary',
        'godly',
    ]

    species_list = [
        'poppy',
        'cactus',
        'aloe',
        'venus flytrap',
        'jade plant',
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

    mutation_list = [
        '',
        'humming',
        'noxious',
        'vorpal',
        'glowing',
        'electric',
        'icy',
        'flaming',
        'psychic',
        'screaming',
        'chaotic',
        'hissing',
        'gelatinous',
        'deformed',
        'shaggy',
        'scaly',
        'depressed',
        'anxious',
        'metallic',
        'glossy',
        'psychedelic',
        'bonsai',
        'foamy',
        'singing',
        'fractal',
        'crunchy',
        'goth',
        'oozing',
        'stinky',
        'aromatic',
        'juicy',
        'smug',
        'vibrating',
        'lithe',
        'chalky',
        'naive',
        'ersatz',
        'disco',
        'levitating',
        'colossal',
        'luminous',
        'cosmic',
        'ethereal',
        'cursed',
        'buff',
        'narcotic',
        'gnu/linux',
        'abraxan', # rip dear friend
    ]


    def __init__(self, this_filename, generation=1):
        # Constructor
        self.plant_id = str(uuid.uuid4())
        self.life_stages = (3600*24, (3600*24)*3, (3600*24)*10, (3600*24)*20, (3600*24)*30)
        # self.life_stages = (2, 4, 6, 8, 10) # debug mode
        self.stage = 0
        self.mutation = 0
        self.species = random.randint(0,len(self.species_list)-1)
        self.color = random.randint(0,len(self.color_list)-1)
        self.rarity = self.rarity_check()
        self.ticks = 0
        self.age_formatted = "0"
        self.generation = generation
        self.dead = False
        self.write_lock = False
        self.owner = getpass.getuser()
        self.file_name = this_filename
        self.start_time = int(time.time())
        self.last_time = int(time.time())
        # must water plant first day
        self.watered_timestamp = int(time.time())-(24*3600)-1
        self.watered_24h = False
        self.visitors = []

    def migrate_properties(self):
        # Migrates old data files to new
        if not hasattr(self, 'generation'):
            self.generation = 1
        if not hasattr(self, 'visitors'):
            self.visitors = []

    def parse_plant(self):
        # Converts plant data to human-readable format
        output = ""
        if self.stage >= 3:
            output += self.rarity_list[self.rarity] + " "
        if self.mutation != 0:
            output += self.mutation_list[self.mutation] + " "
        if self.stage >= 4:
            output += self.color_list[self.color] + " "
        output += self.stage_list[self.stage] + " "
        if self.stage >= 2:
            output += self.species_list[self.species] + " "
        return output.strip()

    def rarity_check(self):
        # Generate plant rarity
        CONST_RARITY_MAX = 256.0
        rare_seed = random.randint(1,int(CONST_RARITY_MAX))
        common_range =    round((2.0/3)*CONST_RARITY_MAX)
        uncommon_range =  round((2.0/3)*(CONST_RARITY_MAX-common_range))
        rare_range =      round((2.0/3)*(CONST_RARITY_MAX-common_range-uncommon_range))
        legendary_range = round((2.0/3)*(CONST_RARITY_MAX-common_range-uncommon_range-rare_range))

        common_max = common_range
        uncommon_max = common_max + uncommon_range
        rare_max = uncommon_max + rare_range
        legendary_max = rare_max + legendary_range
        godly_max = CONST_RARITY_MAX

        if 0 <= rare_seed <= common_max:
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

    def dead_check(self):
        if self.dead:
            return True
        # if it has been >5 days since watering, sorry plant is dead :(
        time_delta_watered = int(time.time()) - self.watered_timestamp
        if time_delta_watered > (5 * (24 * 3600)):
            self.dead = True
        return self.dead

    def update_visitor_db(self, visitor_names):
        game_dir = os.path.dirname(os.path.realpath(__file__))
        garden_db_path = os.path.join(game_dir, 'sqlite/garden_db.sqlite')
        conn = sqlite3.connect(garden_db_path)
        for name in (visitor_names):
            c = conn.cursor()
            c.execute("SELECT * FROM visitors WHERE garden_name = '{}' AND visitor_name = '{}' ".format(self.owner, name))
            data=c.fetchone()
            if data is None:
                sql = """ INSERT INTO visitors (garden_name,visitor_name,weekly_visits) VALUES('{}', '{}',1)""".format(self.owner, name)
                c.execute(sql)
            else:
                sql = """ UPDATE visitors SET weekly_visits = weekly_visits + 1 WHERE garden_name = '{}' AND visitor_name = '{}'""".format(self.owner, name)
                c.execute(sql)
        conn.commit()
        conn.close()

    def guest_check(self):
        user_dir = os.path.expanduser("~")
        botany_dir = os.path.join(user_dir,'.botany')
        visitor_filepath = os.path.join(botany_dir,'visitors.json')
        guest_timestamps = []
        visitors_this_check = []
        if os.path.isfile(visitor_filepath):
            with open(visitor_filepath, 'r') as visitor_file:
                data = json.load(visitor_file)
                if data:
                    for element in data:
                        if element['user'] not in self.visitors:
                            self.visitors.append(element['user'])
                        if element['user'] not in visitors_this_check:
                            visitors_this_check.append(element['user'])
                        # prevent users from manually setting watered_time in the future
                        if element['timestamp'] <= int(time.time()) and element['timestamp'] >= self.watered_timestamp:
                            guest_timestamps.append(element['timestamp'])
                    try:
                       self.update_visitor_db(visitors_this_check)
                    except:
                        pass
                    with open(visitor_filepath, 'w') as visitor_file:
                        visitor_file.write('[]')
        else:
            with open(visitor_filepath, mode='w') as f:
                json.dump([], f)
            os.chmod(visitor_filepath, 0o666)
        if not guest_timestamps:
            return self.watered_timestamp
        all_timestamps = [self.watered_timestamp] + guest_timestamps
        all_timestamps.sort()
        # calculate # of days between each guest watering
        timestamp_diffs = [(j-i)/86400.0 for i, j in zip(all_timestamps[:-1], all_timestamps[1:])]
        # plant's latest timestamp should be set to last timestamp before a
        # gap of 5 days
        # TODO: this considers a plant watered only on day 1 and day 4 to be
        # watered for all 4 days - need to figure out how to only add score
        # from 24h after each watered timestamp
        last_valid_element = next((x for x in timestamp_diffs if x > 5), None)
        if not last_valid_element:
            # all timestamps are within a 5 day range, can just use latest one
            return all_timestamps[-1]
        last_valid_index = timestamp_diffs.index(last_valid_element)
        # slice list to only include up until a >5 day gap
        valid_timestamps = all_timestamps[:last_valid_index + 1]
        return valid_timestamps[-1]

    def water_check(self):
        self.watered_timestamp = self.guest_check()
        self.time_delta_watered = int(time.time()) - self.watered_timestamp
        if self.time_delta_watered <= (24 * 3600):
            if not self.watered_24h:
                self.watered_24h = True
            return True
        else:
            self.watered_24h = False
            return False

    def mutate_check(self):
        # Create plant mutation
        # Increase this # to make mutation rarer (chance 1 out of x each second)
        CONST_MUTATION_RARITY = 10000
        mutation_seed = random.randint(1,CONST_MUTATION_RARITY)
        if mutation_seed == CONST_MUTATION_RARITY:
            # mutation gained!
            mutation = random.randint(0,len(self.mutation_list)-1)
            if self.mutation == 0:
                self.mutation = mutation
                return True
        else:
            return False

    def growth(self):
        # Increase plant growth stage
        if self.stage < (len(self.stage_list)-1):
            self.stage += 1

    def water(self):
        # Increase plant growth stage
        if not self.dead:
            self.watered_timestamp = int(time.time())
            self.watered_24h = True

    def start_over(self):
        # After plant reaches final stage, given option to restart
        # increment generation only if previous stage is final stage and plant
        # is alive
        if not self.dead:
            next_generation = self.generation + 1
        else:
            # Should this reset to 1? Seems unfair.. for now generations will
            # persist through death.
            next_generation = self.generation
        self.write_lock = True
        self.kill_plant()
        while self.write_lock:
            # Wait for garden writer to unlock
            # garden db needs to update before allowing the user to reset
            pass
        if not self.write_lock:
            self.__init__(self.file_name, next_generation)

    def kill_plant(self):
        self.dead = True

    def unlock_new_creation(self):
        self.write_lock = False

    def start_life(self, dm):
       # runs life on a thread
       thread = threading.Thread(target=self.life, args=(dm,))
       thread.daemon = True
       thread.start()

    def life(self, dm):
        # I've created life :)
        counter = 0
        generation_bonus = round(0.2 * (self.generation - 1), 1)
        score_inc = 1 * (1 + generation_bonus)
        while True:
            counter += 1
            if not self.dead:
                if self.watered_24h:
                    self.ticks += score_inc
                    if self.stage < len(self.stage_list)-1:
                        if self.ticks >= self.life_stages[self.stage]:
                            self.growth()
                    if self.mutate_check():
                        pass

            if self.water_check():
                # Do something
                pass

            if self.dead_check():
                dm.harvest_plant(self)
                self.unlock_new_creation()

            if counter % 3 == 0:
                dm.save_plant(self)
                dm.data_write_json(self)
                dm.update_garden_db(self)

            if counter % 30 == 0:
                dm.update_garden_json()
                counter = 0

            # TODO: event check
            time.sleep(2)
