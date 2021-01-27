import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


THRESHOLD = 150
file_paths = [
        # './archives/saved_data1611648500.npy'
        './archives/saved_data1611693859'
        # './archives/saved_data1611747993_run'
    ]

def load_datacollector():
    data_dict = {}

    for path in file_paths:
        with open(path, 'rb+') as f:

            data = np.load(f, allow_pickle = True)[()]
            keys = data.keys()
            print('Keys of this dict: ', keys, '\n')
            data_dict[path] = data
    
    return data_dict

def show_active(data):
    actives = np.array(data['inf_threshold'])
    print(np.shape(actives), '\n', actives)

def get_outbreaks(data, threshold):
    '''
    Calculates the outbreaks from the actives data.

    Returns:
        - An array with the outbreak peak sizes.
        - An array with the outbreak durations.
    '''
    outbreak_peaks = []
    outbreak_widths = []
    counting = False
    current_peak = 0

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

    return outbreak_peaks, outbreak_widths

def save_csv(df):

    path = 'archives/temp.csv'
    df.to_csv(path)


thresh_data = load_datacollector()
print('Thresh: ', thresh_data)
save_csv(thresh_data)

model_data = load_datacollector()

for d in model_data:
    print(model_data[d]['active_threshold_t'])


test_data = np.array([10, 20, 30, 80, 201, 75, 100, 120, 220, 201, 190, 100, 80])
peaks, sizes = get_outbreaks(test_data, 100)

print(peaks, sizes)