from constants import State, Layer, Shape, Color


def get_agent_portrayal(agent):
    if agent is None or agent.layer is not Layer.GRID:
        return

    portrayal = {
        "Shape": Shape[type(agent).__name__.upper()].value,
        "x": agent.pos[0], "y": agent.pos[1],
        "Filled": "true",
        "Color": Color[agent.state.name].value,
        "r": .8,
        "Layer": 0,
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
            "label": None,
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
            "color": Color.JAILED if model.network_dict[source].state == State.JAILED
                                     or model.network_dict[target].state == State.JAILED
            else "#000000"
        }
        for edge_id, (source, target) in enumerate(model.G.edges)
    ]

    return portrayal