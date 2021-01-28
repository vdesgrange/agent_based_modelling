from mesa.batchrunner import BatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import time
from constants import GraphType, Color

from civil_violence_model import CivilViolenceModel
from utils import read_configuration

# network_types = [GraphType.ERDOS_RENYI.name, GraphType.BARABASI_ALBERT.name, GraphType.WATTS_STROGATZ.name]
graph_type=GraphType.ERDOS_RENYI.name
path = 'archives/saved_data_experiment_1_{0}{1}'.format(int(time.time()), graph_type)

replicates = 40
max_steps = 200

model_reporters = {"QUIESCENT": lambda m: m.count_type_citizens("QUIESCENT"),
                   "ACTIVE": lambda m: m.count_type_citizens("ACTIVE"),
                   "JAILED": lambda m: m.count_type_citizens("JAILED"),
                   "OUTBREAKS": lambda m: m.outbreaks}

# data = {}
# run_data = {}

configuration = read_configuration()
model_params = {}
model_params.update(configuration)  # Overwritten user parameters don't appear in the graphic interface
model_params.update({'seed': None})
model_params['graph_type']=GraphType.ERDOS_RENYI.name
model_params['max_iter']=max_steps
print(model_params)

batch = BatchRunner(CivilViolenceModel,
                    max_steps=max_steps,
                    iterations=replicates,
                    fixed_parameters=model_params,
                    model_reporters={'All_Data': lambda m: m.datacollector,
                                     "QUIESCENT": lambda m: m.count_type_citizens("QUIESCENT"),
                                     "ACTIVE": lambda m: m.count_type_citizens("ACTIVE"),
                                     "JAILED": lambda m: m.count_type_citizens("JAILED"),
                                     "OUTBREAKS": lambda m: m.outbreaks},  # attempt all
                    display_progress=True)

batch.run_all()

batch_df = batch.get_model_vars_dataframe()
batch_df = batch_df.drop('All_Data', axis=1)

data = batch_df
run_data = batch.get_collector_model()

with open(path, 'ab') as f:
    np.save(f, data)

run_path = path+'_run'
with open(run_path, 'ab') as f:
    np.save(f, run_data)
