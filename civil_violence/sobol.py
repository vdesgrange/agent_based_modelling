import time
import pandas as pd
import numpy as np
from SALib.sample import saltelli
from mesa.batchrunner import BatchRunner
from civil_violence_model import CivilViolenceModel

replicates = 2
max_steps = 100
distinct_samples = 2

path = 'archives/saved_data_Sobol{0}.npy'.format(int(time.time()))

number_of_variables = 5

problem = {
    'num_vars': number_of_variables,
    'names': ['active_threshold_t', 'initial_legitimacy_l0',
              'max_jail_term', 'agent_vision', 'cop_vision'],
    'bounds': [[0.01, 1], [0.01, 1], [1, 100], [1, 20], [1, 20]]
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
                    columns=['active_threshold_t', 'initial_legitimacy_l0',
                             'max_jail_term', 'agent_vision', 'cop_vision'])
data['Run'], data['QUIESCENT'], data['ACTIVE'], data['JAILED'], data['OUTBREAKS'] = \
    None, None, None, None, None

for i in range(replicates):
    for vals in param_values:
        # Change parameters that should be integers
        vals = list(vals)
        vals[2] = int(vals[2])
        vals[3] = int(vals[3])
        vals[4] = int(vals[4])
        # print(vals)
        # Transform to dict with parameter names and their values
        variable_parameters = {}
        for name, val in zip(problem['names'], vals):
            variable_parameters[name] = val

        batch.run_iteration(variable_parameters, tuple(vals), count)
        iteration_data = batch.get_model_vars_dataframe().iloc[count]
        iteration_data['Run'] = count # Don't know what causes this, but iteration number is not correctly filled
        data.iloc[count, 0:5] = vals
        data.iloc[count, 5:10] = iteration_data
        count += 1

        # clear_output()
        print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')
        # print(data)


with open(path, 'ab') as f:
    np.save(f, data)