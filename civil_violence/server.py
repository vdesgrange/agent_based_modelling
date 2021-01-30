import random

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.batchrunner import BatchRunner
from mesa.visualization.modules import CanvasGrid, ChartModule, PieChartModule

from civil_violence_model import CivilViolenceModel
from constant_variables import GraphType, Color
from graph_utils import NetworkModuleExtended  # For NetworkGrid visualization
from graphics_portrayal import get_agent_portrayal, get_network_portrayal, get_grievance_portrayal
from utils import read_configuration


def get_user_model_parameters():
    """
    Get parameters of the agent-based model
    Default parameters based on Run 5 of Epstein type 1 civil violence model.
    :return: A dictionary of model parameters
    """
    return {
        "agent_density": UserSettableParameter("slider", "Agent Density", .7, 0., 1., step=.001,
                                                 description="Initial percentage of citizen in population"),
        "active_agent_density": UserSettableParameter("slider", "Active agent Density", .1, 0., 1., step=.001,
                                               description="Initial percentage of active citizen in population"),
        "cop_density": UserSettableParameter("slider", "Cop Density", .04, 0, 1, step=.001,
                                             description="Initial percentage of cops in population"),
        "agent_vision": UserSettableParameter("slider", "Agent Vision", 7, 0, 10,
                                              description="Number of patches visible to citizens"),
        "cop_vision": UserSettableParameter("slider", "Cop Vision", 7, 0, 10,
                                            description="Number of patches visible to cops"),
        "initial_legitimacy_l0": UserSettableParameter("slider", "Initial Central authority legitimacy", .8, 0, 1,
                                                       step=.01,
                                                       description="Global parameter: Central authority legitimacy"),
        "active_threshold_t": UserSettableParameter("slider", "Active Threshold", .1, 0, 1, step=.01,
                                                  description="Threshold that agent's Grievance must exceed Net Risk to go active"),
        "max_jail_term": UserSettableParameter("slider", "Max Jail Term", 1000, 0, 1000,
                                               description="Maximum number of steps that jailed citizens stay in"),
        "inf_threshold": UserSettableParameter("slider", "Influencer threshold", 150, 0, 150, 
                                                description="Amount of nodes that need to be connected to consider agents influencers."),
        "removal_step": UserSettableParameter("slider", "Iteration of influencer removal", 0, 0, 100, step=5,
                                                description="Iteration at which a random influencer is removed from the model."),
        # "removal_step": UserSettableParameter("choice", "Removel of influencers", value=False,
        #                                       choices=[False, True]),
        "graph_type": UserSettableParameter("choice", "GraphType",  value=GraphType.BARABASI_ALBERT.name,
                                              choices=["NONE", GraphType.ERDOS_RENYI.name, GraphType.BARABASI_ALBERT.name, GraphType.WATTS_STROGATZ.name])
    }


def get_visualization_elements(model_paramsl, show_network=False):

    # 2D cellular automata representing real-world environment
    canvas_element = CanvasGrid(
        get_agent_portrayal,
        grid_width=model_paramsl['width'], grid_height=model_paramsl['height'],
        canvas_width=500, canvas_height=500)

    grievance_element = CanvasGrid(
        get_grievance_portrayal,
        grid_width=model_paramsl['width'], grid_height=model_paramsl['height'],
        canvas_width=500, canvas_height=500)


    # Graph representing agent's social network
    network_element = NetworkModuleExtended(get_network_portrayal, canvas_width=500, canvas_height=500, library='sigma')

    # Chart for amount of agents during the run
    agents_state_chart = ChartModule([{"Label": "QUIESCENT", "Color": Color['QUIESCENT'].value},
                                      {"Label": "ACTIVE", "Color": Color['ACTIVE'].value},
                                      {"Label": "JAILED", "Color": Color['JAILED'].value}], 100, 270)

    grievance_chart = ChartModule([{"Label": "LEGITIMACY", "Color": Color['QUIESCENT'].value},
                                   # {"Label": "Hardship", "Color": Color['ACTIVE'].value}
                                   ], 50, 135)

    # outbreak_chart = ChartModule([{"Label": "OUTBREAKS", "Color": Color['QUIESCENT'].value},
    #                                # {"Label": "Hardship", "Color": Color['ACTIVE'].value}
    #                                ], 50, 135)

    pie_chart = PieChartModule([{"Label": "QUIESCENT", "Color": Color['QUIESCENT'].value},
                                {"Label": "ACTIVE", "Color": Color['ACTIVE'].value},
                                {"Label": "JAILED", "Color": Color['JAILED'].value}], 200, 500)

    elements = [canvas_element, grievance_element, agents_state_chart, pie_chart, grievance_chart]
    if show_network:
        elements.insert(1, network_element)

    return elements


def run(configuration, seed=None):
    """
    Run the mesa server
    :param configuration: configuration used by the model.
    :param seed: random seed. By default None.
    """
    """
    to get results for multiple iterations, run underlying code and add this to default.json in configurations:  
    "inf_threshold": 50,
    "removal_step": 50,
    "active_threshold_t": 0.5,
    "graph_type": "GraphType.ERDOS_RENYI.name" 
    """

    #batch_run = BatchRunner(CivilViolenceModel, fixed_parameters = config, iterations = 10)
    #batch_run.run_all()
    #data = batch_run.get_model_vars_dataframe()
    #data.head()


    random.seed(seed)

    model_params = get_user_model_parameters()

    # By updating model_params with configuration after getting the user settable parameters,
    # it let us provide fixed values for our model which won't be overwritten by the user choice.
    # Just remove attribute from the configuration file to get user interface back.
    model_params.update(configuration) # Overwritten user parameters don't appear in the graphic interface
    model_params.update({'seed': seed})


    server = ModularServer(
        CivilViolenceModel,
        get_visualization_elements(model_params, show_network=True),
        name="Civil violence with network model",
        model_params=model_params
    )
    print(model_params)

    server.port = 8521
    server.launch()


if __name__ == '__main__':
    config = read_configuration()
    run(config, None)



