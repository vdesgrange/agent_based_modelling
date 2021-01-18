import random
import math
import networkx as nx
from mesa import Agent
from constants import Layer, State


class Citizen(Agent):
    """
    A citizen agent, part of the population.
    """

    def __init__(self, unique_id, model, pos, hardship, legitimacy, risk_aversion, threshold, vision, layer=Layer.GRID):
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

        state: current state of the agent (default: Quiescent)
        jail_sentence: current jail sentence of the agent (default: 0)
        neighbors: List of neighbors in agent vision
        empty_cells: List of empty cells in agent vision
        layer: Environment layer of the agent. Due to Mesa implementation based on the idea an agent should
        be only in one network. We must use trick to follow agent on an additional network.
        """

        super().__init__(unique_id, model)

        self.pos = pos
        self.network_node = 0

        self.hardship = hardship
        self.legitimacy = legitimacy
        self.risk_aversion = risk_aversion
        self.threshold = threshold
        self.vision = vision
        self.state = State.QUIESCENT
        self.jail_sentence = 0

        self.neighbors = []
        self.empty_cells = []
        self.layer = layer

    def step(self):
        """
        Citizen agent rules (Epstein 2002 model)
        """

        # NetworkGrid agent should not perform any action. They are only copy of MultiGrid agent.
        if self.layer == Layer.NETWORK:
            return

        # Jailed agent can't perform any action
        if self.jail_sentence:
            self.jail_sentence -= 1
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

        if self.layer == Layer.NETWORK:
            return

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
        Compute the agent's grievence (Epstein 2002 model)
        :return: H(1 - L)
        """
        return self.hardship * (1 - self.legitimacy)

    def get_network_neighbors(self):
        """ TODO Example to retrieve attributes from the network layer"""

        neighbors = nx.all_neighbors(self.model.G, self.network_node)
        for node_id in neighbors:
            print(self.model.network_dict[node_id].unique_id)



class Cop(Agent):
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

    def step(self):
        raise NotImplementedError
