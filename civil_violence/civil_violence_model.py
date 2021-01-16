from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector

from civil_violence_agents import Citizen

class CivilViolenceModel(Model):
    """ Civil violence model class """
    def __init__(self,
                 height, width,
                 agent_density, agent_vision,
                 cop_density, cop_vision,
                 initial_legitimacy_l0, max_iter,
                 max_jail_term, active_threshold_t,
                 k, movement=True):
        """
        Create a new civil violence model.

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
        :param movement: Can agent move at end of an iteration
        """

        super().__init__()

        # Initialize Model grid and schedule
        self.height = height
        self.width = width
        self.grid = MultiGrid(self.width, self.height, torus=True)  # Grid or MultiGrid ?
        self.schedule = RandomActivation(self)
        self.max_iter = max_iter
        self.iteration = 0  # Simulation iteration counter
        self.running = True
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

        # Data collection
        self.data_collector = DataCollector(
            model_reporters=self.get_model_reporters(),
            agent_reporters=self.get_agent_reporters()
        )

        unique_id = 0
        for (contents, x, y) in self.grid.coord_iter():
            if self.random.random() < self.agent_density:
                agent = Citizen(
                    unique_id=unique_id, model=self,
                    pos=(x, y), hardship=self.random.random(),
                    legitimacy=self.initial_legitimacy_l0, risk_aversion=self.random.random(),
                    threshold=self.active_threshold_t, vision=self.agent_vision)
                unique_id += 1
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)

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
        """ Dictionary of model reporter names and attributes/funcs """
        return {}

    def get_agent_reporters(self):
        """ Dictionary of agent reporter names and attributes/funcs """
        return {}

    def count_type_citizens(model, condition, exclude_jailed=True):
        """
        Helper method to count agents.
        Cop agents can't disappear from the map, so number of cops can be retrieved from model attributes.
        TODO
        """
        count = 0

        return count