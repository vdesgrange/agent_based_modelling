import random
import math
from mesa import Agent

from constants import State


class Citizen(Agent):
    """
    A citizen agent, part of the population.
    """

    def __init__(self, unique_id, model, pos, hardship, legitimacy, risk_aversion, threshold, vision):
        """
        Create a new citizen agent.

        Attributes:
        :param unique_id: unique id of the agent
        :param model: model to which agent belongs to
        :param pos: position of the agent in the space
        :param hardship: agent's perceived hardship
        :param legitimacy: legitimacy of the central authority
        :param risk_aversion: agent's level risk aversion
        :param threshold: threshold beyond which agent become active
        :param vision: number of cells visible for each direction (N/S/E/W)

        network_node : agent's node_id in the graph representing the social network
        state: current state of the agent (default: Quiescent)
        jail_sentence: current jail sentence of the agent (default: 0)
        neighbors: List of neighbors in agent vision
        empty_cells: List of empty cells in agent vision
        """

        super().__init__(unique_id, model)
        random.seed(model.seed)  # Should not be required given it's set in the server.

        self.pos = pos  # Position in MultiGrid space
        self.network_node = 0  # Position in graph

        self.hardship = hardship
        self.legitimacy = legitimacy
        self.risk_aversion = risk_aversion
        self.threshold = threshold
        self.vision = vision
        self.state = State.QUIESCENT
        self.jail_sentence = 0

        self.neighbors = []  # Neighbors in MultiGrid space
        self.empty_cells = []  # Empty cells around the agent in MultiGrid space

    def step(self):
        """
        Citizen agent rules (Epstein 2002 model)
        """

        # Jailed agent can't perform any action
        if self.jail_sentence:
            self.jail_sentence -= 1
            if self.jail_sentence == 0:
                self.state = State.QUIESCENT # Jailed agent returns quiescent
            return

        self.get_network_neighbors()

        self.update_neighbors()  # Should we run this at each turn instead of retrieving the neighbors when necessary ?

        rule_a = self.get_grievance() - self.get_net_risk() > self.threshold
        if self.state is State.QUIESCENT and rule_a:
            self.state = State.ACTIVE
        elif self.state is State.ACTIVE and not rule_a:
            self.state = State.QUIESCENT

        # Move agent in the 2D Grid (Layer 0)
        if self.model.movement and self.empty_cells:
            new_pos = random.choice(self.empty_cells)
            self.model.grid.move_agent(self, new_pos)

    def update_neighbors(self):
        """
        Store surrounding neighborhood object and
        :return:
        """

        # Moore = False because we check N/S/E/W
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=False, radius=self.vision)
        self.neighbors = self.model.grid.get_cell_list_contents(neighborhood)
        self.empty_cells = [c for c in neighborhood if self.model.grid.is_cell_empty(c)]

    def get_arrest_probability(self):
        """
        Compute the arrest probability P of the agent (Epstein 2002 model)
        :return: 1 - exp(-k * C_v / (A_v + 1))
        """
        c_v = sum(isinstance(n, Cop) for n in self.neighbors)
        a_v = sum(isinstance(n, Citizen) and n.state is State.ACTIVE for n in self.neighbors)
        return 1 - math.exp(-1 * self.model.k * c_v / (a_v + 1))

    def get_net_risk(self):
        """
        Compute the agent's net risk N (Epstein 2002 model)
        TODO : extends with Jail term: N = R * P * J^alpha
        :return: R * P
        """
        return self.risk_aversion * self.get_arrest_probability()

    def get_grievance(self):
        """
        Compute the agent's grievance (Epstein 2002 model)
        :return: H(1 - L)
        """
        return self.hardship * (1 - self.legitimacy)

    def get_network_neighbors(self):
        """ TODO Example to retrieve attributes from the network layer"""

        # neighbors = nx.all_neighbors(self.model.G, self.network_node)
        # for node_id in neighbors:
        #     print(self.model.network_dict[node_id].unique_id)

        pass


class Cop(Agent):
    """
    Check local vision and arrest active citizen
    """

    def __init__(self, unique_id, model, pos, vision):
        """
        Create a new law enforcement officer agent.
        :param unique_id: unique id of the agent
        :param model: model to which agent belongs to
        :param pos: position of the agent in the space
        :param vision: number of cells visible for each direction
        """

        super().__init__(unique_id, model)
        self.unique_id = unique_id
        self.model = model
        self.pos = pos
        self.vision = vision
        self.state = State.COP

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
                    and agent.jail_sentence == 0:
                active_neighbors.append(agent)

        # If there are any active arrest one randomly and move there
        if active_neighbors:
            arrestee = random.choice(active_neighbors)
            sentence = random.randint(0, self.model.max_jail_term)
            arrestee.jail_sentence = sentence
            arrestee.state = State.JAILED
            new_pos = arrestee.pos
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
