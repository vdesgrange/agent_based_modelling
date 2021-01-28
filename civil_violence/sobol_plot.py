from SALib.analyze import sobol
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations

# from Sobol import problem

def plot_index(s, params, i, title=''):
    """
    Creates a plot for Sobol sensitivity analysis that shows the contributions
    of each parameter to the global sensitivity.

    Args:
        s (dict): dictionary {'S#': dict, 'S#_conf': dict} of dicts that hold
            the values for a set of parameters
        params (list): the parameters taken from s
        i (str): string that indicates what order the sensitivity is.
        title (str): title for the plot
    """

    if i == '2':
        p = len(params)
        params = list(combinations(params, 2))
        indices = s['S' + i].reshape((p ** 2))
        indices = indices[~np.isnan(indices)]
        errors = s['S' + i + '_conf'].reshape((p ** 2))
        errors = errors[~np.isnan(errors)]
    else:
        indices = s['S' + i]
        errors = s['S' + i + '_conf']
        plt.figure()

    l = len(indices)

    plt.title(title)
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
    plt.axvline(0, c='k')


def sobol_plot_main():
    problem = {
        'num_vars': 3,
        'names': ['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term'],
        'bounds': [[0.01, 1], [0.01, 1], [1, 100]]
    }

    file_path = [
        # './archives/saved_data_sobol_1611799908.npy',
        './archives/saved_data_sobol_no_network_1611861983.npy',
    ]

    for path in file_path:
        with open(path, 'rb') as f:
            data = np.load(f, allow_pickle=True)[()]

    data = pd.DataFrame(data, columns = ['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term', 'Run',
                                         'QUIESCENT', 'ACTIVE', 'JAILED', 'OUTBREAKS', 'LEGITIMACY'])
    Y = data['OUTBREAKS'].values

    # loaded_data = pd.DataFrame(data, columns=['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term', 'Run',
    #                                             'QUIESCENT', 'ACTIVE', 'JAILED', 'OUTBREAKS', 'LEGITIMACY'])
    # loaded_data = loaded_data.drop(loaded_data.index[2992:])
    # Y = loaded_data['OUTBREAKS'].values

    Si_outbreaks = sobol.analyze(problem, Y, print_to_console=False)
    Si = Si_outbreaks

    # plot_index(Si, problem['names'], '1', 'First order sensitivity')
    # plt.show()
    #
    # # Second order
    # plot_index(Si, problem['names'], '2', 'Second order sensitivity')
    # plt.show()

    # Total order
    plot_index(Si, ['Active threshold', 'Initial legitimacy', 'Max jail term'], 'T', 'Total order sensitivity')
    plt.show()


if __name__ == '__main__':
    sobol_plot_main()