import numpy as np
from scipy.special import expit, gamma
import names
import itertools
from history import History

margin = 1E-16


def put_in_range(num, margin=0):
    """
    @type num: float
    @type margin: float
    """
    if num < margin:
        num = margin
    if num > 1 - margin:
        num = 1 - margin
    return num


# Returns the value of a beta distribution at x with a and b parameters
def beta_dist(x, a, b):
    # we can't raise 0 to a negative power, so we're adding a margin to avoid divide by zero errors
    assert 0 <= x <= 1
    x = put_in_range(x, margin)
    a = put_in_range(a, margin)
    b = put_in_range(b, margin)
    norm = 1
    func = 1
    try:
        norm = gamma(a + b) / gamma(a) * gamma(b)
    except ValueError:
        print(f"normalizing the gamma function didn't like x={x}, a={a}, and b={b}")
    try:
        func = (x ** (a - 1)) * ((1 - x) ** (b - 1))
    except ZeroDivisionError:
        print(f"doesn't like the values x={x}, a={a}, and b={b}")

    return func * norm


# This is the curve that Ebbinghaus came up with for his empirical data. k and c were used as fitting parameters
def ebbinghaus(time, k, c):
    """
    @type time: int
    @param time: Time passed since the user saw the post
    @type k: float
    @param k: Fitting parameter. I'm probably going to set this to 20 based on my desmos experiments
    @type c: float
    @param c: Another fitting parameter. Higher c indicates that the person takes longer to forget. I may set this to
    be the engagement the user had with the post (higher engagement -> better retention
    @return: float in the range [0, 1] that represents how much the user has forgotten something
    """
    denom = (np.log10(time + 1)) ** c + k
    return k / denom


# Something to add polarization. Graph is in desmos
def skew_mean(mean):
    mean = put_in_range(mean, margin)
    # Intermediate calculation
    inter = np.cbrt(0.5 ** 2 * (mean - 0.5))
    return inter + 0.5


class Post:
    # Taken from stackoverflow question 1045344
    new_id = itertools.count()

    """
    Instantiates a post with the given attributes
    """

    def __init__(self, leaning, interest_value, id_tag=None, author=None):
        self.interest_value = leaning
        self.leaning = interest_value
        if isinstance(id_tag, int):
            self.id = id_tag
        else:
            self.id = next(Post.new_id)
        if isinstance(author, str):
            self.name = author
        else:
            self.name = "ANON"

    """
    Instantiates a post from an array holding the leaning, interest value, and ID
    """

    @classmethod
    def from_array(cls, array):
        assert len(array) == 3
        return cls(array[0], array[1], id_tag=array[2])

    """
    When we're looking for a post with certain characteristics, this method is useful for seeing how far "off" from
    our ideal post we are
    """

    def l2_diff(self, des_interest, des_leaning):
        inter_err = (self.interest_value - des_interest) ** 2
        lean_err = (self.leaning - des_leaning) ** 2
        return np.sqrt(inter_err + lean_err)

    # returns the unique id of the post
    def get_id(self):
        return self.id

    def get_leaning(self):
        return self.leaning

    def get_interest(self):
        return self.interest_value

    # This returns the post ID, its interest value, and its leaning as a list. Useful when trying to save memory
    def get_stripped_data(self):
        return [self.leaning, self.interest_value, self.id]


class Person:
    def __init__(self, consumption, expected_engagement, activity, name=None, initial_opinion=0.5,
                 begin_online=True):
        """
        @param consumption: integer indicating how many posts, on average, this user will consume
        @param expected_engagement: float in the range [0, 1] indicating, on average, how engaging a post
        must been to keep the user online
        @param activity: float in the range [0, 1] indicating how frequently the user creates posts
        @param name: string that holds the person's name
        @param initial_opinion: float in the range [0, 1] indicating what they initially believe about the issue
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

        # Keeps track of how many time steps have passed in the algorithm
        self.time_step = 0
        # This determines how many posts actually impact a user's opinion. Anything that's older than this will be
        # forgotten
        self.num_remembered_times = 20
        # Keeps track of the last couple of posts that we have seen. Used in belief_update_func
        self.op_update_posts = [[i, 1, self.opinion] for i in range(5)]

    @staticmethod
    def deprecated_how_engaging(post, user_leaning):
        """
        @type post: Post
        @type user_leaning: float
        @return:
        """
        x = post.get_leaning()
        """
        This section tries to account for the fact that we like news which aligns most closely with our own views most.
        More information in the documentation and desmos page
        """
        # We have an inflection point at a leaning of 0.9 for this value of the standard deviation
        std_dev = 0.084
        # We need to calculate a and b for the beta distribution (uses desmos' example page calculations)
        temp_num = user_leaning * (1 - user_leaning) / (std_dev ** 2)
        a = user_leaning * temp_num
        b = (1 - user_leaning) * temp_num
        # our cutoff for the gamma distribution (to keep it from blowing up to infinity)
        cutoff = 10
        bias_factor = (min(beta_dist(x, a, b), cutoff) / cutoff + 1) / 2
        return post.get_interest() * bias_factor

    @staticmethod
    def how_engaging(post, user_leaning):
        """
        @type post: Post
        @type user_leaning: float
        @return:
        """
        x = post.get_leaning()
        mean = skew_mean(user_leaning)
        # mean = user_leaning
        # print(f"mean is {mean} margin is {margin}")
        mean = put_in_range(mean, margin)
        x = put_in_range(x, margin)
        """
        This section tries to account for the fact that we like news which aligns most closely with our own views most.
        More information in the documentation and desmos page
        """
        # We have an inflection point at a leaning of 0.9 for this value of the standard deviation
        std_dev = 0.084
        # We need to calculate a and b for the beta distribution (uses desmos' example page calculations)
        temp_num = mean * (1 - mean) / (std_dev ** 2)
        a = mean * temp_num
        b = (1 - mean) * temp_num
        # our cutoff for the gamma distribution (to keep it from blowing up to infinity)
        cutoff = 10
        # bias_factor = (min(beta_dist(x, a, b), cutoff) / cutoff + 1) / 2
        bias_factor = min(1, (3 * beta_dist(x, a, b) / 10 + 0.3) / 2)
        result = post.get_interest() * bias_factor
        if result > 1:
            print(f"Result is greater than 1!!! ({result})\nbias factor is {bias_factor} and interest is \
{post.get_interest()}")
        return result

    # How the user updates their beliefs. Subject to modification
    def belief_update_func(self, post_leaning, engagement):
        self.op_update_posts.append([self.time_step, engagement, post_leaning])
        total = 0
        norm = 0
        for element in self.op_update_posts:
            # print(f"checking out element {element}")
            # We're finding the weighted average of the posts' leaning, weighted by the engagement the user had
            total += element[1] * element[2]
            norm += element[1]
        # print(f"{self.name} went from believing {self.opinion} to {total / norm}")
        return total / norm

    def truncate_update_posts(self):
        index = len(self.op_update_posts)
        for idx, element in enumerate(self.op_update_posts):
            if element[0] > self.num_remembered_times:
                index = idx
                break
        my_list = self.op_update_posts[:index]
        return my_list

    # Resets the state of the person to their original opinion, with an empty feed and no notifications
    def reset(self, is_online=True):
        self.opinion = self.initialized_opinion
        self.feed.clear()
        self.notifications.clear()
        self.is_online = is_online
        self.history.new_epoch()
        self.time_step = 0
        self.op_update_posts = [[i, 1, self.opinion] for i in range(5)]

    # Method to see if the person is online or not
    def get_online(self):
        return self.is_online

    # This is called to determine whether or not the person creates a post. If not, they return None. If they do,
    # they return the post
    def make_post(self):
        # If the person is offline, they will not be making any posts
        if not self.is_online:
            return None
        elif np.random.rand() < self.activity:
            # Screening the leaning of the user
            leaning = self.opinion + np.random.normal(loc=0.0, scale=0.05)
            if leaning > 1:
                leaning = 1
            elif leaning < 0:
                leaning = 0
            # Initializes a post with a random engagement factor and a bias which reflects the user's current opinion
            post = Post(leaning, np.random.rand())
            return post
        # Otherwise the user has decided not to make a post, and returns None
        return None

    # Function that has the person read all of their notifications from direct friends
    def _read_notifications(self):
        # Similar to _read_feed, keeps track of how engaged the person was reading each post, and returns a list of
        # these values
        engagement = []
        for post in self.notifications:
            interest = Person.how_engaging(post, self.opinion)
            engagement.append(interest)
            self.opinion = self.belief_update_func(post.get_leaning(), interest)
        return engagement

    # Function that has the person read the first few posts in their inbox
    def _read_feed(self):
        num_posts_to_read = int(self.consumption + np.random.normal())
        if num_posts_to_read < 1:
            num_posts_to_read = 1
        # This list keeps track of the engagement of the user while reading each article (interest + screen)
        engagement = []
        if num_posts_to_read > len(self.feed):
            print(f"You haven't given {self.name} enough posts to read!!! They're getting bored!")
            return engagement
        for i in range(num_posts_to_read):
            post = self.feed.pop(0)
            # This person finds the article interesting at face value (does not take into account their leaning)
            interest = Person.how_engaging(post, self.opinion)
            engagement.append(interest)
            self.opinion = self.belief_update_func(post.get_leaning(), interest)
        return engagement

    # Function that simulates random phone pickups. if they get an interesting enough notification, they'll go online
    def _check_phone(self):
        for post in self.notifications:
            if post.get_interest() > self.exp_eng:
                self.is_online = True
                break
        self.notifications.clear()

    # This is the function that will determine whether or not the person decides to keep looking through their feed
    def _stay_online(self, tot_interest):
        prob = np.pi / 2 * np.arctan(tot_interest - self.consumption * self.exp_eng + np.tan(np.pi / 4))
        # There's always a 5% chance that people stay online, even if they haven't gotten very interesting posts
        prob = max(prob, 0.05)
        return np.random.rand() <= prob

    # Sends a notification to the person's phone
    def notify(self, post):
        """
        @type post: Post
        """
        assert isinstance(post, Post)
        # print(f"{self.name} notified of post")
        self.notifications.append(post)

    # Adds a post to their feed
    def add_to_feed(self, post):
        assert isinstance(post, Post)
        self.feed.append(post)

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
        self.time_step += 1
        # Have the user forget some posts
        self.op_update_posts = self.truncate_update_posts()
        return tot_interest
