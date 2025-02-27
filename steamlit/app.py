import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.offline import plot
import plotly.express as px
from plotly.express.colors import sample_colorscale
import os
import pandas as pd
import pickle 
import streamlit as st
from datetime import datetime

st.set_page_config(layout="wide")

folder_path = "../data/graphs_info/"

# @st.cache_data
def load_graph_data(year, month):
    year_path = os.path.join(folder_path, f'{str(year)}/')
    path = os.path.join(year_path, f'{month}_month/')
    with open(os.path.join(path, 'pos.pkl'), 'rb') as f:
        pos = pickle.load(f)
    with open(os.path.join(path, 'partition.pkl'), 'rb') as f:
        partition = pickle.load(f)
    with open(os.path.join(path, 'between_centrality.pkl'), 'rb') as f:
        bc = pickle.load(f)
    with open(os.path.join(path, 'topics.pkl'), 'rb') as f:
        keywords = pickle.load(f)
    df = pd.read_csv(os.path.join(path, 'graph.csv'))
    df.set_index(df.columns[0], inplace=True)
    info_df = pd.read_csv(os.path.join(year_path, f'{str(year)}_paper_info.csv'))
    info_df.set_index(info_df.columns[0], inplace=True)
    return info_df, df, pos, partition, bc, keywords

def load_pickle_data(path):
    with open(os.path.join(folder_path, path), 'rb') as f:
        return pickle.load(f)

def draw_graph_3d(G, pos, partition, measures, kw, title, min_node_size, max_node_size, top_n = 5):
    centrality = np.array(list(measures.values()))
    centrality_size = (((centrality-min(centrality))/(max(centrality)-min(centrality) + 1e-4)) * (max_node_size-min_node_size)) + min_node_size
    edge_x = []
    edge_y = []
    edge_z = []
    weights = []
    weight_values = nx.get_edge_attributes(G, 'weight')
    # # pos = nx.spring_layout(graph, dim=3, k=1e-4, seed=123)
    # pos = nx.kamada_kawai_layout(G, dim=3,)
    for edge in G.edges():
        x0, y0, z0 = pos[edge[0]]
        x1, y1, z1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])
        weights.append(f'{edge[0]}, {edge[1]}: {weight_values[(edge[0], edge[1])]}')
    
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=3, color='grey'),
        mode='lines',
        opacity=1,
        hoverinfo='none'
    )
    node_x = []
    node_y = []
    node_z = []
    node_colors = []  # List to store node colors
    set_partition = set(partition.values())
    cluster_pos = {pid: [] for pid in set_partition}
    max_title_length = 100
    texts = []
    for node in G.nodes():
        t = info_df.loc[int(node)].title
        if len(t) > max_title_length:
            text = f'Title = {t[:max_title_length]}{"<br>"}{t[max_title_length:]}'
        else : text = f'Title = {t}'
        texts.append(text)
    for node in G.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        partition_node = partition[node]
        node_colors.append(partition_node)
        cluster_pos[partition_node].append((x,y,z))

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers',
        # hoverinfo='text',
        marker=dict(
            size=centrality_size, 
            line=dict(width=0), 
            color=node_colors,
            colorscale='Viridis',   # choose a colorscale
            opacity=0.3,
            colorbar=dict(
                thickness=15,
                title='Group',
                xanchor='left',
                titleside='right'
            ),
        ),
        hoverinfo='text',
        text=texts,
        # text=[f'Title: {node}' for node in G.nodes()],
        textposition='bottom center'
    )
    colors = sample_colorscale("Viridis", [n/(len(set(node_colors)) -1) for n in range(len(set(node_colors)))])

    annotations = []
    for pid in set_partition:
        annotation_text = kw[pid]
        p = np.array(cluster_pos[pid]).mean(axis=0)
        annotation = dict(
            x=p[0],
            y=p[1],
            z=p[2],
            text=annotation_text,
            xanchor="center",
            yanchor="top",
            showarrow=False,
            font=dict(
                color=colors[pid],
                size=10
            ),
            opacity=1
        )
        annotations.append(annotation)
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=title,
        showlegend=False,
        width=800,  # Adjust figure width
        height=800,  # Adjust figure height
        scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
    )
    if (kw_show) :
        fig.update_layout(
            scene=dict(annotations=annotations),
        )
    
    return fig


# Slider for selecting month from January 2018 to December 2023
min_month = datetime(2018, 1, 1)
max_month = datetime(2024, 5, 1)
selected_month = st.sidebar.slider(
    "Select Month",
    min_value=min_month,
    max_value=max_month,
    value=min_month,
    format="YYYY/MM"
)
kw_show = st.sidebar.checkbox("Show keyword in network graph", value=True)
year = selected_month.year
month = selected_month.month
info_df, df, positions, partition, bc, keywords = load_graph_data(year, month)
# Load data from CSV files
affiliations_df = pd.read_csv("../static/data/afflication.csv")
G = nx.Graph()
for index, row in df.iterrows():
    G.add_edge(row['target'], row['source'] , weight=row['weight'])

fig = draw_graph_3d(G, positions, partition, bc, keywords, "3D graph", min_node_size=20, max_node_size=50)

month_df = info_df.loc[info_df.month == month]

st.title("Graph Visualization")
st.header(f'{year}/{month} : {len(month_df)} Papers')

col1, col2 = st.columns([2 , 1])

with col1:

    st.header("3D Cluster Graph")
    st.plotly_chart(fig)

    # Create the donut chart
    heatmap_data = affiliations_df.groupby(['country']).size().reset_index(name='size')
    heat_fig = px.pie(heatmap_data, values='size', names='country', hole=0, title='Author\'s Country Chart', )
    heat_fig.update_traces(textposition='inside')
    heat_fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
    st.plotly_chart(heat_fig)
    
with col2:
    papers_per_day = month_df.groupby(['day']).size().reset_index(name='count')

    # Display the data in a Streamlit app
    st.header('Papers Overview')

    # Add a selectbox for selecting a paper
    selected_paper_title = st.selectbox("Select a paper:", month_df['title'])

    # Display detailed information of the selected paper
    selected_paper = month_df[month_df['title'] == selected_paper_title].iloc[0]
    st.write("###", selected_paper['title'])
    st.write("**Abstract:**", selected_paper['abstract'])
    st.write("**Publication Date:**", f"{int(selected_paper['day'])}/{int(selected_paper['month'])}/{selected_paper['year']}")
