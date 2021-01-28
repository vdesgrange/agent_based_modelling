import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from SALib.sample import saltelli
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from mesa.batchrunner import BatchRunner
from batchrunner_mp import BatchRunnerMP
from civil_violence_model import CivilViolenceModel
from utils import *


def sobol_analysis_no_network(problem):
    replicates = 20
    max_steps = 200
    distinct_samples = 20

    path = 'archives/saved_data_sobol_{0}.npy'.format(int(time.time()))

    model_reporters = {"QUIESCENT": compute_quiescent,
                       "ACTIVE": compute_active,
                       "JAILED": compute_jailed,
                       "OUTBREAKS": compute_outbreaks,
                       "LEGITIMACY": compute_legitimacy}

    # We get all our samples here
    param_values = saltelli.sample(problem, distinct_samples)
    data = pd.DataFrame(index=range(replicates*len(param_values)),
                        columns=['active_threshold_t', 'initial_legitimacy_l0',
                                 'max_jail_term', 'agent_vision', 'cop_vision'])

    data['Run'], data['QUIESCENT'], data['ACTIVE'], data['JAILED'], data['OUTBREAKS'] =\
        None, None, None, None, None

    available_processors = cpu_count()
    pool = Pool(available_processors)

    combinations = enumerate([list(v) for _ in range(replicates) for v in param_values])

    with tqdm(replicates, disable=False) as pbar:
        for count, vals, iteration_data in pool.imap_unordered(_mp_function, combinations):
            data.iloc[count, 0:5] = vals
            data.iloc[count, 5:10] = iteration_data
            pbar.update()

    pool.close()

    with open(path, 'ab') as f:
        np.save(f, data)


    # batch = BatchRunner(CivilViolenceModel,
    #                     max_steps=max_steps,
    #                     variable_parameters={name: [] for name in problem['names']},
    #                     model_reporters=model_reporters)

    # for i in range(replicates):
    #     for vals in param_values:
    #         # Change parameters that should be integers
    #         vals = list(vals)
    #         vals[2] = int(vals[2])
    #         vals[3] = int(vals[3])
    #         vals[4] = int(vals[4])
    #
    #         # Transform to dict with parameter names and their values
    #         variable_parameters = {}
    #         for name, val in zip(problem['names'], vals):
    #             variable_parameters[name] = val
    #
    #         batch.run_iteration(variable_parameters, tuple(vals), count)
    #         iteration_data = batch.get_model_vars_dataframe().iloc[count]
    #         iteration_data['Run'] = count  # Don't know what causes this, but iteration number is not correctly filled
    #         data.iloc[count, 0:5] = vals
    #         data.iloc[count, 5:10] = iteration_data
    #         count += 1
    #
    #         print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')

    # Close multi-processing

    return data


def _mp_function(input):
    count, vals = input

    vals[2] = int(vals[2])
    vals[3] = int(vals[3])
    vals[4] = int(vals[4])

    variable_parameters = {}
    names = ['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term', 'agent_vision', 'cop_vision']
    for name, val in zip(names, vals):
        variable_parameters[name] = val  # dictionary

    batch = BatchRunner(CivilViolenceModel,
                        max_steps=max_steps,
                        variable_parameters={name: [] for name in names},
                        model_reporters=model_reporters)

    batch.run_iteration(variable_parameters, tuple(vals), count)
    iteration_data = batch.get_model_vars_dataframe().iloc[count]
    iteration_data['Run'] = count  # Don't know what causes this, but iteration number is not correctly filled

    print("Counter : ", count)
    return count, vals, iteration_data


def sobol_main():
    problem = {
        'num_vars': 5,
        'names': ['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term', 'agent_vision', 'cop_vision'],
        'bounds': [[0.01, 1], [0.01, 1], [1, 100], [1, 20], [1, 20]]
    }

    data = sobol_analysis_no_network(problem)


if __name__ == '__main__':
    sobol_main()