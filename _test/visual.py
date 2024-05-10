import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

st.title("Streamlit App with Graph Visualization")
st.write("This app demonstrates graph visualization using NetworkX and Streamlit.")

# Load data from CSV files
affiliations_df = pd.read_csv("ETL/afflication.csv")
authors_df = pd.read_csv("ETL/author2afflication.csv")

# Merge author-affiliation data
merged_df = pd.merge(authors_df, affiliations_df, how='left', on='affiliation_id')

# Downsample data
sample_size = min(1000, len(merged_df))  # Adjust sample size as needed
merged_df_sample = merged_df.sample(n=sample_size, random_state=42, replace=False)

# Create a bipartite graph
G = nx.Graph()

for _, row in merged_df_sample.iterrows():
    author = row['author']
    affiliation = row['organization_name']
    G.add_edge(author, affiliation)

# Display the DataFrame
st.write("Grouped Data:")
st.write(merged_df_sample)

# Create the donut chart
heatmap_data = merged_df_sample.groupby(['country', 'city', 'organization_name']).size().reset_index(name='size')
fig = px.pie(heatmap_data, values='size', names='country', hole=0.3)

st.write("Donut Chart:")
st.plotly_chart(fig)

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
info_df, df, positions, partition, dc, bc, keywords = load_graph_data(year, month)

# Draw the graph
st.write("Graph Visualization:")
fig, ax = plt.subplots()  # Create a new figure and axis
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=100, edge_color='black', linewidths=1, font_size=10, ax=ax)
ax.set_title("Author-Affiliation Graph")  # Set the title using the axis
st.pyplot(fig)  # Pass the figure explicitly to st.pyplot()
