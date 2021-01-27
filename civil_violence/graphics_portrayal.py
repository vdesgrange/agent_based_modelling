from utils import linear_gradient
from cv_constants import State, Shape, Color
from civil_violence_agents import Citizen

# we generate an array of hex values in between start and end hex values
# in order to represent agents with an array of susceptibility values
# in the grid
grad_grievance = linear_gradient("#FFD1D7", "#860110", n=100)['hex']


def get_agent_portrayal(agent):
    """
    Generate a portrayal of the agent (citizen, cop, etc.(
    :param agent: agent to be portrayed
    :return: json-ready dictionary
    """

    portrayal = {
        "Shape": Shape[type(agent).__name__.upper()].value,
        "x": agent.pos[0], "y": agent.pos[1],
        "Filled": "true",
        "Color": Color[agent.state.name].value,
        "r": .8,
        "w": 0.7,
        "h": 0.7,
        "Layer": 0,
        "Agent": agent.unique_id,
    }

    return portrayal


def get_network_portrayal(model):
    """
    Generate a portrayal (JSON-ready dictionary used by the relevant JavaScript code (sigma.js) to draw shapes)
    TODO : Resolve issue with agent that can't be added to NetworkGrid if already on MultiGrid + deepcopy modification.
    TODO : Hide edge when agent jailed
    :param graph: Generated networkx graph representing social network
    :return:
    """

    portrayal = dict()
    portrayal["nodes"] = [
        {
            # Main attributes
            "id": agent.network_node,
            "label": "{}".format(agent.unique_id),
            # Display attributes
            "size": 3,
            "color": Color[agent.state.name].value,
        }
        for agent in model.citizen_list  # Must add agent to NetworkGrid. Problem to be resolved.
    ]

    portrayal["edges"] = [
        {
            "id": edge_id,
            "source": source,
            "target": target,
            # "color": Color.JAILED if model.network_dict[source].state == State.JAILED
            #                          or model.network_dict[target].state == State.JAILED
            # else "#000000"
        }
        for edge_id, (source, target) in enumerate(model.G.edges)
    ]

    return portrayal


def get_grievance_portrayal(agent):

    portrayal = {
        "Shape": "rect",
        "x": agent.pos[0], "y": agent.pos[1],
        "Filled": "true",
        "Color": "#000000",
        "w": 0.7,
        "h": 0.7,
        "Layer": 1,
        "Agent": agent.unique_id,
    }

    if isinstance(agent, Citizen):
        grievance_value = int(agent.grievance * 100)
        portrayal["Color"] = grad_grievance[grievance_value]
        portrayal["Grievance"] = int(agent.grievance * 100)

    return portrayal

