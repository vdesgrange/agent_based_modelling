from IPython.display import clear_output
import SALib

# %matplotlib inline
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

path = 'archives/saved_data{0}.npy'.format(int(time.time()))

problem = {
    'num_vars': 3,
    'names': ['active_threshold_t', 'initial_legitimacy_l0',
              'max_jail_term'],
    'bounds': [[0, 1], [0, 1], [0, 100], [0.01, 0.5], [4, 8], [4, 8]]
}

replicates = 5
max_steps = 200
distinct_samples = 5

model_reporters = {"QUIESCENT": lambda m: m.count_type_citizens("QUIESCENT"),
                   "ACTIVE": lambda m: m.count_type_citizens("ACTIVE"),
                   "JAILED": lambda m: m.count_type_citizens("JAILED")}

data = {}

for i, var in enumerate(problem['names']):
    # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
    samples = np.linspace(*problem['bounds'][i], num=distinct_samples)

    configuration = read_configuration()
    model_params = {}
    model_params.update(configuration)  # Overwritten user parameters don't appear in the graphic interface
    model_params.update({'seed': None})

    batch = BatchRunner(CivilViolenceModel,
                        max_steps=max_steps,
                        iterations=replicates,
                        variable_parameters={var: samples},
                        fixed_parameters=model_params,
                        model_reporters=model_reporters,
                        display_progress=True)

    batch.run_all()

    data[var] = batch.get_model_vars_dataframe()


with open(path, 'ab') as f:
    np.save(f, data)

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

    f, axs = plt.subplots(3, figsize=(7, 10))

    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs[i], df[var], var, param, i)


for param in ('ACTIVE', 'JAILED'):
    plot_all_vars(data, param)
    plt.show()