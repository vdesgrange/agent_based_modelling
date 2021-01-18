import networkx as nx
from copy import deepcopy
from mesa.space import NetworkGrid
from constants import Layer

def generate_network(agent_list, p, directed=False, seed=None, graph_type=None):

    if graph_type == "erdos_renyi_graph":
        return generate_erdos_renyi(agent_list, p, directed, seed)

    return generate_erdos_renyi(agent_list, p, directed, seed)  # Default


def generate_erdos_renyi(agent_list, p, directed=False, seed=None):
    """
    Generate a network grid based on Erdos Renyi graph.
    Add as many nodes as there's agents.
    Given that mesa doesn't work with multiple grid, we must use a deep copy on agent list
    and use the copy on the new network.

    :param agent_list: List of agents
    :param p: probability of creating an edge
    :param directed: True if graph is directed
    :param seed: randomization seed
    :return: Mesa network grid
    """

    num_nodes = len(agent_list)
    graph = nx.generators.random_graphs.erdos_renyi_graph(num_nodes, p, seed, directed)
    network_dict = dict()
    # network = NetworkGrid(graph)

    for idx, agent in enumerate(agent_list):
        agent.network_node = idx
        network_dict[idx] = agent

        # new_agent = deepcopy(agent)
        # new_agent.layer = Layer.NETWORK
        # network.place_agent(new_agent, idx)  # Note : if we want to get

    return graph, network_dict
