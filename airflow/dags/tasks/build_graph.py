import pickle
import pandas as pd
import networkx as nx
import community as community_louvain

def build_graph():
    for i in range(1,13):
        df = pd.read_csv(f'/opt/airflow/data/graphs_info_UAE_v3/2024/{i}_month/graph.csv')
        G = nx.Graph()
        for index, row in df.iterrows():
            G.add_edge(row['target'], row['source'] , weight=row['weight'])
        Gcc = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])
        bc = nx.betweenness_centrality(Gcc)
        partition = community_louvain.best_partition(Gcc)

        with open(f'/opt/airflow/data/graphs_info_UAE_v3/2024/{i}_month/partition.pkl', 'wb') as f:
            pickle.dump(partition, f)

        with open(f'/opt/airflow/data/graphs_info_UAE_v3/2024/{i}_month/between_centrality.pkl', 'wb') as f:
            pickle.dump(bc, f)

