from IPython.display import clear_output
import SALib

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

path = 'archives/saved_data{0}'.format(int(time.time()))

number_of_variables = 6

problem = {
    'num_vars': number_of_variables,
    'names': ['active_threshold_t', 'initial_legitimacy_l0',
              'max_jail_term', 'p', 'agent_vision', 'cop_vision'],
    'bounds': [[0.01, 1], [0.01, 1], [1, 100], [0.01, 0.4], [1, 20], [1, 20]]
}

replicates = 10
max_steps = 200
distinct_samples = 20

model_reporters = {"QUIESCENT": lambda m: m.count_type_citizens("QUIESCENT"),
                   "ACTIVE": lambda m: m.count_type_citizens("ACTIVE"),
                   "JAILED": lambda m: m.count_type_citizens("JAILED"),
                   "OUTBREAKS": lambda m: m.outbreaks}

data = {}
run_data = {}

for i, var in enumerate(problem['names']):
    # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
    samples = np.linspace(*problem['bounds'][i], num=distinct_samples)

    # Keep in mind that max_jail_term should be integers. You will have to change
    # your code to acommodate for this or sample in such a way that you only get integers.
    if var == 'max_jail_term':
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype=int)
    if var == 'agent_vision':
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype=int)
    if var == 'cop_vision':
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype=int)

    configuration = read_configuration()
    model_params = {}
    model_params.update(configuration)  # Overwritten user parameters don't appear in the graphic interface
    model_params.update({'seed': None})

    # print({var: samples})

    batch = BatchRunner(CivilViolenceModel,
                        max_steps=max_steps,
                        iterations=replicates,
                        variable_parameters={var: samples},
                        fixed_parameters=model_params,
                        model_reporters={'All_Data': lambda m: m.datacollector,
                                         "QUIESCENT": lambda m: m.count_type_citizens("QUIESCENT"),
                                         "ACTIVE": lambda m: m.count_type_citizens("ACTIVE"),
                                         "JAILED": lambda m: m.count_type_citizens("JAILED"),
                                         "OUTBREAKS": lambda m: m.outbreaks},  # attempt all
                        # model_reporters=model_reporters,
                        display_progress=True)

    batch.run_all()

    batch_df = batch.get_model_vars_dataframe()
    batch_df = batch_df.drop('All_Data', axis=1)

    data[var] = batch_df
    run_data[var] = batch.get_collector_model()
    # data[var] = batch.get_model_vars_dataframe()


with open(path, 'ab') as f:
    np.save(f, data)

run_path = path+'_run'
with open(run_path, 'ab') as f:
    np.save(f, run_data)

def plot_param_var_conf(ax, df, var, param, i):
    """
    Helper function for plot_all_vars. Plots the individual parameter vs
    variables passed.

    Args:
        ax: the axis to plot to
        df: dataframe that holds the data to be plotted
        var: variables to be taken from the dataframe
        param: which output variable to plot
    """
    x = df.groupby(var).mean().reset_index()[var]
    y = df.groupby(var).mean()[param]

    replicates = df.groupby(var)[param].count()
    err = (1.96 * df.groupby(var)[param].std()) / np.sqrt(replicates)

    ax.plot(x, y, c='k')
    ax.fill_between(x, y - err, y + err)

    ax.set_xlabel(var)
    ax.set_ylabel(param)


def plot_all_vars(df, param):
    """
    Plots the parameters passed vs each of the output variables.

    Args:
        df: dataframe that holds all data
        param: the parameter to be plotted
    """

    f, axs = plt.subplots(number_of_variables, figsize=(7, 10))

    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs[i], df[var], var, param, i)


for param in ('OUTBREAKS', "ACTIVE"):
    plot_all_vars(data, param)
    plt.show()