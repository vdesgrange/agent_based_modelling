import numpy as np
import matplotlib.pyplot as plt


x_labels = dict({
    "active_threshold_t": "Active threshold",
    "initial_legitimacy_l0": "Initial legitimacy",
    "max_jail_term": "Max jail term",
    "agent_vision": "Citizen vision",
    "cop_vision": "Cop vision",
})

y_labels = dict({
    "OUTBREAKS": "Number of outbreaks",
    "ACTIVE": "Number of active citizens",
    "QUIESCENT": "Number of quiescent citizens",
    "JAILED": "Number of jailed citizens",
    "INFLUENCERS": "Number of influencers",
    "LEGITIMACY": "Central authority legitimacy"
})


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

    x_label = x_labels[var]
    y_label = y_labels[param]

    ax.tick_params(axis='both', which='major', labelsize=6)
    ax.set_xlabel(x_label, size=7)

    if i == 2:
        ax.set_ylabel(y_label, size=9)


def plot_all_vars(problem, df, param):
    """
    Plots the parameters passed vs each of the output variables.

    Args:
        problem: details of the data processed for each parameters
        df: dataframe that holds all data
        param: the parameter to be plotted
    """

    f, axs = plt.subplots(5, figsize=(3, 5), dpi=300)

    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs[i], df[var], var, param, i)


def load_plot_archive(problem, file_paths):
    """
    Utility to load one-factor-at-a-time sensitivity analysis archived data.
    Running sensitivity analysis takes a long time, so results are saved in archived files.
    In this file, the loaded data are plotted.

    :param problem:  details of the data processed for each parameters
    :file_paths: paths to the archived data
    """

    for path in file_paths:
        with open(path, 'rb') as f:
            data = np.load(f, allow_pickle=True)[()]

        for param in y_labels.keys():
            plot_all_vars(problem, data, param)
            plt.show()


if __name__ == '__main__':

    # OFAT analysis for civil violence model without network
    file_paths = [
        # './archives/saved_data_1611773618.npy',  # Same than saved_data_local_SA.npy
        './archives/saved_data_local_SA.npy',
    ]

    problem = {
        'num_vars': 5,
        'names': ['active_threshold_t', 'initial_legitimacy_l0',
                  'max_jail_term', 'agent_vision', 'cop_vision'],
        'bounds': [[0.01, 1], [0.01, 1], [1, 100], [0.01, 0.4], [1, 20], [1, 20]]
    }

    load_plot_archive(problem, file_paths)
