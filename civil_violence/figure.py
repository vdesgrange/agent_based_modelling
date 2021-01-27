import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import networkx as nx


def create_fig(data, draw=False):

    if draw is not False:
        df = pd.DataFrame(data)
        df.columns = ['Node', 'Edges']
        
        fig = sns.displot(df['Edges'], bins=max(df['Edges'])+1, kde=True)

        plt.title('Amount of edges per node')
        plt.show()

    else:
        pass


def draw_multiple_graphs(num_nodes=100, p=0.2, p_ws=0.1, seed=None):

    # Erdos Renyi
    erdos = nx.generators.random_graphs.erdos_renyi_graph(num_nodes, p)
    erdos_small = nx.generators.random_graphs.erdos_renyi_graph(int(num_nodes/5), p)
    
    # Watts Strogatz
    k = int((num_nodes-1)*p)
    watts = nx.generators.random_graphs.watts_strogatz_graph(num_nodes, k, p)

    k_small = int(((num_nodes/5)-1)*p)
    watts_small = nx.generators.random_graphs.watts_strogatz_graph(int(num_nodes/5), k_small, p)

    # Barabasi alber
    m = int((p*num_nodes-1)/2)
    barabasi = nx.generators.random_graphs.barabasi_albert_graph(num_nodes, m)

    m_small = int((p*(num_nodes/5)-1)/2)
    barabasi_small = nx.generators.random_graphs.barabasi_albert_graph(int(num_nodes/5), m_small)

    fig, axs = plt.subplots(3, 3)
    ax = axs.flatten()

    # draw erdos
    nx.draw_circular(erdos_small, node_size=10, font_size=5, ax=ax[0])
    # nx.draw_circular(erdos, node_size=10, ax=ax[3])
    df = pd.DataFrame(list(nx.clustering(erdos).items()))
    df.columns = ['Node', 'Clustering']
    sns.distplot(df['Clustering'], kde=True, ax=ax[3])

    df = pd.DataFrame(erdos.degree())
    df.columns = ['Node', 'Edges']
    sns.distplot(df['Edges'], kde=True, ax=ax[6])

    # draw watts
    nx.draw_circular(watts_small, node_size=10, ax=ax[1])

    df = pd.DataFrame(list(nx.clustering(watts).items()))
    df.columns = ['Node', 'Clustering']
    sns.distplot(df['Clustering'], kde=True, ax=ax[4])

    df = pd.DataFrame(watts.degree())
    df.columns = ['Node', 'Edges']
    sns.distplot(df['Edges'], kde=True, ax=ax[7])

    # draw barabasi
    nx.draw_circular(barabasi_small, node_size=10, ax=ax[2])

    df = pd.DataFrame(list(nx.clustering(barabasi).items()))
    df.columns = ['Node', 'Clustering']
    sns.distplot(df['Clustering'], kde=True, ax=ax[5])

    df = pd.DataFrame(barabasi.degree())
    df.columns = ['Node', 'Edges']
    sns.distplot(df['Edges'], kde=True, ax=ax[8])
    
    # create_fig(erdos.edges, draw=True)
    # Draw the graphs
    # nx.draw(graph)
    for _ in ax:
        _.set_ylabel('')
        _.set_xlabel('')

    ax[0].set_title('Ernos-Renyi', size=10)
    ax[1].set_title('Watts-Strogatz', size=10)
    ax[2].set_title('Barabasi-Albert', size=10)

    ax[0].set_ylabel('Network')
    ax[3].set_ylabel('Fraction of cluster coefficient')
    ax[6].set_ylabel('Fraction')

    ax[4].set_xlabel('Cluster Coefficient')
    ax[7].set_xlabel('Degree distribution')
    plt.show()


if __name__ == '__main__':
    draw_multiple_graphs()

