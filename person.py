import numpy as np
from scipy.special import expit
import names


# Rule to update what each person believes after seeing a new news article. This is not super accurate yet
def simple_update(stimulus, prior):
    return expit(stimulus + prior)


class Post:
    def __init__(self, engagement, leaning):
        self.engaging = engagement
        self.leaning = leaning


class Person:
    def __init__(self, consumption, expected_engagement, activity, name=None, initial_opinion=0.5, update_func=simple_update, begin_online=True):
        # This stat determines how likely the person is to post
        self.activity = activity
        # Keeps track of how much content this person can consume (on average)
        self.consumption = consumption
        # This is how engaging the person expect the average article in their feed to be
        self.exp_eng = expected_engagement
        # This keeps track of all the novel articles which the social media site delivers to this person
        self.feed = []
        # This keeps track of direct notifications to the user (from adjacent nodes)
        self.notifications = []
        # This keeps track of what the person thinks over time. Initialized to be some value
        self.opinion = initial_opinion
        # This is the function that they use to determine how to update their beliefs based on new stimuli
        self.belief_update_func = update_func
        # This keeps track of whether they are online or not
        self.is_online = begin_online
        # Makes a random name for the person or uses the one specified upon instantiation
        if isinstance(name, str):
            self.name = name
        else:
            self.name = names.get_full_name()

    def _make_post(self):
        # TODO: write the method that determines how people create content
        pass

    # Function that has the person read the first few posts in their inbox
    def _read_feed(self):
        num_posts_to_read = self.consumption + np.random.normal()
        if num_posts_to_read < 1:
            num_posts_to_read = 1
        # This list keeps track of the engagement of the user while reading each article
        engagement = []
        # This keeps track of how stimulating the session was as a whole
        interest = 0
        for i in range(num_posts_to_read):
            pass
        return interest, engagement

    # Function that simulates random phone pickups. if they get an interesting enough notification, they'll go online
    def _check_phone(self):
        for post in self.notifications:
            if post.get_engagement() > self.exp_eng:
                self.is_online = True
                break
        self.notifications.clear()

    # This is the function that will determine whether or not the person decides to keep looking through their feed
    def _stay_online(self, tot_interest):
        prob = np.pi / 2 * np.arctan(tot_interest - self.consumption * self.exp_eng + np.tan(np.pi / 4))
        # There's always a 5% chance that people
        prob = max(prob, 0.05)
        return np.random.rand() >= prob

    # Sends a notification to the person's phone
    def notify(self, post):
        """
        @type post: Post
        """
        assert isinstance(post, Post)
        self.notifications.append(post)

    # Returns the person's name
    def my_name_is(self):
        return self.name

    # Gets the person's opinion
    def get_opinion(self):
        return self.opinion

    # Function that simulates the person going through their feed, and deciding whether they will be online next cycle
    def cycle(self):
        tot_interest = []
        if self.is_online:
            # Reads through the stuff that's been recommended by the algorithm
            tot_interest, engagement = self._read_feed()
            self.is_online = self._stay_online(tot_interest)
        else:
            # They'll check their phones 10% of the cycles for new notifications
            if len(self.notifications) > 0 and np.random.rand() < 0.1:
                # They'll see if they have any new notifications, and go online if they're interesting
                self._check_phone()
            # The person has a 5% chance of spontaneously going online
            elif np.random.rand() < 0.05:
                self.is_online = True
        return tot_interest
