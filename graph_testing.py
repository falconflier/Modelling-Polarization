import secrets

import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import netgraph
from networkx_viewer import Viewer
from person import Person, Post


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


def _gen_people_graph():
    # Total number of nodes in the graph, and the lowest possible average for the degrees
    num_people = 20
    avg_connections = 2
    # Dictionary of dictionaries
    dict = {}
    # Populating the dictionary
    for i in range(num_people):
        rand_person = Person(int(np.random.rand() * 5), np.random.rand(), np.random.rand())
        # Points to a person with certain attributes and names
        rand_person_dict = {"Name": rand_person.my_name_is(), "Person": rand_person}
        dict[i] = rand_person_dict
    # Generating the graph that will be associated with the people
    G = _gen_connected_graph(num_people, avg_connections)
    print(dict)
    # Associating the graph with the randomly generated people
    nx.set_node_attributes(G, dict)
    return G


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
    G = _gen_people_graph()
    nx.draw_kamada_kawai(G, with_labels=True)
    plt.show()
    app = Viewer(G)
    app.mainloop()
