import numpy as np
from scipy.special import expit
import names
import itertools
from history import History


# Rule to update what each person believes after seeing a new news article. This is not super accurate yet
def simple_update(stimulus, prior):
    return expit(stimulus + prior)


class Post:
    # Taken from stackoverflow question 1045344
    new_id = itertools.count()

    def __init__(self, interest_value, leaning, author=None):
        self.interest_value = interest_value
        self.leaning = leaning
        self.id = next(Post.new_id)
        if isinstance(author, str):
            self.name = author
        else:
            self.name = "Author not specified"

    def l2_diff(self, des_interest, des_leaning):
        inter_err = (self.interest_value - des_interest) ** 2
        lean_err = (self.leaning - des_leaning) ** 2
        return np.sqrt(inter_err + lean_err)


class Person:
    def __init__(self, consumption, expected_engagement, activity, name=None, initial_opinion=0.5
                 , update_func=simple_update, begin_online=True):
        """
        @param consumption: integer indicating how many posts, on average, this user will consume
        @param expected_engagement: float in the range [0, 1] indicating, on average, how engaging a post
        must been to keep the user online
        @param activity: float in the range [0, 1] indicating how frequently the user creates posts
        @param name: string that holds the person's name
        @param initial_opinion: float in the range [0, 1] indicating what they initially believe about the issue
        @param update_func: function that determines how the user updates their beliefs
        @param begin_online: boolean that determines whether the user starts online or not
        """
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
        # This keeps track of what the person thinks over time. Initialized to be some value that we also keep track
        # of for later if we want to reset them (new stage of MC)
        self.opinion = initial_opinion
        self.initialized_opinion = initial_opinion
        # This is the function that they use to determine how to update their beliefs based on new stimuli
        self.belief_update_func = update_func
        # This keeps track of whether they are online or not
        self.is_online = begin_online
        """
        This instance of History is very important, because it will store information about how the user evolves over
        time. I chose to factor it out into a separate class, we'll see if that was wise or not
        """
        self.history = History()
        # Makes a random name for the person or uses the one specified upon instantiation
        if isinstance(name, str):
            self.name = name
        else:
            self.name = names.get_full_name()

    # Resets the state of the person to their original opinion, with an empty feed and no notifications
    def reset(self, is_online=True):
        self.opinion = self.initialized_opinion
        self.feed.clear()
        self.notifications.clear()
        self.is_online = is_online

    # This is called to determine whether or not the person creates a post. If not, they return None. If they do,
    # they return the post
    def make_post(self):
        if np.random.rand() > self.activity:
            # Screening the leaning of the user
            leaning = self.opinion + np.random.normal(loc=0.0, scale=0.1)
            if leaning > 1:
                leaning = 1
            elif leaning < 0:
                leaning = 0
            # Initializes a post with a random engagement factor and a bias which reflects the user's current opinion
            post = Post(np.random.rand(), leaning, author=self.name)
            return post
        # Otherwise the user has decided not to make a post, and returns None
        return None

    # Function that has the person read all of their notifications from direct friends
    def _read_notifications(self):
        # Similar to _read_feed, keeps track of how engaged the person was reading each post, and returns a list of
        # these values
        engagement = []
        for post in self.notifications:
            engagement.append(post.interest_value)
        return engagement

    # Function that has the person read the first few posts in their inbox
    def _read_feed(self):
        num_posts_to_read = self.consumption + np.random.normal()
        if num_posts_to_read < 1:
            num_posts_to_read = 1
        # This list keeps track of the engagement of the user while reading each article (interest + screen)
        engagement = []
        for i in range(num_posts_to_read):
            post = self.feed.pop(0)
            # This person finds the article interesting at face value (does not take into account their leaning)
            # TODO: Update their beliefs, and change their interest based on the bias of the article
            interest = post.interest_value
            engagement.append(interest)
        return engagement

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
        print(f"{self.name} notified of post")
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
            notification_engagement = self._read_notifications()
            feed_engagement = self._read_feed()
            tot_interest = sum(notification_engagement) + sum(feed_engagement)
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
