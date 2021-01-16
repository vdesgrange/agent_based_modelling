from mesa import Agent
import random


class Citizen(Agent):
    """
    A citizen agent, part of the population.
    """

    def __init__(self, unique_id, model, pos, hardship, legitimacy, risk_aversion, threshold, vision):
        """
        Create a new citizen agent.
        :param unique_id: unique id of the agent
        :param model: model to which agent belongs to
        :param pos: position of the agent in the space
        :param hardship: agent's perceived hardship
        :param legitimacy: legitimacy of the central authority
        :param risk_aversion: agent's level risk aversion
        :param threshold: threshold beyond which agent become active
        :param vision: number of cells visible for each direction
        """

        super().__init__(unique_id, model)

        self.pos = pos
        self.hardship = hardship
        self.legitimacy = legitimacy
        self.risk_aversion = risk_aversion
        self.threshold = threshold
        self.vision = vision

        self.neighbors = []
        self.empty_cells = []

    def step(self):
        """ TODO """
        self.update_neighbors()

        if self.model.movement and self.empty_cells:
            new_pos = random.choice(self.empty_cells)
            self.model.grid.move_agent(self, new_pos)

    def update_neighbors(self):
        # Moore = False because we check N/S/E/W
        neighborhood = self.model.grid.get_neighborhood(self.pos, moore=False, radius=self.vision)
        self.neighbors = self.model.grid.get_cell_list_contents(neighborhood)
        self.empty_cells = [c for c in neighborhood if self.model.grid.is_cell_empty(c)]
