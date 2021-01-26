import networkx as nx
from mesa.visualization.modules import NetworkModule

from constant_variables import GraphType


class NetworkModuleExtended(NetworkModule):
    """
    NetworkModuleExtended is exactly NetworkModule class.
    Except it will provide the model as parameters instead of the graph G from model.G.
    This extended version is used to vizualise social network between agents
    while going around the limitation of mesa (implemented with the idea of using only one Space object).
    """
    def render(self, model):
        return self.portrayal_method(model)


def generate_network(agent_list, graph_type, p, p_ws, directed=False, seed=None):
    """
    Generate a network based on the provided parameters
    TODO : If  the signature for all graph is the same, this could be improved as we might not need switch

    :param agent_list: List of agents to be added to the network
    :param p: Probability for edge creation
    :param directed: True if directed, False if undirected
    :param seed: Indicator of random number generation state
    :param graph_type: constants to select a type of Graph.
    :return:
    """

    if graph_type == GraphType.ERDOS_RENYI.name:
        return generate_erdos_renyi(agent_list, p, directed, seed)

    if graph_type == GraphType.BARABASI_ALBERT.name:
        return generate_barabasi_albert(agent_list, p, seed)

    if graph_type == GraphType.WATTS_STROGATZ.name:
        return generate_watts_strogatz(agent_list, p, p_ws, seed)

    # Default - no network
    no_graph = nx.Graph()
    network_dict = dict()
    for idx, agent in enumerate(agent_list):
        no_graph.add_node(idx)
        agent.network_node = idx
        network_dict[agent.network_node] = agent

    return no_graph, network_dict


def generate_erdos_renyi(agent_list, p, directed=False, seed=None):
    """
    Generate an Erdos Renyi graph. Add as many nodes as there's agents.
    :param agent_list: List of agents (citizen)
    :param p: probability of creating an edge
    :param directed: True if graph is directed
    :param seed: randomization seed
    :return: networkx graph and dictionnary mapping graph node to agent reference.
    """

    num_nodes = len(agent_list)
    graph = nx.generators.random_graphs.erdos_renyi_graph(num_nodes, p, seed, directed)
    network_dict = dict()

    agent_number = 0
    for agent in agent_list:
        # Set the localisation of the agent in the social network
        agent.network_node = list(graph.nodes)[agent_number]
        network_dict[agent.network_node] = agent
        agent_number += 1
    return graph, network_dict


def generate_barabasi_albert(agent_list, p, seed=None):
    """
    Generate an Erdos Renyi graph. Add as many nodes as there's agents.
    :param agent_list: List of agents (citizen)
    :param p: probability of creating an edge
    :param seed: randomization seed
    :return: networkx graph and dictionnary mapping graph node to agent reference.
    """

    num_nodes = len(agent_list)
    m = int((p*num_nodes-1)/2)
    graph = nx.generators.random_graphs.barabasi_albert_graph(num_nodes, m, seed)
    network_dict = dict()

    agent_number = 0
    for agent in agent_list:
        # Set the localisation of the agent in the social network
        agent.network_node = list(graph.nodes)[agent_number]
        network_dict[agent.network_node] = agent
        agent_number += 1
    return graph, network_dict


def generate_watts_strogatz(agent_list, p, p_ws, seed=None):
    """
    Generate an Erdos Renyi graph. Add as many nodes as there's agents.
    :param agent_list: List of agents (citizen)
    :param p: probability of creating an edge
    :param p_ws: probability of rewiring each edge
    :param seed: randomization seed
    :return: networkx graph and dictionnary mapping graph node to agent reference.
    """

    num_nodes = len(agent_list)
    k = int((num_nodes-1)*p)
    graph = nx.generators.random_graphs.watts_strogatz_graph(num_nodes, k, p_ws, seed)
    network_dict = dict()

    agent_number = 0
    for agent in agent_list:
        # Set the localisation of the agent in the social network
        agent.network_node = list(graph.nodes)[agent_number]
        network_dict[agent.network_node] = agent
        agent_number += 1
    return graph, network_dict


def print_network(G, network_dict):
    """
    Simple tool to print the population agent's network graph
    :param G: a graph from networkx module
    :param network_dict: map between node id and agent's
    """

    print("######### Network #########")

    for n in list(G.nodes):
        print("======")
        neighbours = nx.all_neighbors(G, n)
        agent = network_dict[n]
        print("{} Agent {} localized at Node {} connected to :".format(str(type(agent)), agent.unique_id, n))
        for m in neighbours:
            print("-- Agent {}".format(m))

    print("###########################")