import networkx as nx
import matplotlib.pyplot as plt
import json
import random
from datetime import datetime
from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from civil_violence_agents import Citizen, Cop
from constant_variables import State, GraphType
from graph_utils import generate_network, print_network
from figure import create_fig, run_analysis
from utils import *


class CivilViolenceModel(Model):
    """ Civil violence model class """
    def __init__(self,
                 max_iter=200,
                 height=40, width=40,
                 agent_density=0.7, agent_vision=7,
                 active_agent_density=0.01,
                 cop_density=0.04, cop_vision=7,
                 inf_threshold=40, tackle_inf=False,
                 k=2.3, graph_type=GraphType.BARABASI_ALBERT.name,
                 p=0.1, p_ws=0.1,
                 directed=False, max_jail_term=30,
                 active_threshold_t=0.1, initial_legitimacy_l0=0.82,
                 movement=True, seed=None):
        """
        Create a new civil violence model.

        :param max_iter: Maximum number of steps in the simulation.
        :param height: Grid height.
        :param width: Grid width.
        :param agent_density: Approximate percentage of cells occupied by citizen agents.
        :param agent_vision: Radius of the agent vision in every direction.
        :param active_agent_density: Enforce initial percentage of cells occupied by active agents.
        :param cop_density: Approximate percentage of cells occupied by cops.
        :param cop_vision: Radius of the cop vision in every direction.
        :param initial_legitimacy_l0: Initial legitimacy of the central authority.
        :param inf_threshold: Amount of nodes that need to be connected before an agent is considered an influencer.
        :param tackle_inf: Remove influencer when outbreaks starting
        :param max_jail_term: Maximal jail term.
        :param active_threshold_t: Threshold where citizen agent became active.
        :param k: Arrest term constant k.
        :param graph_type: Graph used to build network
        :param p: Probability for edge creation
        :param directed: Is graph directed
        :param movement: Can agent move at end of an iteration
        :param seed: random seed

        Additional attributes:
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

        # =============================
        # === Initialize attributes ===
        # =============================

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
        self.active_agent_density = active_agent_density
        self.cop_density = cop_density
        self.cop_vision = cop_vision
        self.inf_threshold = inf_threshold

        self.citizen_list = []
        self.cop_list = []
        self.influencer_list = []
        self.jailings_list = [0, 0, 0, 0]
        self.outbreaks = 0
        self.outbreak_now = 0
        self.outbreak_influencer_now = False
        self.tackle_inf = tackle_inf

        date = datetime.now()
        self.path = f'output/{self.graph_type}_{date.month}_{date.day}_{date.hour}_{date.minute}_'

        # === Set Data collection ===
        self.datacollector = DataCollector(
            model_reporters=self.get_model_reporters(),
            agent_reporters=self.get_agent_reporters()
        )

        # ==============================
        # === Initialize environment ===
        # ==============================

        # Add agents to the model
        unique_id = 0
        for (contents, x, y) in self.grid.coord_iter():
            random_x = self.random.random()
            if random_x < self.agent_density:
                # Add agents
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

            elif random_x < (self.agent_density + self.active_agent_density):
                # Enforce an initial proportion of active agents
                agent = Citizen(
                    unique_id=unique_id, model=self,
                    pos=(x, y), hardship=self.random.random(), susceptibility=self.random.random(),
                    influence=self.random.random(), expression_intensity=self.random.random(),
                    legitimacy=self.initial_legitimacy_l0, risk_aversion=self.random.random(),
                    threshold=0, vision=self.agent_vision)

                unique_id += 1
                self.citizen_list.append(agent)
                self.grid.place_agent(agent, (x, y))  # Place agent in the MultiGrid
                self.schedule.add(agent)

            elif random_x < (self.agent_density + self.active_agent_density + self.cop_density):
                # Add law enforcement officer
                agent = Cop(
                    unique_id=unique_id, model=self,
                    pos=(x, y), vision=self.cop_vision)

                unique_id += 1
                self.cop_list.append(agent)
                self.grid.place_agent(agent, (x, y))  # Place agent in the MultiGrid
                self.schedule.add(agent)

        # Generate a social network composed of every civilian agents
        self.G, self.network_dict = generate_network(self.citizen_list, graph_type, p, p_ws, directed, seed)
        # print_network(self.G, self.network_dict)  # Uncomment to print the network.

        # With network in place, set the influencers.
        # Change the parameter value to determine how many connections a node needs to be considered an influencer.
        self.set_influencers(self.inf_threshold)

        # Create the graph show the frequency of degrees for the nodes
        create_fig(self.G.degree, draw=False)  # Set draw=True to draw a figure

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        One step in agent-based model simulation
        """

        self.schedule.step()
        self.iteration += 1
        self.update_legitimacy()

        self.outbreak_score_monitoring()
        self.datacollector.collect(self)

        # Save initial values
        if self.iteration == 1:
            self.save_initial_values(save=False)

        # Stop the model after a certain amount of iterations.
        if self.iteration > self.max_iter:
            self.save_data(save=False)
            self.running = False

    def outbreak_score_monitoring(self):
        if self.tackle_inf:
            if self.count_type_citizens("ACTIVE") > 30 and not self.outbreak_influencer_now:
                self.jail_influencer()
                self.outbreak_influencer_now = True

            if self.count_type_citizens("ACTIVE") < 30:
                self.outbreak_influencer_now = False

        # Count amount of outbreaks
        if self.count_type_citizens("ACTIVE") > 50 and self.outbreak_now == 0:
            self.outbreaks += 1  # Total number of outbreak
            self.outbreak_now = 1  # Indicate if outbreak now

        if self.count_type_citizens("ACTIVE") < 50:
            self.outbreak_now = 0

    def save_data(self, save=True):

        if save is not False:
            df_end = self.datacollector.get_agent_vars_dataframe()
            name = self.path + 'run_values.csv'
            df_end.to_csv(name)
        else:
            pass

    def save_initial_values(self, save=False):
        
        if save is not False:
            dictionary_data = {
                'agent_density': self.agent_density,
                'agent_vision': self.agent_vision,
                'active_agent_density': self.active_agent_density,
                'cop_density': self.cop_density,
                'initial_legitimacy_l0': self.initial_legitimacy_l0,
                'inf_threshold': self.inf_threshold,
                'max_iter': self.max_iter,
                'max_jail_term': self.max_jail_term,
                'active_threshold_t': self.active_threshold_t,
                'k': self.k,
                'graph_type': self.graph_type,
            }
            
            name = self.path + 'ini_values.json'
            a_file = open(name, "w")
            json.dump(dictionary_data, a_file)
            a_file.close()
        else:
            pass


    def update_legitimacy(self):
        """
        Compute legitimacy (Epstein Working Paper 2001)
        """
        self.jailings_list[3] = self.jailings_list[2]
        self.jailings_list[2] = self.jailings_list[1]
        self.jailings_list[1] = self.jailings_list[0]/(self.count_type_citizens("ACTIVE")+ self.count_type_citizens("QUIESCENT"))  # +1 otherwise it can divide by zero
        self.jailings_list[0] = 0
        self.legitimacy = self.initial_legitimacy_l0 * (1 - self.jailings_list[1] - self.jailings_list[2] ** 2 - self.jailings_list[3] ** 3)
        if self.legitimacy <= 0:
            self.legitimacy = 0
        # print(self.initial_legitimacy_l0)
        # print(self.legitimacy)


    def get_model_reporters(self):
        """
        Dictionary of model reporter names and attributes/funcs
        Reference to functions instead of lambda are provided to handle multiprocessing case.
        Multiprocessing pool cannot directly handle lambda.
        """
        return {"QUIESCENT": compute_quiescent,
                "ACTIVE": compute_active,
                "JAILED": compute_active,
                "LEGITIMACY": compute_legitimacy,
                "INFLUENCERS": compute_influencers,
                "OUTBREAKS": compute_outbreaks}

    def get_agent_reporters(self):
        """
        Dictionary of agent reporter names and attributes/funcs
        """

        return {"Grievance": lambda a: getattr(a, 'grievance', None),
                "Hardship": lambda a: getattr(a, 'hardship', None),
                "State": lambda a: getattr(a, 'state', None),
                "Legitimacy": lambda m: self.legitimacy,
                "Influencer": lambda a: getattr(a, 'influencer', None),
                "N_connections": lambda a: getattr(a, 'network_neighbors', None),
                "InfluencePi": lambda a: getattr(a, 'influence', None)}

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
        Un-jail an agent
        If the sentence of a jailed agent is over, place him back on a random empty cell in the grid.
        """

        if len(self.grid.empties) == 0:
            raise Exception("There are no empty cells.")

        new_pos = self.random.choice(list(self.grid.empties))
        self.grid.place_agent(agent, new_pos)

    def set_influencers(self, inf_threshold=150):
        """
        If an agent in the network is connected to a large amount of nodes, this agent can
        be considered an influencer and receives a corresponding tag.
        """
        for agent in self.citizen_list:
            agent.set_influencer(len(list(self.G.neighbors(agent.network_node))), inf_threshold)
            if agent.influencer:
                self.influencer_list.append(agent)

    def remove_influencer(self):
        """
        Removes a random agent with the influencer tag from the grid.
        Gives manual control over the model to evaluate the influence of influencers.
        """
        if self.influencer_list:
            for i in range(len(self.influencer_list)):
                to_remove = self.random.choice(self.influencer_list)
                if to_remove.pos: # Check if influencer is jailed.
                    self.grid.remove_agent(to_remove)
                self.influencer_list.remove(to_remove)
                self.citizen_list.remove(to_remove)
                self.schedule.remove(to_remove)
                self.G.remove_node(to_remove.network_node)

    def jail_influencer(self):
        """
        Jail a random agent with the influencer tag from the grid.
        Gives manual control over the model to evaluate the influence of influencers.
        """
        if self.influencer_list:
            for i in range(len(self.influencer_list)):
                arrestee = self.random.choice(self.influencer_list)
                if arrestee.state == State.JAILED: # Check if influencer is jailed.
                    continue
                sentence = random.randint(1, self.max_jail_term)
                arrestee.jail_sentence = sentence
                arrestee.state = State.JAILED
                self.jailings_list[0] += 1
                if sentence > 0:
                    self.remove_agent_grid(arrestee)

                print(arrestee.unique_id, ' was an influencer and has been jailed.')
