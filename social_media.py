import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import netgraph
from networkx_viewer import Viewer
from person import Person, Post
from graph_funcs import gen_rand_ppl, link_ppl_rand_graph


# Useful to know exactly how it's implemented
def gaussian(x, mu=0.5, sigma=0.05):
    norm = 1 / (sigma * np.sqrt(2 * np.pi))
    expo = - 1 / 2 * ((x - mu) / sigma) ** 2
    return norm * np.exp(expo)


# Finds the polarization and average opinion of the population
def poll_opinions(G, show_hist=False):
    opinion_poll = []
    for node in G.nodes(data=True):
        name = node[1]['Name']
        person = node[1]['Person']
        opinion = person.get_opinion()
        # print(f"Name is {name}, opinion is {opinion}")
        opinion_poll.append(opinion)
    if show_hist:
        fig, axs = plt.subplots(1)
        # We can set the number of bins with the `bins` kwarg
        axs.hist(opinion_poll, bins=20, density=True)
        lin = np.linspace(0, 1, 100)
        axs.plot(lin, gaussian(lin))
        plt.show()


# Function that iterates through a list of posts to find the one that is closest to the specified attributes
def find_post_with_attr(list_posts, des_interest, des_leaning):
    """
    @type list_posts: list
    """
    closest_post = None
    closest_err = float('inf')
    # Iterate through the given list of posts and find the one with the closest attributes
    for post in list_posts:
        err = post.l2_diff(des_interest, des_leaning)
        # Updates the current closest posts if a better one is found
        if err < closest_err:
            closest_post = post
            closest_err = err
    return closest_post


def add_available_post(array, post):
    """
    This function takes in a post, and stores the stripped down data (leaning, interest, and id) in a numpy array. Sorts the
    posts by their leaning for quick access by the social media site
    @param array: numpy n by 3 array of doubles
    @param post: post to be stored in the array
    @return: array with the post appended
    """
    if len(array) == 0:
        return np.array([post.get_stripped_data()])
    idx = np.searchsorted(array[:, 0], post.get_leaning())
    # print(f"array started out as \n{np.around(array, 2)}\n want to add post with {np.round(post.get_leaning(), 2)} leaning"
    #       f" to index {idx}")
    if idx == 0:
        return np.concatenate(([post.get_stripped_data()], array))
    elif idx == len(array):
        return np.concatenate((array, [post.get_stripped_data()]))

    # print(f"post is {post}, array is {array} index is {idx}, get_stripped_data returns {post.get_stripped_data()}")
    # print(f"array[:idx] is {array[:idx]}, and array[idx:] is {array[idx:]}")
    return np.concatenate((array[:idx], [post.get_stripped_data()], array[idx:]))


def send_news(user):
    """
    @type user: Person
    """
    opinion = user.get_opinion()
    # TODO: based on the user's current opinion, send them news that reinforces their beliefs


# class Company:
if __name__ == "__main__":
    # num_mc_cycles = 1
    num_users = 10
    avg_cxns = 3
    num_time_cycles = 100

    # These are the users that we will keep running tests on. We will randomize the graph later
    users = gen_rand_ppl(num_users)
    graph = link_ppl_rand_graph(users, 3)

    """
    This is all the content that has been generated in the last couples cycles of the algorithm. I don't think we can
    store all of the data, because I ran a test and 10,000^2 posts managed to use up all of my memory.
    If we choose to remove duplicate posts from people's feeds, we can use a decorator on the node, and employ this
    indexing system so that we don't have to keep track of every single post that they have seen in the past
    """
    num_stored_cycles = 7
    store_idx = -1
    all_content = [i for i in range(num_stored_cycles)]

    # going through multiple time cycles
    for i in range(num_time_cycles):
        # This is the most novel user-generated content
        new_content = np.ones([0, 3])
        """
        This is the first time that we'll iterate through the graph. The first time, we're seeing who posted on their
        message board. It's kind of inefficient, but I don't see a way around it if we always want to procure the
        freshest news for the users. This loop iterates through every node in the graph and gives a tuple with info
        about the node
        """
        for node_tuple in graph.nodes(data=True):
            # Retrieving the associated person with each node
            person = node_tuple[1]['Person']
            name = node_tuple[1]['Name']

            # Seeing if that person decides to make a post at this timestep
            post = person.make_post()
            """
            if post is of the proper type (not None) then this portion of the code will send the post to all of this
            person's friends
            """
            if isinstance(post, Post):
                # If the user decides not to make a post, they return None which is not appended
                new_content = add_available_post(new_content, post)
                """
                node_tupe is a tuple that holds the node index, as well as its attributes. Have to index into it to
                use it for an adjacency call, which returns an iterable of node indices
                """
                for neigh_node in graph.adj[node_tuple[0]]:
                    """
                    Notifies all of their friends directly that they made a post
                    graph.nodes[index] returns the attributes of the node, which is a dictionary which we can index
                    into using the key ['Person'] to get the Person and call its methods
                    """
                    graph.nodes[neigh_node]['Person'].notify(post)

        print(f"new content:\n{np.around(new_content, 2)}")
        store_idx += 1
        if store_idx > 2:
            store_idx = 0
        all_content[store_idx] = new_content

        """
        The second time that we iterate through the graph. This time, we'll actually be making predictions about
        what people want to see in their inbox
        """
        for node_tuple in graph.nodes(data=True):
            person = node_tuple[1]['Person']
            # Adding news to their feed (factoring this out so that it's easier to modify later)
            send_news(person)
            person.cycle()
