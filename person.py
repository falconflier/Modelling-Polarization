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
        # Keeps track of how much content this person can consume (on average)
        self.activity = activity
        self.consumption = consumption
        self.exp_eng = expected_engagement
        self.feed = []
        self.notifications = []
        self.opinion = initial_opinion
        self.update_func = update_func
        self.is_online = begin_online
        if isinstance(name, str):
            self.name = name
        else:
            self.name = names.get_full_name()

    # Function that has the person read the first few posts in their inbox
    def read_feed(self):
        # TODO: write this
        return 0

    # Function that simulates random phone pickups. if they get an interesting enough notification, they'll go online
    def check_phone(self):
        for post in self.notifications:
            if post.get_engagement() > self.exp_eng:
                self.is_online = True
                break
        self.notifications.clear()

    # Function that simulates the person going through their feed, and deciding whether they will be online next cycle
    def cycle(self):
        if self.is_online:
            # Reads through the stuff that's been recommended by the algorithm
            engagement = self.read_feed()
            self.is_online = self._stay_online(engagement)
        else:
            # They'll check their phones 10% of the cycles for new notifications
            if len(self.notifications) > 0 and np.random.rand() < 0.1:
                # They'll see if they have any new notifications, and go online if they're interesting
                self.check_phone()
            # The person has a 5% chance of spontaneously going online
            elif np.random.rand() < 0.05:
                self.is_online = True

    # This is the function that will determine whether or not the person decides to keep looking through their feed
    def _stay_online(self, tot_engagement):
        prob = np.pi / 2 * np.arctan(tot_engagement - self.consumption * self.exp_eng + np.tan(np.pi / 4))
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
