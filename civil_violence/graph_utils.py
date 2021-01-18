import networkx as nx
from mesa.visualization.modules import NetworkModule


class NetworkModuleExtended(NetworkModule):
    """
    NetworkModuleExtended is exactly NetworkModule class.
    Except it will provide the model as parameters instead of the graph G from model.G.
    This extended version is used to vizualise social network between agents
    while going around the limitation of mesa (implemented with the idea of using only one Space object).
    """
    def render(self, model):
        return self.portrayal_method(model)


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

    for idx, agent in enumerate(agent_list):
        agent.network_node = idx
        network_dict[idx] = agent

    return graph, network_dict
