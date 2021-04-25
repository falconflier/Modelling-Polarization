from person import Person, Post
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx


# A method that I stole straight from Matplotlib's documentation. Would be extremely cool to use to model changing
# biases over time
def animated_hist():
    import numpy as np

    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    # Fixing random state for reproducibility
    np.random.seed(19680801)
    # Fixing bin edges
    HIST_BINS = np.linspace(-4, 4, 100)

    # histogram our data with numpy
    data = np.random.randn(1000)
    n, bin_edges = np.histogram(data, HIST_BINS)

    def prepare_animation(bar_container):
        def animate(frame_number):
            # simulate new data coming in
            data = np.random.randn(1000)
            n, _ = np.histogram(data, HIST_BINS)
            for count, rect in zip(n, bar_container.patches):
                rect.set_height(count)
            return bar_container.patches

        return animate

    fig, ax = plt.subplots()
    bin_edges, bin_edges, bar_container = ax.hist(data, HIST_BINS, lw=1, ec="yellow", fc="green", alpha=0.5)
    ax.set_ylim(top=55)  # set safe limit to ensure that all data is visible.

    ani = animation.FuncAnimation(fig, prepare_animation(bar_container), 50,
                                  repeat=False, blit=True)

    ani.save('./animation.gif', writer='imagemagick', fps=60)

    plt.show()


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





data = []
for i in range(10000):
    data.append(np.random.normal(loc=0.5, scale=0.05))
plt.hist(data, bins=50, range=[0, 1])
plt.show()
# my_array = np.zeros([10, 2])
# for i in range(10):
#     rand_row = np.array([i, np.random.rand()])
#     my_array[i] = rand_row
# # np.random.shuffle(my_array)
# print(my_array)
# print(f"sorted array:\n{my_array[my_array[:, 1].argsort()]}")

# my_array = np.empty(0)
# print(f"my array is {my_array}")
# my_array = np.insert(my_array, 0, np.array([13]))
# print(f"my array is {my_array}")
# my_array = np.insert(my_array, -1, np.arange(2, 9, 1))
# print(f"my array is {my_array}")
# my_array = np.insert(my_array, 0, np.array([-1]))
# print(f"my array is {my_array}")
# print(f"sorted array is {np.sort(my_array)}")
# print(np.searchsorted(my_array, 1))
# my_array = np.concatenate((np.arange(3), np.arange(5, 10)))
# print(f"my array is {my_array}")
# val = 3
# idx = np.searchsorted(my_array, val)
# my_array = np.concatenate((my_array[:idx], [val], my_array[idx:]))
# print(f"my array is {my_array}")

# my_list = [1, 2, 3, 4, 5]
# my_list.append(6)
# print(my_list)
# my_list.insert(0, 7)
# print(my_list)
# print(my_list.pop(0))
# print(my_list)
# print(my_list.pop())
#
# my_post = Post(0.7, 0.8)
# print(my_post.interest_value)
# print(my_post.leaning)
# print(f"my post has id: {my_post.id}")
# for i in range(10):
#     my_post = Post(np.random.rand(), np.random.rand())
#     print(f"my post has id: {my_post.id}")
#
# string = "HELLOooooO"
# print(string.lower())
# print(string)
