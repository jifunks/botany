class LoginCompleter:
    """ A loop-based completion system for logins """
    def __init__(self, menu):
        self.s = ""
        self.logins = None
        self.completions = []
        # completion_id has a value of -1 for the base user input
        # and between 0 and len(completions)-1 for completions
        self.completion_id = -1
        self.completion_base = ""
        self.menu = menu

    def initialize(self):
        """ Initialise the list of completable logins """
        garden = self.menu.user_data.retrieve_garden_from_db()
        self.logins = set()
        for plant_id in garden:
            if not garden[plant_id]:
                continue
            entry = garden[plant_id]
            if "owner" in entry:
                self.logins.add(entry["owner"])
        self.logins = sorted(list(self.logins))

    def update_input(self, s):
        """ Update the user input and reset completion base """
        self.s = s
        self.completion_base = self.s
        self.completion_id = -1

    def complete(self, direction = 1):
        """
        Returns the completed string from the user input
        Loops forward in the list of logins if direction is positive, and
        backwards if direction is negative
        """
        def loginFilter(x):
            return x.startswith(self.s) & (x != self.s)

        # Refresh possible completions after the user edits
        if self.completion_id == -1:
            if self.logins is None:
                self.initialize()
            self.completion_base = self.s
            self.completions = list(filter(loginFilter, self.logins))

        self.completion_id += direction
        # Loop from the back
        if self.completion_id == -2:
            self.completion_id = len(self.completions) - 1
        # If we are at the base input, return it
        if self.completion_id == -1 or self.completion_id == len(self.completions):
            self.completion_id = -1
            return self.completion_base
        return self.completions[self.completion_id]
