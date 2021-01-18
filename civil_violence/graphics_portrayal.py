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


def get_network_portrayal(G):
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
            "id": node_id,
            "label": None,
            # Display attributes
            "size": 3,
            "color": "#CC0000",
        }
        for (node_id, agents) in G.nodes.data("agent")  # Must add agent to NetworkGrid. Problem to be resolved.
    ]

    portrayal["edges"] = [
        {
            "id": edge_id,
            "source": source,
            "target": target,
            "color": "#000000"
        }
        for edge_id, (source, target) in enumerate(G.edges)
    ]
    # if ((source.state is not State.JAILED) or (target.state is not State.JAILED) )
    return portrayal