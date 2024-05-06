import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.offline import plot
import os
import pandas as pd
import pickle 
import streamlit as st
from datetime import datetime

folder_path = "../data/graphs_info/"
@st.cache_data
def load_graph_data(year, month):
    path = os.path.join(folder_path, f"{str(year)}/{month}_month/")
    with open(os.path.join(path, 'pos.pkl'), 'rb') as f:
        pos = pickle.load(f)
    with open(os.path.join(path, 'paritition.pkl'), 'rb') as f:
        partition = pickle.load(f)
    with open(os.path.join(path, 'degree_centrality.pkl'), 'rb') as f:
        dc = pickle.load(f)
    with open(os.path.join(path, 'between_centrality.pkl'), 'rb') as f:
        bc = pickle.load(f)
    df = pd.read_csv(os.path.join(path, 'graph.csv'))
    return df, pos, partition, dc, bc

def load_pickle_data(path):
    with open(os.path.join(folder_path, path), 'rb') as f:
        return pickle.load(f)

def draw_graph_3d(G, pos, partition, measures, title, min_node_size, max_node_size):
    centrality = np.array(list(measures.values()))
    centrality_size = (((centrality-min(centrality))/(max(centrality)-min(centrality))) * (max_node_size-min_node_size)) + min_node_size
    edge_x = []
    edge_y = []
    edge_z = []
    weights = []
    weight_values = nx.get_edge_attributes(G, 'weight')
    # pos = nx.spring_layout(graph, dim=3, k=1e-4, seed=429)
    pos = nx.kamada_kawai_layout(G, dim=3,)
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])
        weights.append(f'{edge[0]}, {edge[1]}: {weight_values[(edge[0], edge[1])]}')
    
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=1, color='grey'),
        mode='lines',
        opacity=0.8
    )

    node_x = []
    node_y = []
    node_z = []
    node_colors = []  # List to store node colors
    partition_nodes = {pid: [] for pid in set(partition.values())}
    for node in G.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        # Assign color based on partition
        node_colors.append(partition[node])
        partition_nodes[partition[node]].append(node)
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers',
        hoverinfo='text',
        marker=dict(
            size=centrality_size, 
            line=dict(width=2), 
            color=node_colors,
            colorscale='Viridis',   # choose a colorscale
            opacity=1,
            colorbar=dict(
                thickness=15,
                title='Group',
                xanchor='left',
                titleside='right'
            ),
        ),
        # text=[f'Node {node}' for node in graph.nodes()],
        # textposition='bottom center'
    )

    # invisible_similarity_trace = go.Scatter3d(
    #     x=node_x, y=node_y, z=node_z,
    #     mode='markers',
    #     hoverinfo='text',
    #     marker=dict(
    #         color=[],
    #         opacity=0,
    #     )
    # )
    # invisible_similarity_trace.text=weights

    node_text = []
    for node, adjacencies in enumerate(G.adjacency()):
        node_text.append(adjacencies[0])

    node_trace.text = node_text

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=title,
        showlegend=False,
        width=800,  # Adjust figure width
        height=800,  # Adjust figure height
        scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
        # scene_camera=camera
    )
    return fig

st.title('Streamlit Assignment')
# Slider for selecting month from January 2018 to December 2023
min_month = datetime(2018, 1, 1)
max_month = datetime(2023, 12, 1)
selected_month = st.sidebar.slider(
    "Select Month",
    min_value=min_month,
    max_value=max_month,
    value=min_month,
    format="YYYY/MM"
)
year = selected_month.year
month = selected_month.month
df, positions, partition, dc, bc = load_graph_data(year, month)


G = nx.Graph()

for index, row in df.iterrows():
    G.add_edge(row['target'], row['source'] , weight=row['weight'])

Gcc = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])

fig = draw_graph_3d(Gcc, positions, partition, bc, "3D graph", min_node_size=10, max_node_size=100)

st.plotly_chart(fig)
