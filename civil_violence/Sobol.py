from SALib.sample import saltelli
from mesa.batchrunner import BatchRunner
from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
import time

from civil_violence_model import CivilViolenceModel
from server import get_user_model_parameters
from utils import read_configuration

replicates = 10
max_steps = 100
distinct_samples = 10

path = 'archives/saved_data_Sobol{0}.npy'.format(int(time.time()))

problem = {
    'num_vars': 3,
    'names': ['active_threshold_t', 'initial_legitimacy_l0',
              'max_jail_term'],
    'bounds': [[0.01, 1], [0.01, 1], [1, 100]]
}

model_reporters = {"QUIESCENT": lambda m: m.count_type_citizens("QUIESCENT"),
                   "ACTIVE": lambda m: m.count_type_citizens("ACTIVE"),
                   "JAILED": lambda m: m.count_type_citizens("JAILED"),
                   "OUTBREAKS": lambda m: m.outbreaks}

# We get all our samples here
param_values = saltelli.sample(problem, distinct_samples)


# READ NOTE BELOW CODE
batch = BatchRunner(CivilViolenceModel,
                    max_steps=max_steps,
                    variable_parameters={name:[] for name in problem['names']},
                    model_reporters=model_reporters)

count = 0
data = pd.DataFrame(index=range(replicates*len(param_values)),
                    columns=['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term'])
data['Run'], data['QUIESCENT'], data['ACTIVE'], data['JAILED'], data['LEGITIMACY'], data['OUTBREAKS'] =\
    None, None, None, None, None, None

for i in range(replicates):
    for vals in param_values:
        # Change parameters that should be integers
        vals = list(vals)
        vals[2] = int(vals[2])
        # print(vals)
        # Transform to dict with parameter names and their values
        variable_parameters = {}
        for name, val in zip(problem['names'], vals):
            variable_parameters[name] = val

        batch.run_iteration(variable_parameters, tuple(vals), count)
        iteration_data = batch.get_model_vars_dataframe().iloc[count]
        iteration_data['Run'] = count # Don't know what causes this, but iteration number is not correctly filled
        data.iloc[count, 0:3] = vals
        data.iloc[count, 3:8] = iteration_data
        count += 1

        # clear_output()
        print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')
        # print(data)


with open(path, 'ab') as f:
    np.save(f, data)