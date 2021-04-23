import secrets
import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import netgraph
from networkx_viewer import Viewer
from person import Person, Post


# Useful to know exactly how it's implemented
def gaussian(x, mu=0.5, sigma=0.05):
    norm = 1 / (sigma * np.sqrt(2 * np.pi))
    expo = - 1 / 2 * ((x - mu) / sigma) ** 2
    return norm * np.exp(expo)


# Uses fast_gnp_random_graph cuz I'm not expecting very connected graphs
def _gen_connected_graph(num_nodes, avg_degree):
    # In an (undirected) graph we have n(n-1)/2 total possible edges, so we need a proper probability of drawing an edge
    prob = 2 * avg_degree * num_nodes / (num_nodes * (num_nodes - 1))
    if prob > 1:
        prob = 1
    # Generating a random graph with the specified attributes
    G = nx.fast_gnp_random_graph(num_nodes, prob)
    # nx.draw_kamada_kawai(G)
    # plt.show()
    num_added_edges = 0
    # Making the graph connected
    while not nx.is_connected(G):
        # Gives a generator of sets of all nodes
        sets_of_cxns = nx.connected_components(G)
        first_list = list(next(sets_of_cxns))
        second_list = list(next(sets_of_cxns))
        first_node = secrets.choice(first_list)
        second_node = secrets.choice(second_list)
        G.add_edge(first_node, second_node)
        num_added_edges += 1
    print(f"Number of added edges is {num_added_edges}")
    # nx.draw_kamada_kawai(G)
    # plt.show()
    return G


# This function generates a dictionary of random people with specified size
def gen_rand_ppl(num_people):
    # Dictionary of dictionaries
    ppl_dict = {}
    # Populating the dictionary
    for i in range(num_people):
        init_op = np.random.normal(loc=0.5, scale=0.05)
        if init_op < 0:
            init_op = 0
        elif init_op > 1:
            init_op = 1
        rand_person = Person(int(np.random.rand() * 5), np.random.rand(), np.random.rand(), initial_opinion=init_op)
        # The dictionary holds the person's name, and the actualy instance of the person class to call methods on
        rand_person_dict = {"Name": rand_person.my_name_is(), "Person": rand_person}
        ppl_dict[i] = rand_person_dict
    return ppl_dict


# This function takes in a dictionary of random people and associates them with a randomly generated graph with a
# minimum average degree of avg_connections (see _gen_connected_graph())
def associated_ppl_with_rand_graph(people_dict, avg_connections):
    num_nodes = len(people_dict)
    graph = _gen_connected_graph(num_nodes, avg_connections)
    nx.set_node_attributes(graph, people_dict)
    return graph


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


"""
Given that even social media companies don't have a direct link into your mind, I'm going to write a function that looks
at how engaged the use was with different articles in the last step, and tries to predict how they are leaning on the
issue
"""
def predict_leaning():
    # TODO: make this actually predict something
    return 0.5


# class Company:
if __name__ == "__main__":
    # num_mc_cycles = 1
    num_users = 3
    avg_cxns = 3
    num_time_cycles = 1

    # These are the users that we will keep running tests on. We will randomize the graph later
    users = gen_rand_ppl(num_users)
    graph = associated_ppl_with_rand_graph(users, 3)
    # going through multiple time cycles
    for i in range(num_time_cycles):
        # This is the most novel user-generated content
        new_content = []
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
                new_content.append(post)
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
        """
        The second time that we iterate through the graph. This time, we'll actually be making predictions about
        what people want to see in their inbox
        """
        for node_tuple in graph.nodes(data=True):
            person = node_tuple[1]['Person']
            # We need to know how engaged they were with the past content
            past_engagement = node_tuple[1]['Person']

