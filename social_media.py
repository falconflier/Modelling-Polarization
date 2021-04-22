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
        # Points to a person with certain attributes and names
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


# class Company:
if __name__ == "__main__":
    num_reruns = 1
    num_users = 10
    avg_cxns = 3
    num_cycles = 1

    # These are the users that we will keep running tests on. We will randomize the graph later
    users = gen_rand_ppl(num_users)
    graph = associated_ppl_with_rand_graph(users, 3)
    # going through multiple time cycles
    for i in range(num_cycles):
        # This is the most novel user-generated content
        new_content = []
        for node in graph.nodes(data=True):
            person = node[1]['Person']
            post = person.make_post()
            if isinstance(post, Post):
                new_content.append(post)
