
AGENT_COLOR = "#0066CC"


def get_agent_portrayal(agent):
    """ TODO """
    if agent is None:
        return

    portrayal = {
        "Shape": "circle",
        "x": agent.pos[0], "y": agent.pos[1],
        "Filled": "true",
        "Color": AGENT_COLOR,
        "r": .8,
        "Layer": 0,
    }

    return portrayal
