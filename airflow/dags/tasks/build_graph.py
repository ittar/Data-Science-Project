import pickle
from networkx import is_empty
import pandas as pd
import networkx as nx
import community as community_louvain

def build_graph():
    for i in range(1,13):
        df = pd.read_csv(f'/opt/airflow/data/graphs_info/2024/{i}_month/graph.csv')
        G = nx.Graph()
        for index, row in df.iterrows():
            G.add_edge(row['target'], row['source'] , weight=row['weight'])
        bc = dict()
        partition = dict()
        if (not is_empty(G)):
            bc = nx.betweenness_centrality(G)
            partition = community_louvain.best_partition(G)

        with open(f'/opt/airflow/data/graphs_info/2024/{i}_month/partition.pkl', 'wb') as f:
                pickle.dump(partition, f)

        with open(f'/opt/airflow/data/graphs_info/2024/{i}_month/between_centrality.pkl', 'wb') as f:
                pickle.dump(bc, f)

