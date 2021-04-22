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
        self.article_list = []

    def store_posts(self, posts):
        self.article_list.append(posts)
