from civil_violence_agents import Citizen, QUIESCENT, ACTIVE, JAILED

COLOR_SET = {
    QUIESCENT: "#138AF2",
    ACTIVE: "#AB05F2",
    JAILED: "#FFFFFF",
}

SHAPE_SET = {
    "Citizen": "circle",
    "Cop": "circle"
}


def get_agent_portrayal(agent):
    """ TODO """
    if agent is None:
        return

    portrayal = {
        "Shape": SHAPE_SET[type(agent).__name__],
        "x": agent.pos[0], "y": agent.pos[1],
        "Filled": "true",
        "Color": COLOR_SET[agent.state],
        "r": .8,
        "Layer": 0,
     }

    return portrayal
