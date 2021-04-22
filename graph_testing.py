import secrets
import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import netgraph
from networkx_viewer import Viewer
from person import Person, Post


# Useful to know exactly how it's implemented
def _gaussian(x, mu=0.5, sigma=0.05):
    norm = 1 / (sigma * np.sqrt(2 * np.pi))
    expo = - 1 / 2 * ((x - mu) / sigma) ** 2
    return norm * np.exp(expo)


# A method that I shamelessly copied from stackexchange while I was trying to get interactive graphs to work
def stack_exchange_interactive_graph():
    import numpy as np
    import matplotlib.pyplot as plt; plt.ion()
    plt.ion()
    import networkx
    import netgraph  # pip install netgraph

    # Construct sparse, directed, weighted graph
    total_nodes = 20
    weights = np.random.rand(total_nodes, total_nodes)
    connection_probability = 0.1
    is_connected = np.random.rand(total_nodes, total_nodes) <= connection_probability
    graph = np.zeros((total_nodes, total_nodes))
    graph[is_connected] = weights[is_connected]

    # construct a networkx graph
    g = networkx.from_numpy_array(graph, networkx.DiGraph)

    # decide on a layout
    pos = networkx.layout.spring_layout(g)

    # Create an interactive plot.
    # NOTE: you must retain a reference to the object instance!
    # Otherwise the whole thing will be garbage collected after the initial draw
    # and you won't be able to move the plot elements around.
    plot_instance = netgraph.InteractiveGraph(graph, node_positions=pos)

    ######## drag nodes around #########

    # To access the new node positions:
    node_positions = plot_instance.node_positions


# Displays the different ways that networkx can visualize a graph
def test_nx_draw(graph):
    print("Standard display")
    nx.draw(graph)
    plt.show()
    print("Draw circular layout")
    nx.draw_circular(graph)
    plt.show()
    print("Kamada-Kawai force-directed layout")
    nx.draw_kamada_kawai(graph)
    plt.show()
    print("Draw with random layout")
    nx.draw_random(graph)
    plt.show()
    print("draw with spectral 2D layout")
    nx.draw_spectral(graph)
    plt.show()
    print("draw with spring layout")
    nx.draw_spring(graph)
    plt.show()
    print("draw with shell layout")
    nx.draw_shell(graph)
    plt.show()


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
def _gen_rand_ppl(num_people):
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


# This function generates a random graph with each Node associated with a randomly generated instance of Person
def _gen_people_graph(num_people, avg_connections):
    # Total number of nodes in the graph, and the lowest possible average for the degrees
    ppl_dict = _gen_rand_ppl(num_people)
    # Generating the graph that will be associated with the people
    G = _gen_connected_graph(num_people, avg_connections)
    # Associating the graph with the randomly generated people
    nx.set_node_attributes(G, ppl_dict)
    return G


# This function takes in a dictionary of random people and associates them with a randomly generated graph with a
# minimum average degree of avg_connections (see _gen_connected_graph())
def _associated_ppl_with_rand_graph(people_dict, avg_connections):
    num_nodes = len(dict)
    graph = _gen_connected_graph(num_nodes, avg_connections)
    nx.set_node_attributes(G, people_dict)
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
        axs.plot(lin, _gaussian(lin))
        plt.show()


# Here are useful functions that I've found online which might come in handy:
# set(<list>) turns the list into a set
# set_A.difference(set_B) returns the difference of the sets A - B
# from functools import cache OR from functools import lru_cache automates memoization
# nx.is_connected(G) returns True (False) if G is Connected (Not Connected)
# nx.connected_components(G) returns generators of sets in G
# nx.gnp_random_graph(n, p, seed=None, directed=False) returns a randomly generated graph with n nodes. Selects
# edges with p probability
# nx.fast_gnp_random_graph(...) does something similar, but it's faster for sparse graphs
if __name__ == "__main__":
    G = _gen_people_graph(100, 3)
    poll_opinions(G, show_hist=True)
    # nx.draw_kamada_kawai(G, with_labels=True)
    # plt.show()
    # app = Viewer(G)
    # app.mainloop()
