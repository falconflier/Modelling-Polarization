import numpy as np
import networkx as nx
import secrets
import matplotlib.pyplot as plt
from person import Person, Post

"""
This file contains all the functions for generating random people and associating them with a random graph.
social_media.py was getting a bit crowded so I refactored it into this file
"""


# Uses fast_gnp_random_graph cuz I'm not expecting very connected graphs
def gen_connected_graph(num_nodes, avg_degree):
    assert num_nodes > 0
    prob = 0
    # Avoiding divide by 0 errors (if num_nodes==1, we want prob==0)
    if num_nodes > 1:
        # In an (undirected) graph we have n(n-1)/2 total possible edges, so we need a proper probability of drawing an
        # edge
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
    # print(f"Number of added edges is {num_added_edges}")
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
        rand_person = Person(int(np.random.rand() * 5), np.random.rand() / 2, np.random.rand(), initial_opinion=init_op)
        # The dictionary holds the person's name, and the actualy instance of the person class to call methods on
        rand_person_dict = {"Name": rand_person.my_name_is(), "Person": rand_person}
        ppl_dict[i] = rand_person_dict
    return ppl_dict


# This function takes in a dictionary of random people and associates them with a randomly generated graph with a
# minimum average degree of avg_connections (see _gen_connected_graph())
def link_ppl_rand_graph(people_dict, avg_connections):
    num_nodes = len(people_dict)
    graph = gen_connected_graph(num_nodes, avg_connections)
    nx.set_node_attributes(graph, people_dict)
    return graph


def draw_bias_graph(graph):
    """
    @type graph: the graph to draw, with associated dictionary of People with an opinion field
    @return:
    """
    color_map = []
    for node_tuple in graph.nodes(data=True):
        # Retrieving the associated leaning with each node
        leaning = node_tuple[1]['Person'].get_opinion()
        if leaning < 0.5:
            color_map.append('red')
        elif leaning > 0.5:
            color_map.append('blue')
        else:
            color_map.append('green')
    nx.draw(graph, node_color=color_map, with_labels=True)
    plt.show()
