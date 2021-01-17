from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid  # For MultiGrid visualization
from mesa.visualization.modules import NetworkModule  # For NetworkGrid visualization

from civil_violence_model import CivilViolenceModel
from graphics_portrayal import get_agent_portrayal, get_network_portrayal


def get_user_model_parameters():
    """
    Get parameters of the agent-based model
    Default parameters based on Run 5 of Epstein type 1 civil violence model.
    :return: A dictionary of model parameters
    """
    return {
        "agent_density": UserSettableParameter("slider", "Agent Density", .7, 0., 1., step=.001,
                                                 description="Initial percentage of citizen in population"),
        "cop_density": UserSettableParameter("slider", "Cop Density", .074, 0, 1, step=.001,
                                             description="Initial percentage of cops in population"),
        "agent_vision": UserSettableParameter("slider", "Agent Vision", 7, 0, 10,
                                              description="Number of patches visible to citizens"),
        "cop_vision": UserSettableParameter("slider", "Cop Vision", 7, 0, 10,
                                            description="Number of patches visible to cops"),
        "initial_legitimacy_l0": UserSettableParameter("slider", "Initial Central authority legitimacy", .8, 0, 1,
                                                       step=.001,
                                                       description="Global parameter: Central authority legitimacy"),
        "active_threshold_t": UserSettableParameter("slider", "Active Threshold", .01, 0, 1, step=.001,
                                                  description="Threshold that agent's Grievance must exceed Net Risk to go active"),
        "max_jail_term": UserSettableParameter("slider", "Max Jail Term", 1000, 0, 1000,
                                               description="Maximum number of steps that jailed citizens stay in")
    }


def get_visualization_elements():

    # 2D cellular automata representing real-world environment
    canvas_element = CanvasGrid(get_agent_portrayal, grid_width=40, grid_height=40, canvas_width=500, canvas_height=500)

    # Graph representing agent's social network
    # network_element = NetworkModule(get_network_portrayal, canvas_width=500, canvas_height=500, library='sigma')

    return [canvas_element]


def run():
    """
    Run the mesa server
    """

    model_params = {
        "width": 40,
        "height": 40,
        "max_iter": 1000,
        "max_jail_term": 1000,
        "k": 2.3,
    }
    model_params.update(get_user_model_parameters())

    server = ModularServer(
        CivilViolenceModel,
        get_visualization_elements(),
        name="Civil violence with network model",
        model_params=model_params
    )

    server.port = 8521
    server.launch()


if __name__ == '__main__':
    run()
