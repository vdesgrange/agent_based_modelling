import networkx as nx
from copy import deepcopy
from mesa.space import NetworkGrid


def generate_network(agent_list, p, directed=False, seed=None, graph_type=None):

    if graph_type == "erdos_renyi_graph":
        return generate_erdos_renyi(agent_list, p, directed, seed)

    return generate_erdos_renyi(agent_list, p, directed, seed)  # Default


def generate_erdos_renyi(agent_list, p, directed=False, seed=None):
    """
    Generate a network grid based on Erdos Renyi graph.
    Add as many nodes as there's agents
    :param agent_list: List of agents
    :param p: probability of creating an edge
    :param directed: True if graph is directed
    :param seed: randomization seed
    :return: Mesa network grid
    """
    twin_list = deepcopy(agent_list)

    num_nodes = len(agent_list)
    graph = nx.generators.random_graphs.erdos_renyi_graph(num_nodes, p, seed, directed)
    network = NetworkGrid(graph)

    for idx, agent in enumerate(twin_list):
        agent.network_node = idx
        network.place_agent(agent, idx)

    return graph, network
