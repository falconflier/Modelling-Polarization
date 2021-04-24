import numpy as np
# This class keeps track of the statistics of a person throughout the entire time that the algorithm is run, through
# different stages of the Monte Carlo process

# Useful for checking if a given string seems to indicate 'true.' However, it returns false if anything except what is
# shown in the list is passed to the function
def str2bool(string):
    """
    @type string: str
    """
    string = string.lower()
    return string in ['yes', 'y', 'true', 't']
    

# Keeps track of a person's history throughout many iterations of the Monte Carlo cycle. I'm still deciding how to
# associate one of these with each person. It's probably best just to instantiate a new History for every Person
class History:
    # Initializes data structures to keep track of multiple epochs
    def __init__(self):
        self.epoch_idx = 0
        self.epoch_list = []
        self.cur_epoch = None
        # This one keeps track of how many time cycles have passed in the social media algorithm
        self.time_index = 0

    # This stores all relevant data about the Person after every time period
    # Automatically increments the time index when it is called
    def store_data(self, cur_opinion, entire_feed=None, post_engagement=None, notifications=None):
        self.cur_epoch.store_posts(entire_feed)
        self.time_index += 1

    # This method will display all the information we have about the person's beliefs and, critically, the news articles
    # that they saw at every stage of the journey
    def display_epoch(self, epoch):
        if not isinstance(epoch, int) or 0 > epoch > len(self.epoch_list):
            print(f"Epoch index is not valid. We only randomized the graph {len(self.epoch_list)} times")
            return
        # TODO: write the visualization methods for epoch and use them here

    # This method will begin a new epoch to store info in
    def new_epoch(self):
        self.epoch_idx += 1
        new_epoch = Epoch()
        self.epoch_list.append(new_epoch)
        self.cur_epoch = new_epoch


# This class is useful to demarcate the different stages of the MC algorithm, since we are likely to reset people
class Epoch:
    def __init__(self):
        """
        Initializes the Epoch. Doesn't take in any arguments (yet)
        """
        """
        This be a list of posts, which will let us see exactly what the person was exposed
        to without having to go through an outside list
        """
        self.read_posts = []
        """
        This will be a numpy array of values that 
        """
        self.read_posts_indices = np.ones(0)
        self.all_posts = []

    """
    Taken from stackexchange question 48776902. Goes through a sorted list, finds the index that the value would have
    been at (value should not already been in sorted_list) and adds value at that index. Used to speed up the bookeeping
    of what posts the user has already seen.
    """
    def _add_read_posts(self, posts):
        """
        @param posts: The list of indices (integers) to be added to self.read_posts_indices
        @return: Nothing. Sorts and inserts all integers in values self.read_posts
        """
        for post in posts:
            val = post.get_id()
            # Find the index that val should be at
            idx = np.searchsorted(self.read_posts_indices, val)
            # "insert" value at that index
            self.read_posts_indices = np.concatenate((self.read_posts_indices[:idx], [val], self.read_posts_indices[idx:]))

    # Stores a list of all the posts the user actually finished reading
    def store_read_posts(self, posts):
        self.read_posts.append(posts)
        self._add_read_posts(posts)

    # Stores a list of all the posts which were in the user's feed, but which they may or may not have finished reading
    def store_all_posts(self):
        pass
