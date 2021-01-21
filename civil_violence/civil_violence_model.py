from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import matplotlib.pyplot as plt

from civil_violence_agents import Citizen, Cop
from constants import State
from graph_utils import generate_network, print_network

from figure import create_fig

class CivilViolenceModel(Model):
    """ Civil violence model class """
    def __init__(self,
                 height, width,
                 agent_density, agent_vision,
                 cop_density, cop_vision,
                 initial_legitimacy_l0, max_iter,
                 max_jail_term, active_threshold_t,
                 k, graph_type,
                 p, p_ws, directed,
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
            influencer_list : a list storing the citizien agents that are influencers

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
        self.legitimacy = initial_legitimacy_l0
        self.k = k
        self.graph_type = graph_type

        self.agent_density = agent_density
        self.agent_vision = agent_vision
        self.cop_density = cop_density
        self.cop_vision = cop_vision

        self.citizen_list = []
        self.cop_list = []
        self.influencer_list = []
        self.jailings_list = [0, 0, 0, 0]

        # === Set Data collection ===
        self.datacollector = DataCollector(
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

        self.G, self.network_dict = generate_network(self.citizen_list, graph_type, p, p_ws, directed, seed)
        print_network(self.G, self.network_dict)  # Print the network. Can be commented.

        # With network in place, set the influencers. Change the parameter value to determine how
        # many connections a node needs to be considered an influencer.
        self.set_influencers(inf_threshold=10)

        # Create the graph show the frequency of degrees for the nodes
        create_fig(self.G.degree, draw=False) # Set =True when we want to draw a figure

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """ One step in agent-based model simulation """
        self.schedule.step()
        self.datacollector.collect(self)
        self.iteration += 1
        self.update_legitimacy()
        self.datacollector.collect(self)

        if self.iteration > self.max_iter:
            self.running = False

        # for agent in self.influencer_list:
        #     print('Agent ', agent.unique_id, ' is an influencer ')

    def update_legitimacy(self):
        """
        Compute legitimacy (Epstein Working Paper 2001)
        """
        self.jailings_list[3] = self.jailings_list[2]
        self.jailings_list[2] = self.jailings_list[1]
        self.jailings_list[1] = self.jailings_list[0]/(self.count_type_citizens("ACTIVE")+1)  # +1 otherwise it can divide by zero
        self.jailings_list[0] = 0
        self.legitimacy = self.initial_legitimacy_l0 * (1 - self.jailings_list[1] - self.jailings_list[2] ** 2 - self.jailings_list[3] ** 3)
        if self.legitimacy <= 0:
            self.legitimacy = 0
        # print(self.initial_legitimacy_l0)
        # print(self.legitimacy)


    def get_model_reporters(self):
        """ Dictionary of model reporter names and attributes/funcs """
        return {"QUIESCENT": lambda m: self.count_type_citizens("QUIESCENT"),
                "ACTIVE": lambda m: self.count_type_citizens("ACTIVE"),
                "JAILED": lambda m: self.count_type_citizens("JAILED"),
                "LEGITIMACY": lambda m: self.legitimacy}

    def get_agent_reporters(self):
        """ TODO Dictionary of agent reporter names and attributes/funcs
            TODO Doesn't work the way it should"""

        return {"Grievance": lambda a: getattr(a, 'grievance', None),
                "Hardship": lambda a: getattr(a, 'hardship', None)}

    def count_type_citizens(self, state_req):
        """
        Helper method to count agents.
        Cop agents can't disappear from the map, so number of cops can be retrieved from model attributes.
        """
        count = 0
        for agent in self.citizen_list:
            if type(agent).__name__.upper() == 'COP':
                continue
            if agent.jail_sentence and state_req == 'JAILED':
                count += 1
            else:
                if agent.state is State.ACTIVE and state_req == 'ACTIVE':
                    count += 1
                elif agent.state == State.QUIESCENT and state_req == 'QUIESCENT':
                    count += 1
        return count

    def remove_agent_grid(self, agent):
        """
        Removes an agent from the grid.
        """
        self.grid.remove_agent(agent)

    def add_jailed(self, agent):
        """
        If the sentence of a jailed agent is over, place him back on a
        random empty cell in the grid.
        """
        if (len(self.grid.empties) == 0):
            raise Exception("There are no empty cells.")
        new_pos = self.random.choice(list(self.grid.empties))
        self.grid.place_agent(agent, new_pos)
        # print(agent.unique_id, " was placed back on the grid at pos: ", new_pos) # TEST

    def set_influencers(self, inf_threshold=10):
        """
        If an agent in the network is connected to a large amount of nodes, this agent can
        be considered an influencer and receives a corresponding tag.
        """
        for agent in self.citizen_list:
            if len(list(self.G.neighbors(agent.network_node))) > inf_threshold:
                agent.set_influencer()
                self.influencer_list.append(agent)

    def remove_influencer(self):
        """
        Function that removes a random agent with the influencer tag from the gird. Gives 
        manual control over the model to evaluate the influence of influencers.
        """
        to_remove = self.random.choice(self.influencer_list)
        self.grid.remove_agent(to_remove)
        self.influencer_list.remove(to_remove)
        self.citizen_list.remove(to_remove)
        print(agent.unique_id, ' was an influencer and has been removed.')
