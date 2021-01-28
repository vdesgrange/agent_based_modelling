import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from SA import number_of_variables


problem = {
    'num_vars': 6,
    'names': ['active_threshold_t', 'initial_legitimacy_l0',
              'max_jail_term', 'p', 'agent_vision', 'cop_vision'],
    'bounds': [[0, 1], [0, 1], [0, 100], [0.01, 0.5], [4, 8], [4, 8]]
}

def load_plot_archive():
    file_path = [
        # './archives/saved_data1611750187.npy',
        './archives/saved_data_local_SA.npy',
    ]

    # print(dir(data))
    # print(vars(data))
    for path in file_path:
        with open(path, 'rb') as f:
            data = np.load(f, allow_pickle=True)[()]

    print(data.keys())
    param ='OUTBREAKS'
    plot_all_vars(data, param)
    plt.show()

    # for param in ('OUTBREAKS', "ACTIVE"):
    #     plot_all_vars(data, param)
    #     plt.show()

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

    # print(param)
    # print(var)
    # print(df.groupby(var)[param].count())
    replicates = df.groupby(var)[param].count()
    err = (1.96 * df.groupby(var)[param].std()) / np.sqrt(replicates)
    # print(df["active_threshold_t"])
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

    f, axs = plt.subplots(6, figsize=(3, 5))

    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs[i], df[var], var, param, i)


load_plot_archive()