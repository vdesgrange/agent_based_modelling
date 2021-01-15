from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from civil_violence_model import CivilViolenceModel


def get_manual_model_parameters():
    """
    Get parameters of the agent-based model
    Default parameters based on Run 5 of Epstein type 1 civil violence model.
    :return: A dictionary of model parameters
    """
    return {
        "agent_density": UserSettableParameter("slider", "Agent Density", 70, 0, 100,
                                                 description="Initial percentage of citizen in population"),
        "cop_density": UserSettableParameter("slider", "Cop Density", 7.4, 0, 100,
                                             description="Initial percentage of cops in population"),
        "agent_vision": UserSettableParameter("slider", "Agent Vision", 7, 0, 10,
                                              description="Number of patches visible to citizens"),
        "cop_vision": UserSettableParameter("slider", "Cop Vision", 7, 0, 10,
                                            description="Number of patches visible to cops"),
        "initial_legitimacy_l0": UserSettableParameter("slider", "Initial Central authority legitimacy", 80, 0, 100,
                                                       description="Global parameter: Central authority legitimacy"),
        "active_threshold_t": UserSettableParameter("slider", "Active Threshold", 10, 0, 100,
                                                  description="Threshold that agent's Grievance must exceed Net Risk to go active"),
        "max_jail_term": UserSettableParameter("slider", "Max Jail Term", 1000, 0, 1000,
                                               description="Maximum number of steps that jailed citizens stay in")
    }


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
    model_params.update(get_manual_model_parameters())

    server = ModularServer(CivilViolenceModel, [], name="Civil violence with network model", model_params=model_params)

    server.port = 8521
    server.launch()


if __name__ == '__main__':
    run()
