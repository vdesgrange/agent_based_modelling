from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from civil_violence_model import CivilViolenceModel


def get_model_parameters():
    """
    Get parameters of the agent-based model
    :return: A dictionary of model parameters
    """
    return {}


def run():
    """
    Run the mesa server
    """
    model_params = get_model_parameters()
    server = ModularServer(CivilViolenceModel, [], name="Civil violence with network model", model_params=model_params)

    server.port = 8521
    server.launch()


if __name__ == '__main__':
    run()
