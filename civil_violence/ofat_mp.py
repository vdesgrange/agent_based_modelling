import time
import numpy as np
import matplotlib.pyplot as plt
from batchrunner_mp import BatchRunnerMP
from civil_violence_model import CivilViolenceModel
from utils import *


def sensitive_analysis_no_network(problem, replicates=10, max_steps=200, distinct_samples=20, nr_processes=None):
    """
    One-factor-at-a-time (OFAT) sensitivity analysis of civil violence model with network (no bias)
    Work with multiprocessing
    :param problem: details of the variable parameters
    :param replicates: number of replicates to be run
    :param max_steps: Maximal number of steps of the simulations
    :param distinct_samples: Number of samples per variables
    :param nr_processes: number of CPUs to be used. If None, by default all available CPUs will be used.
    """

    data = {}
    run_data = {}

    for i, var in enumerate(problem['names']):
        # Get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples)

        # max_jail_term, agent_vision and cop_vision must be integers.
        integer_param = ['max_jail_term', 'agent_vision', 'cop_vision']
        if var in integer_param:
            samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype=int)

        # Get default configuration
        configuration = read_configuration('./configurations/ofat_no_network.json')
        model_params = {}
        model_params.update(configuration)  # Overwritten user parameters don't appear in the graphic interface
        model_params.update({'seed': None})

        # BatchRunnerMP used is a local modified version of the BatchRunnerMP class provided by mesa.
        # It handle the multiprocessing issue which prohibite
        batch = BatchRunnerMP(CivilViolenceModel,
                            nr_processes=nr_processes,
                            max_steps=max_steps,
                            iterations=replicates,
                            variable_parameters={var: samples},
                            fixed_parameters=model_params,
                            model_reporters={'All_Data': compute_datacollector,  # multiprocessing pool can't handle
                                             "QUIESCENT": compute_quiescent,     # lambda function.
                                             "ACTIVE": compute_active,
                                             "JAILED": compute_jailed,
                                             "OUTBREAKS": compute_outbreaks,
                                             "INFLUENCERS": compute_influencers,
                                             "LEGITIMACY": compute_legitimacy},
                            display_progress=True)

        batch.run_all()

        batch_df = batch.get_model_vars_dataframe()
        batch_df = batch_df.drop('All_Data', axis=1)

        data[var] = batch_df
        run_data[var] = batch.get_collector_model()

        # Uncomment to save data per parameter.
        # path = 'archives/progress_data_ofat_{0}_{1}.npy'.format(var, int(time.time()))
        # with open(path, 'ab') as f:
        #     np.save(f, data)

    # Save final data
    path = 'archives/saved_data_ofat_{0}.npy'.format(int(time.time()))
    with open(path, 'ab') as f:
        np.save(f, data)

    run_path = path+'_run'
    with open(run_path, 'ab') as f:
        np.save(f, run_data)

    return data, run_data


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

    f, axs = plt.subplots(problem['num_vars'], figsize=(5, 10))
    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs[i], df[var], var, param, i)


def ofat_main():
    """
    Main function of the one-factor-at-a-time sensitivity analysis.
    """
    problem = {
        'num_vars': 5,
        'names': ['active_threshold_t', 'initial_legitimacy_l0',
                  'max_jail_term', 'agent_vision', 'cop_vision'],
        'bounds': [[0.01, 1], [0.01, 1], [1, 100], [1, 20], [1, 20]]
    }

    data, run_data = sensitive_analysis_no_network(problem, 10, 200, 20, None)
    for param in ("OUTBREAKS", "ACTIVE", "QUIESCENT", "JAILED", "INFLUENCERS", "LEGITIMACY"):
        plot_all_vars(problem, data, param)
        plt.show()


if __name__ == '__main__':
    ofat_main()
