# %matplotlib inline

import time
import numpy as np
import networkx as nx
import pandas as pd
import SALib
import matplotlib.pyplot as plt

from mesa.batchrunner import BatchRunner
from IPython.display import clear_output
from SALib.sample import saltelli
from SALib.analyze import sobol
from itertools import combinations

from civil_violence_model import CivilViolenceModel
from server import get_user_model_parameters
from utils import read_configuration

path = 'archives/saved_data{0}.npy'.format(int(time.time()))


def ofat_barabasi_albert_analysis(problem):
    """
    One factor at a time sensitivity analysis of civil violence model regarding
    network type parameters.
    Analyse the network transmission
    """

    max_steps = 20  # Simulation number of steps
    replicates = 3  # Number of simulations # 10
    distinct_samples = 20

    model_reporters = {
        "QUIESCENT": lambda m: m.count_type_citizens("QUIESCENT"),
        "ACTIVE": lambda m: m.count_type_citizens("ACTIVE"),
        "JAILED": lambda m: m.count_type_citizens("JAILED"),
        "OUTBREAKS": lambda m: m.outbreaks,
        "INFLUENCERS": lambda m: len(m.influencer_list),
        "CLUSTERING": lambda m: nx.average_clustering(m.G)
    }

    agent_reporters = {
        "HARDSHIP_CONT": lambda a: getattr(a, 'hardship_cont', None),
        "GRIEVANCE": lambda a: getattr(a, 'grievance', None),
        "DEGREE": lambda a: getattr(a, ['model', 'G'], None).degree(a.network_node)
    }

    data = {}

    for i, var in enumerate(problem['names']):
        # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples)

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
                            model_reporters=model_reporters,
                            agent_reporters=agent_reporters,
                            display_progress=True)
        batch.run_all()

        data[var] = batch.get_model_vars_dataframe()

    with open(path, 'ab') as f:
        np.save(f, data)

    return data


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


def plot_all_vars(problem, df, param):
    """
    Plots the parameters passed vs each of the output variables.

    Args:
        df: dataframe that holds all data
        param: the parameter to be plotted
    """

    f, axs = plt.subplots(3, figsize=(7, 10))

    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs[i], df[var], var, param, i)


if __name__ == '__main__':
    problem = {
        'num_vars': 3,
        'names': ['p', 'inf_threshold'],
        'bounds': [[0.01, 1], [10, 200]]
    }
    
    data = ofat_barabasi_albert_analysis(problem)
    for param in ('OUTBREAKS', "ACTIVE"):
        plot_all_vars(problem, data, param)
        plt.show()