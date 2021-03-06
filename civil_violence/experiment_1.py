import time
import numpy as np
from mesa.batchrunner import BatchRunner
from civil_violence_model import CivilViolenceModel
from utils import read_configuration


def experiment_1(replicates=40, max_steps=200, graph_type="None"):
    """
    Experiment 1 - Run simulations of civil violence with network model.
    Function to generates data which are used for comparison of network topology influence on civil violence model.
    """
    path = 'archives/saved_data_experiment_1_{0}_{1}'.format(int(time.time()), graph_type)

    configuration = read_configuration()
    model_params = {}
    model_params.update(configuration)  # Overwritten user parameters don't appear in the graphic interface
    model_params.update({'seed': None})
    model_params['graph_type'] = graph_type
    model_params['max_iter'] = max_steps

    batch = BatchRunner(CivilViolenceModel,
                        max_steps=max_steps,
                        iterations=replicates,
                        fixed_parameters=model_params,
                        model_reporters={'All_Data': lambda m: m.datacollector,
                                         "QUIESCENT": lambda m: m.count_type_citizens("QUIESCENT"),
                                         "ACTIVE": lambda m: m.count_type_citizens("ACTIVE"),
                                         "JAILED": lambda m: m.count_type_citizens("JAILED"),
                                         "OUTBREAKS": lambda m: m.outbreaks},  # attempt all
                        display_progress=True)

    batch.run_all()

    batch_df = batch.get_model_vars_dataframe()
    batch_df = batch_df.drop('All_Data', axis=1)

    data = batch_df
    run_data = batch.get_collector_model()

    with open(path, 'ab') as f:
        np.save(f, data)

    run_path = path+'_run'
    with open(run_path, 'ab') as f:
        np.save(f, run_data)


if __name__ == '__main__':
    # Graph_type to be changed to compare influence of each networks
    experiment_1(replicates=2, max_steps=200, graph_type="None")
