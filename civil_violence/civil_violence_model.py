from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from civil_violence_agents import Citizen, Cop
from graph_utils import generate_network, print_network


class CivilViolenceModel(Model):
    """ Civil violence model class """
    def __init__(self,
                 height, width,
                 agent_density, agent_vision,
                 cop_density, cop_vision,
                 initial_legitimacy_l0, max_iter,
                 max_jail_term, active_threshold_t,
                 k, graph_type,
                 p, directed,
                 movement=True, seed=None):
        """
        Create a new civil violence model.
        TODO - This class is not fully implemented

        :param height: Grid height.
        :param width: Grid width.
        :param agent_density: Approximate percentage of cells occupied by citizen agents.
        :param agent_vision: Radius of the agent vision in every direction.
        :param cop_density: Approximate percentage of cells occupied by cops.
        :param cop_vision: Radius of the cop vision in every direction.
        :param initial_legitimacy_l0: Initial legitimacy of the central authority.
        :param max_iter: Maximum number of steps in the simulation.
        :param max_jail_term: Maximal jail term.
        :param active_threshold_t: Threshold where citizen agent became active.
        :param k: Arrest term constant k.
        :param graph_type: Graph used to build network
        :param p: Probability for edge creation
        :param directed: Is graph directed
        :param movement: Can agent move at end of an iteration
        :param seed: random seed

        Additionnal attributes:
            running : is the model running
            iteration : current step of the simulation
            citizen_list : a list storing the citizen agents added to the model.

            grid : A 2D cellular automata representing the real world space environment
            network : A NetworkGrid with as many nodes as (citizen) agents representing the social network.
            Agent in the NetworkGrid are deep copy of agent in the MultiGrid has Mesa implementation is based on
            the usage of a single space. (Example: NetworkGrid place_agent method will change "pos" attribute from agent
            meaning one agent can't be on both MultiGrid and NetworkGrid).
            We maintain a dictionary of agent position instead.

        """

        super().__init__()

        # === Initialize attributes ===
        self.seed = seed
        self.random.seed(self.seed)

        # Initialize Model grid and schedule
        self.height = height
        self.width = width
        self.grid = MultiGrid(self.width, self.height, torus=True)  # Grid or MultiGrid ?
        self.schedule = RandomActivation(self)
        self.max_iter = max_iter
        self.iteration = 0  # Simulation iteration counter
        self.movement = movement

        # Set Model main attributes
        self.max_jail_term = max_jail_term
        self.active_threshold_t = active_threshold_t
        self.initial_legitimacy_l0 = initial_legitimacy_l0
        self.k = k

        self.agent_density = agent_density
        self.agent_vision = agent_vision
        self.cop_density = cop_density
        self.cop_vision = cop_vision

        self.citizen_list = []
        self.cop_list = []

        # === Set Data collection ===
        self.data_collector = DataCollector(
            model_reporters=self.get_model_reporters(),
            agent_reporters=self.get_agent_reporters()
        )

        # === Initialize environment ===

        # Add agents to the model
        unique_id = 0
        for (contents, x, y) in self.grid.coord_iter():
            random_x = self.random.random()
            if random_x < self.agent_density:
                agent = Citizen(
                    unique_id=unique_id, model=self,
                    pos=(x, y), hardship=self.random.random(), susceptibility=self.random.random(), 
                    influence=self.random.random(), expression_intensity=self.random.random(),
                    legitimacy=self.initial_legitimacy_l0, risk_aversion=self.random.random(),
                    threshold=self.active_threshold_t, vision=self.agent_vision)

                unique_id += 1
                self.citizen_list.append(agent)
                self.grid.place_agent(agent, (x, y))  # Place agent in the MultiGrid
                self.schedule.add(agent)
            elif random_x < (self.agent_density + self.cop_density):
                agent = Cop(
                    unique_id=unique_id, model=self,
                    pos=(x, y), vision=self.cop_vision)

                unique_id += 1
                self.cop_list.append(agent)
                self.grid.place_agent(agent, (x, y))  # Place agent in the MultiGrid
                self.schedule.add(agent)

        # Generate a social network composed of every population agents

        self.G, self.network_dict = generate_network(self.citizen_list, graph_type, p, directed, seed)
        print_network(self.G, self.network_dict)  # Print the network. Can be commented.

        self.running = True
        self.data_collector.collect(self)

    def step(self):
        """ One step in agent-based model simulation """
        self.schedule.step()
        self.data_collector.collect(self)
        self.iteration += 1

        if self.iteration > self.max_iter:
            self.running = False

    def get_model_reporters(self):
        """ TODO Dictionary of model reporter names and attributes/funcs """
        return {}

    def get_agent_reporters(self):
        """ TODO Dictionary of agent reporter names and attributes/funcs """
        return {}

    def count_type_citizens(model, condition, exclude_jailed=True):
        """
        Helper method to count agents.
        Cop agents can't disappear from the map, so number of cops can be retrieved from model attributes.
        TODO
        """
        count = 0

        return count
