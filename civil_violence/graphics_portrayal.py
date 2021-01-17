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
            "size": 3 if agents else 1,
            "color": "#CC0000",
        }
        for (node_id, agents) in G.nodes.data("agent")
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

    return portrayal