import random
import math
from mesa import Agent
from constant_variables import State, HardshipConst


class Citizen(Agent):
    """
    A citizen agent, part of the population.
    """

    def __init__(self, unique_id, model, pos, hardship, susceptibility, influence, expression_intensity, 
        legitimacy, risk_aversion, threshold, vision, jailable=True):
        """
        Create a new citizen agent.

        Attributes:
        :param unique_id: unique id of the agent
        :param model: model to which agent belongs to
        :param pos: position of the agent in the space
        :param hardship: agent's perceived hardship, sum of endogenous and contagious hardship
        :param susceptibility: How susceptible this agent is to contagious hardship
        :param influence: How influentual this agent is to other agents
        :param expression_intensity: How strongly this agent expresses their hardship
        :param legitimacy: legitimacy of the central authority
        :param risk_aversion: agent's level risk aversion
        :param threshold: threshold beyond which agent become active
        :param vision: number of cells visible for each direction (N/S/E/W)
        :param state: Model state of the agent
        :param jailable: Flag that indicates if an agent can get arrested

        Other attributes:
        hardship_endo: endogenous hardship
        hardship_cont: contagious hardship
        network_node : agent's node_id in the graph representing the social network
        state: current state of the agent (default: Quiescent)
        jail_sentence: current jail sentence of the agent (default: 0)
        neighbors: List of neighbors in agent vision
        empty_cells: List of empty cells in agent vision
        """

        super().__init__(unique_id, model)
        random.seed(model.seed)

        self.pos = pos  # Position in MultiGrid space
        self.network_node = 0  # Position in graph

        self.hardship = hardship  # Set equal to U(0, 1) for initialization
        self.hardship_endo = hardship
        self.hardship_cont = 0
        self.susceptibility = susceptibility
        self.influence = influence
        self.expression_intensity = expression_intensity
        self.legitimacy = legitimacy
        self.risk_aversion = risk_aversion
        self.threshold = threshold
        self.vision = vision
        self.jail_sentence = 0
        self.grievance = self.get_grievance()

        self.jailable = jailable
        self.influencer = False

        self.network_neighbors = []  # Neighbors in social network
        self.neighbors = []  # Neighbors in MultiGrid space
        self.empty_cells = []  # Empty cells around the agent in MultiGrid space

        self.state = State.ACTIVE if threshold == 0 else State.QUIESCENT

    def step(self):
        """
        Citizen agent rules (Epstein 2002 model)
        """

        # Jailed agent can't perform any action
        # After sentence resets state and contagious hardship
        if self.jail_sentence:
            self.jail_sentence -= 1

            if self.jail_sentence == 0:
                self.state = State.QUIESCENT  # Jailed agent returns quiescent
                self.hardship_cont = 0
                self.model.add_jailed(self)
            return

        self.hardship = self.update_hardship()
        self.get_network_neighbors()
        self.update_neighbors()  # Should we run this at each turn instead of retrieving the neighbors when necessary ?

        self.grievance = self.get_grievance()
        rule_a = self.grievance - self.get_net_risk() > self.threshold
        if self.state is State.QUIESCENT and rule_a:
            self.state = State.ACTIVE
        elif self.state is State.ACTIVE and not rule_a:
            self.state = State.QUIESCENT

        # Move agent in the 2D Grid
        if self.model.movement and self.empty_cells:
            new_pos = random.choice(self.empty_cells)
            self.model.grid.move_agent(self, new_pos)

    def update_neighbors(self):
        """
        Keep track of neighbours and empty surrounding cells.
        """

        # Moore = False because we check N/S/E/W
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=False, radius=self.vision)
        self.neighbors = self.model.grid.get_cell_list_contents(neighborhood)
        self.empty_cells = [c for c in neighborhood if self.model.grid.is_cell_empty(c)]

    def get_arrest_probability(self):
        """
        Compute the arrest probability P of the agent (expanded from Epstein 2002 model)
        round of (C_v / (A_v + 1) is suggested to have more active agents in the model.
        Removing it might make difficult actual outbreaks.

        :return: 1 - exp(-k * C_v / int(A_v + 1))
        """
        c_v = sum(isinstance(n, Cop) for n in self.neighbors)
        a_v = sum(isinstance(n, Citizen) and n.state is State.ACTIVE for n in self.neighbors)
        cop_to_agent_ratio = int(c_v / (a_v + 1))  # This modification is suggested to get active agent more easily
        return 1 - math.exp(-1 * self.model.k * cop_to_agent_ratio)  # Rounding to min integer

    def get_net_risk(self):
        """
        Compute the agent's net risk N (Epstein 2002 model)
        :return: R * P
        """
        return self.risk_aversion * self.get_arrest_probability()

    def get_grievance(self):
        """
        Compute the agent's grievance (Epstein 2002 model).
        Also works with the ABEC-model described in Huang et al. (2018) since only hardship is calculated differently.
        :return: H(1 - L)
        """
        return self.hardship * (1 - self.model.legitimacy)

    def update_hardship(self):
        """
        Hardship in the ABEC-model consists of endogenous hardship (U(0, 1) as the Epstein model)
        and contagious hardship which is updated at every timestep.

        Updates the contagious hardship and the perceived hardship.
        """
        
        if self.hardship < 1:
            received_hardship = self.get_received_hardship()
            self.hardship_cont += received_hardship

        hardship = self.hardship_cont + self.hardship_endo

        # Ensure hardship has a maximum value of 1
        if hardship > 1:
            return 1
        else:
            return hardship

    def get_received_hardship(self, hardship_params=HardshipConst):
        """
        Calculates the received contagious hardship of an agent by its neighbors.
        Is a product of various endo- and exogenous parameters.
        Transmission_rate is a parameter we can consider setting fixed because it is not of importance to our
        project, but removing it will increase the received hardship.
        Timestep, or delta_time, can also be considered fixed in this discrete time model.
        Distance is a parameter that is more or less incorporated in NetworkX, so perhaps set this fixed as well.
        :param hardship_params: default values
        """
        # Fixed values for parameters
        distance = hardship_params.DISTANCE.value
        timestep = hardship_params.TIME_STEP.value
        transmission_rate = hardship_params.TRANSMISSION_RATE.value
        hardship = hardship_params.HARDSHIP.value

        for n in self.model.G.neighbors(self.network_node):  # Network neighbors
            agent = self.model.network_dict[n]  # Get agent at the neighbor node
            if agent.state == State.ACTIVE:  # If the agent is active state
                hardship += (distance * timestep * transmission_rate * 
                    agent.influence * agent.expression_intensity * self.susceptibility)

        return hardship

    def set_influencer(self, connections, threshold):
        """
        Determine if civilian agent is an influencer
        """
        if connections > threshold:
            self.influencer = True
        else: 
            self.influencer = False

    def get_network_neighbors(self):
        """
        Retrieve neighbors to this agent in the social network.
        """

        self.network_neighbors = (list(self.model.G.neighbors(self.network_node)))


class Cop(Agent):
    """
    Create a new law enforcement officer agent.
    """

    def __init__(self, unique_id, model, pos, vision):
        """
        Create a new law enforcement officer agent.
        :param unique_id: unique id of the agent
        :param model: model to which agent belongs to
        :param pos: position of the agent in the space
        :param vision: number of cells visible for each direction (N,S,E,W)
        """

        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.model = model
        self.pos = pos
        self.vision = vision
        self.state = State.COP

        # Data collector fix
        self.hardship = None
        self.hardship_cont = None
        self.grievance = None
        self.degree = None

        self.neighbors = []  # Neighbors in MultiGrid space
        self.empty_cells = []  # Empty cells around the agent in MultiGrid space

    def step(self):
        """
        Inspect vision and arrest a random agent. Move there
        """
        self.update_neighbors()
        active_neighbors = []
        
        # Check for all active neighbors in vision
        for agent in self.neighbors:
            if type(agent).__name__.upper() == 'CITIZEN' \
                    and agent.state is State.ACTIVE \
                    and agent.jail_sentence == 0 \
                    and agent.jailable:
                active_neighbors.append(agent)

        # If there are any active arrest one randomly and move there
        if active_neighbors:
            arrestee = random.choice(active_neighbors)
            sentence = random.randint(1, self.model.max_jail_term)
            arrestee.jail_sentence = sentence
            arrestee.state = State.JAILED
            new_pos = arrestee.pos
            self.model.jailings_list[0] += 1

            if sentence > 0:
                self.model.remove_agent_grid(arrestee)
            if self.model.movement:
                self.model.grid.move_agent(self, new_pos)

        # No active citizens, move to random empty cell
        elif self.model.movement and self.empty_cells:
            new_pos = random.choice(self.empty_cells)
            self.model.grid.move_agent(self, new_pos)

    def update_neighbors(self):
        """
        Create a list of neighbors & empty neighbor cells
        """
        # Moore = False because we check N/S/E/W
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=False, radius=self.vision)
        self.neighbors = self.model.grid.get_cell_list_contents(neighborhood)
        self.empty_cells = [c for c in neighborhood if self.model.grid.is_cell_empty(c)]
