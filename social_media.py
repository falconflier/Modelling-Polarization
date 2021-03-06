import time
import numpy as np
import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
import netgraph
from networkx_viewer import Viewer
from person import Person, Post
from graph_funcs import gen_rand_ppl, gen_polar_rand_ppl, gen_biased_rand_ppl, link_ppl_rand_graph, draw_bias_graph


# Useful to know exactly how it's implemented
def gaussian(x, mu=0.5, sigma=0.05):
    norm = 1 / (sigma * np.sqrt(2 * np.pi))
    expo = - 1 / 2 * ((x - mu) / sigma) ** 2
    return norm * np.exp(expo)


# Finds the polarization and average opinion of the population
def poll_opinions(ppl_dict, show_hist=False):
    """
    @type ppl_dict: dict
    @type show_hist: bool
    """
    opinion_poll = []

    # for node in ppl_dict.nodes(data=True):
    #     person = node[1]['Person']
    #     opinion = person.get_opinion()
    #     # print(f"Name is {name}, opinion is {opinion}")
    #     opinion_poll.append(opinion)
    for element in ppl_dict.items():
        opinion_poll.append(element[1]['Person'].get_opinion())
    if show_hist:
        fig, axs = plt.subplots(1)
        # We can set the number of bins with the `bins` kwarg
        axs.hist(opinion_poll, bins=20, density=True)
        lin = np.linspace(0, 1, 100)
        axs.plot(lin, gaussian(lin))
        plt.show()
    return opinion_poll


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


def send_similar_news(user, content):
    """
    @param content: all the available content that has been generated in the last time step, stored as a list of
    numpy arrays (there's probably a more efficient way to do that, but I'm not sure how)
    @type user: Person whose feed we will populate with new posts
    """
    tolerance = 0.3
    opinion = user.get_opinion()
    output = []
    for array in content:
        # Skipping over portions of the array which aren't "initialized"
        if isinstance(array, int):
            continue
        """
        basic idea:
        We're going to check all posts that are within 0.15 leaning of the user's opinion. Then we're going to use the
        static method in Person class to calculate how engaging it will be, rank that, and then send it to the user's
        feed
        """
        # print(f"array is \n{array}\nportion that we're interested in is\n{array[:, 0]}")
        # This is the index that a post with the perfect leaning would have. It's the beginning of our search
        opinion_idx = np.searchsorted(array[:, 0], opinion)
        """
        Checking the posts that have more of a positive leaning
        """
        if opinion_idx < len(array):
            # Initializing the first post that we examine
            post_leaning = array[opinion_idx, 0]
            post = Post.from_array(array[opinion_idx])
            post_idx = opinion_idx
            # While we're still close to the user's preferred region
            while np.abs(post_leaning - opinion) < tolerance and post_idx < len(array):
                # Predicting how riveting the post will be, and storing that
                predicted_engagement = Person.how_engaging(post, opinion)
                output.append([predicted_engagement, post])
                # If we're at the end, we need to break out of the loop
                if post_idx == len(array) - 1:
                    break
                # Otherwise we can go onto the next post
                post_idx += 1
                post_leaning = array[post_idx, 0]
                post = Post.from_array(array[post_idx])
        """
        Checking the posts that have more of a negative leaning
        """
        if 0 < opinion_idx < len(array):
            # Initializing the first post that we examine
            post_idx = opinion_idx - 1
            post_leaning = array[post_idx, 0]
            post = Post.from_array(array[post_idx])
            # While we're still close to the user's preferred region
            while np.abs(post_leaning - opinion) < tolerance and post_idx >= 0:
                # Predicting how riveting the post will be, and storing that
                predicted_engagement = Person.how_engaging(post, opinion)
                output.append([predicted_engagement, post])
                # If we've reached the zeroeth index, we need to break out of the loop
                if post_idx == 0:
                    break
                # Otherwise we can go onto the next post
                post_idx -= 1
                post_leaning = array[post_idx, 0]
                post = Post.from_array(array[post_idx])
    output = sorted(output, key=lambda x: x[0], reverse=True)
    for tuple in output:
        person.add_to_feed(tuple[1])


def send_news(user, content):
    """
    @param content: all the available content that has been generated in the last time step, stored as a list of
    numpy arrays (there's probably a more efficient way to do that, but I'm not sure how)
    @type user: Person whose feed we will populate with new posts
    """
    tolerance = 0.3
    opinion = user.get_opinion()
    output = []
    for array in content:
        # Skipping over portions of the array which aren't "initialized"
        if isinstance(array, int):
            continue
        """
        basic idea:
        We're going to check ALL posts, using
        static method in Person class to calculate how engaging it will be, rank that, and then send it to the user's
        feed
        """
        for post_array in array:
            # Recreating the post from information stored about it
            re_post = Post.from_array(post_array)
            # Predicting how riveting the post will be, and storing that
            predicted_engagement = Person.how_engaging(re_post, opinion)
            output.append([predicted_engagement, re_post])
    # Sorting the output by how engaging it is
    output = sorted(output, key=lambda x: x[0], reverse=True)
    # Putting each post, based on its predicted engagement, in the user's feed
    for element in output:
        person.add_to_feed(element[1])


# class Company:
if __name__ == "__main__":
    num_mc_cycles = 1
    """
    runtimes for 100 users:
    at 100 time cycles, takes about 7 seconds
    at 1200 num_time_cycles, takes about 2 minutes to run algorithm
    can go up to 10000 (and maybe higher?), but takes a bit
    """
    avg_cxns = 3
    num_users = 100
    num_time_cycles = 100
    # Keeps track of how long a period of time is. Might be useful later for normalizing data
    len_time_interval = 1

    # These are the users that we will keep running tests on. We will keep them through multiple iterations of the
    # algorithm
    # users = gen_polar_rand_ppl(num_users, 0.25, 0.75)
    # users = gen_rand_ppl(num_users)
    users = gen_biased_rand_ppl(num_users, 0.9)
    initial_op = poll_opinions(users)
    for mc_cycle in range(num_mc_cycles):
        # Randomizing social connections
        graph = link_ppl_rand_graph(users, 3)

        # Resetting users to their original state
        for person in users.items():
            # print(person)
            person[1]['Person'].reset()

        # draw_bias_graph(graph)

        """
        This is all the content that has been generated in the last couples cycles of the algorithm. I don't think we can
        store all of the data, because I ran a test and 10,000^2 posts managed to use up all of my memory.
        If we choose to remove duplicate posts from people's feeds, we can use a decorator on the node, and employ this
        indexing system so that we don't have to keep track of every single post that they have seen in the past
        """
        num_stored_cycles = 3
        store_idx = -1
        all_content = [-1 for i in range(num_stored_cycles)]
        # print(f"all content is\n{all_content}\n(should be empty)'")

        # This will allow us to calculate the site's "revenue" over time
        time_spent_online = []
        # Keeps track of specific timestamps
        start_time = time.time()
        quarter_time = 0
        half_time = 0
        three_quarters_time = 0
        # going through multiple time cycles
        for i in range(num_time_cycles):
            # Useful to have this printout
            if i == num_time_cycles // 4:
                quarter_time = time.time()
                print(f"25% complete, took {quarter_time - start_time}s")
                print(f"all content has length {len(all_content)}, sub-news have lengths {[len(all_content[i]) for i in range(num_stored_cycles)]}")
            elif i == num_time_cycles // 2:
                half_time = time.time()
                print(f"50% complete, took {half_time - quarter_time}")
                print(f"all content has length {len(all_content)}, sub-news have lengths {[len(all_content[i]) for i in range(num_stored_cycles)]}")
            elif i == 3 * num_time_cycles // 4:
                three_quarters_time = time.time()
                print(f"75% complete, took {three_quarters_time - half_time}")
                print(f"all content has length {len(all_content)}, sub-news have lengths {[len(all_content[i]) for i in range(num_stored_cycles)]}")
            elif i == 19 * num_time_cycles // 20:
                print(f"95% complete, took {time.time() - three_quarters_time}")
                print(f"all content has length {len(all_content)}, sub-news have lengths {[len(all_content[i]) for i in range(num_stored_cycles)]}")
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

            # print(f"new content:\n{np.around(new_content, 2)}")
            store_idx += 1
            if store_idx >= num_stored_cycles:
                store_idx = 0
            all_content[store_idx] = new_content

            num_online = 0

            """
            The second time that we iterate through the graph. This time, we'll actually be making predictions about
            what people want to see in their inbox
            """
            for node_tuple in graph.nodes(data=True):
                person = node_tuple[1]['Person']
                if person.get_online():
                    num_online += 1
                # Adding news to their feed (factoring this out so that it's easier to modify later)
                send_news(person, all_content)
                # User goes through their normal routine on the site
                person.cycle()

            time_spent_online.append(num_online)

        print(f"average users on site was {sum(time_spent_online) / len(time_spent_online)}")
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3)
        opinion_dist = poll_opinions(users)
        np_new_opinions = np.array(opinion_dist)
        np_old_opinions = np.array(initial_op)
        print(f"For the original distribution, the the average opinion was {np.round(np.mean(np_old_opinions), 4)} with"
              f" standard deviation {np.round(np.std(np_old_opinions), 4)}.\nFor the distribution at the end of the "
              f"algorithm, the average is {np.round(np.mean(np_new_opinions), 4)} and the standard deviation is "
              f"{np.round(np.std(np_new_opinions), 4)}")
        # Plots the last few hundred steps of the number of people online
        num_steps_to_plot = 300
        if len(time_spent_online) < num_steps_to_plot:
            lin_space = np.arange(len(time_spent_online))
            ax1.plot(lin_space, time_spent_online)
        else:
            lin_space = np.arange(num_steps_to_plot)
            ax1.plot(lin_space, time_spent_online[-num_steps_to_plot:])
        n_bins = min(int(num_users / 5), 30)
        ax2.hist(opinion_dist, density=True, bins=n_bins, range=[0, 1])
        ax3.hist(initial_op, density=True, bins=n_bins, range=[0, 1])
        plt.show()

        print("Current bias graph")
        draw_bias_graph(graph)
        for node_tuple in graph.nodes(data=True):
            person = node_tuple[1]['Person'].reset()
        print("bias graph at beginning of cycle")
        draw_bias_graph(graph)
