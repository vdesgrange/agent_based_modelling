import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def create_fig(data, draw=False):

    if draw is not False:
        df = pd.DataFrame(data)
        df.columns = ['Node', 'Edges']
        
        sns.displot(df['Edges'], bins=max(df['Edges'])+1, kde=True)
        plt.title('Amount of edges per node')
        plt.show()
    
    else:
        pass




