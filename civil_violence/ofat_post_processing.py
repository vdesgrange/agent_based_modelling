import numpy as np
import pandas as pd

'''
README:
To run this script, please follow the following steps:
    1. Adjust the following constants such that they correspond to those in the SA.py file. 
    2. Run the ofat_mp.py script. 
    3. Add the paths to the output files from the ofat_mp.py to the file_paths list (line27).
    4. Depending on if the output files is a Sensitivity Analysis (multiple dictionaries), 
    or a fixed run (single dictionary), several lines need to be commented in/out. 
    5. Run the ofat_work.py script. 
'''

THRESHOLD = 50
ITERATIONS = 10
STEPS = 20
N_PARAMS = 6
N_OUTPUT = 6

PARAMS = ['active_threshold_t', 'initial_legitimacy_l0', 'max_jail_term', 'p', 'agent_vision', 'cop_vision']
BOUNDS = [[0.01, 1], [0.01, 1], [1, 100], [0.01, 0.4], [1, 20], [1, 20]]
OUTPUT_PARAMS = ['PARAM_VAL', 'MEAN_N', 'MEAN_PEAK_HEIGHT', 'MEAN_PEAK_WIDTH', 'MAX_PEAK_HEIGHT', 'MAX_PEAK_WIDTH']

file_paths = ['./archives/saved_data_1611773618.npy', './archives/saved_data_1611773618_run.npy']


def load_datacollector():
    """
    Loads in the data from the specified paths into different dictionaries.
    """
    data_dict = {}

    for path in file_paths:
        with open(path, 'rb+') as f:

            data = np.load(f, allow_pickle = True)[()]
            keys = data.keys()
            data_dict[path] = data
    
    return data_dict


def map_keys():
    """
    Maps the used parameter bounds to key values for the data dictionary. 
    Keys are of the form: (Parameter value, iteration)
    """
    keys_dict = {}
    # iter_list = np.arange(ITERATIONS*STEPS).reshape((STEPS, ITERATIONS)) # In case of multiple exported dictionaries.
    iter_list = np.arange(ITERATIONS)	# In case of a single exported dictionary
    for i in range(len(PARAMS)):
        param_list = []
        if PARAMS[i] == 'max_jail_term':
            param_range = np.linspace(BOUNDS[i][0], BOUNDS[i][1], STEPS, dtype=np.int32).reshape(STEPS, 1)
        else:
            param_range = np.linspace(BOUNDS[i][0], BOUNDS[i][1], STEPS).reshape(STEPS, 1)
        param_matrix = np.repeat(param_range, ITERATIONS, axis=1)
        for j in range(STEPS):
            # param_list.extend(list(zip(param_matrix[j], iter_list[j]))) # In case of multiple exported dictionaries.
            param_list.extend(list(zip(param_matrix[j], iter_list))) # In case of a single exported dictionary.
        keys_dict[PARAMS[i]] = param_list

    return keys_dict


def get_param_means(data, parameter):
    """
    For a provided parameter, calculates the determined output values for every parameter/iteration
    configuration.

    Returns a dataframe with the output type as column names. Every row contains the mean values of 
    the set amount of iterations for every parameter configuration.
    """
    # Initialize outputs
    output = np.zeros((STEPS, N_OUTPUT))   
    keys = keys_dict[parameter]

    # Divide the key list in the different step sizes of the parameter.
    for i in range(STEPS):
        peak_heights = []
        peak_widths = []
        s_keys = keys[i*ITERATIONS : (i+1)*ITERATIONS]
        
        # Every key is an iteration
        for key in s_keys:
            actives = data[parameter][key]['ACTIVE']
            ph, pw = get_outbreaks(actives, THRESHOLD)
            peak_heights.extend(ph)
            peak_widths.extend(pw)
            
        # Output calculation
        mean_n_peaks = len(peak_heights)/ITERATIONS
        mean_peak_height = np.mean(np.array(peak_heights))
        mean_peak_width = np.mean(peak_widths)
        max_peak_height = np.max(peak_heights)
        max_peak_width = np.max(peak_widths)

        output[i] = [key[0], mean_n_peaks, mean_peak_height, mean_peak_width, max_peak_height, max_peak_width]

    output_df = pd.DataFrame({
        'PARAM_VAL': output[:, 0],
        'MEAN_N': output[:, 1],
        'MEAN_PEAK_HEIGHT': output[:, 2],
        'MEAN_OUTBREAK_DURATION': output[:, 3],
        'MAX_PEAK_HEIGHT': output[:, 4],
        'MAX_OUTBREAK_DURATION': output[:, 5]})
    
    return output_df  # Can also return 'output' if the data is wanted in array form.


def get_outbreaks(data, threshold):
    """
    Calculates the outbreaks from the actives data based on a certain threshold.
    The last codeblock defines the behavior when the provided data ends in an outbreak.
    Depending on the user, they might want to include/exclude that final outbreak.

    Returns:
        - An array with the peak size of every outbreak.
        - An array with the outbreak durations.
    """
    outbreak_peaks = []
    outbreak_widths = []
    counting = False
    current_peak = 0
    start = 0

    for i in range(len(data)):

        if data[i] >= threshold and not counting:
            counting = True
            if current_peak < data[i]:
                current_peak = data[i]
            start = i

        elif data[i] >= threshold and counting:
            if current_peak < data[i]:
                current_peak = data[i]

        elif data[i] < threshold and counting:
            outbreak_peaks.append(current_peak)
            outbreak_widths.append(i-start)
            current_peak = 0
            counting = False

    if not outbreak_peaks and not counting: # Captures data without outbreaks, empty list break further calculations.
        outbreak_peaks.append(0)
        outbreak_widths.append(0)

    # Capture cases where timeline ends in an outbreak.
    # Uncomment if final outbreak needs to be included in calculation.
    # Obviously skewers data, but might be preferable over 0 or infinite outbreaks.
    
    # if not outbreak_peaks and counting: # Data is a single massive outbreak.
    #     outbreak_peaks.append(current_peak)
    #     outbreak_widths.append(len(data))
    # elif outbreak_peaks and counting: # Data ends in an outbreak.
    #     outbreak_peaks.append(current_peak)
    #     outbreak_widths.append(len(data)-start)
 
    return outbreak_peaks, outbreak_widths


def fix_keys(dictionary):
    """
    This function trims the dictionary keys from ([all parameters], iteration) to a more manageable
    ('changed parameter', iteration) format.
    Like in the SA.py file, the 'max_jail_term'-parameter steps are casted to int.
    """
    new_dictionary = {}
    for k in dictionary:
        if dictionary == 'max_jail_term':
            new_k = (int(k[0]), k[-1])
        else:
            new_k = (k[0], k[-1])
        new_dictionary[new_k] = dictionary[k]
    return new_dictionary


def save_csv(name, df):
    """
    Save an output dataframe as a CSV file in the archives folder.
    """
    path = 'archives/'+name+'_out.csv'
    df.to_csv(path)


if __name__ == '__main__':
    # Run the script
    model_data = load_datacollector()
    run_data = model_data[file_paths[1]]  # Step-wise DataCollector is only captured in the *_run.npy files.

    for dic in run_data:
        run_data[dic] = fix_keys(run_data[dic])

    keys_dict = map_keys()
    output_data = {}

    # Output calculation
    for param in run_data.keys():
        output_data[param] = get_param_means(run_data, param)
    # Saving output
    for df in output_data:
        save_csv(str(df), output_data[df])
