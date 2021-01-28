import time
import pandas as pd
import numpy as np
from SALib.sample import saltelli
from tqdm import tqdm
from multiprocessing import Pool, cpu_count
from mesa.batchrunner import BatchRunner
from civil_violence_model import CivilViolenceModel
from utils import *


def sobol_analysis_no_network(problem):
    replicates = 4
    max_steps = 150
    distinct_samples = 100

    path = 'archives/saved_data_sobol_{0}.npy'.format(int(time.time()))

    model_reporters = {"QUIESCENT": compute_quiescent,
                       "ACTIVE": compute_active,
                       "JAILED": compute_jailed,
                       "OUTBREAKS": compute_outbreaks,
                       "LEGITIMACY": compute_legitimacy}

    # We get all our samples here
    param_values = saltelli.sample(problem, distinct_samples)
    data = pd.DataFrame(index=range(replicates*len(param_values)),
                        columns=['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term'])

    data['Run'], data['QUIESCENT'], data['ACTIVE'], data['JAILED'], data['OUTBREAKS'], data['LEGITIMACY'] = \
        None, None, None, None, None, None

    column_order = ['Run', 'QUIESCENT', 'ACTIVE', 'JAILED', 'OUTBREAKS', 'LEGITIMACY']
    available_processors = cpu_count()
    print("Sobol MP will use {} processors.".format(available_processors))
    pool = Pool(available_processors)

    run_iter_args = enumerate([[max_steps, model_reporters, list(v)] for _ in range(replicates) for v in param_values])
    print("Number steps is {}. Starting ...".format(len(param_values) * replicates))

    with tqdm((len(param_values) * (replicates)), disable=False) as pbar:
        for count, vals, iteration_data in pool.imap_unordered(_mp_function, run_iter_args):
            data.iloc[count, 0:3] = vals
            data.loc[count, column_order] = iteration_data.loc[0, column_order]
            print(f'{count / (len(param_values) * (replicates)) * 100:.2f}% done')

            if count % 200 == 0:
                path_tmp = 'archives/progress_data_sobol_{0}.npy'.format(int(time.time()))
                with open(path_tmp, 'ab') as f:
                    np.save(f, data)
                    print("Progress saved in the file {:s}".format(path_tmp))

    pbar.update()

    # Close multi-processing
    pool.close()

    path = 'archives/saved_data_sobol_{0}.npy'.format(int(time.time()))
    with open(path, 'ab') as f:
        np.save(f, data)
        print("Results saved in file {:s}".format(path))

    return data


def _mp_function(input):
    count, iter_args = input

    max_steps = iter_args[0]
    model_reporters = iter_args[1]
    vals = iter_args[2]

    vals[2] = int(vals[2])

    variable_parameters = {}
    names = ['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term']
    for name, val in zip(names, vals):
        variable_parameters[name] = val  # dictionary

    batch = BatchRunner(CivilViolenceModel,
                        max_steps=max_steps,
                        variable_parameters={name: [] for name in names},
                        model_reporters=model_reporters)

    batch.run_iteration(variable_parameters, tuple(vals), count)
    iteration_data = batch.get_model_vars_dataframe()
    iteration_data['Run'] = count  # Don't know what causes this, but iteration number is not correctly filled

    return count, vals, iteration_data


def sobol_main():
    problem = {
        'num_vars': 3,
        'names': ['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term'],
        'bounds': [[0.01, 1], [0.01, 1], [1, 100]]
    }

    sobol_analysis_no_network(problem)


if __name__ == '__main__':
    sobol_main()