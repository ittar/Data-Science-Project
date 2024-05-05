import streamlit as st
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

df = pd.read_csv("ETL/afflication.csv")

heatmap_data = df.groupby(['country', 'city', 'organization_name']).size().reset_index()

st.write(heatmap_data)

fig = go.Figure()
fig.add_trace(go.Scattergeo(
        lon = [21.0936],
        lat = [7.1881],
        text = ['Africa'],
        mode = 'text',
        showlegend = False,
        geo = 'geo2'
    ))
fig.show()

st.write(px.scatter_geo(heatmap_data, locations="iso_alpha", color="continent",
                     hover_name="country", size="pop",
                     projection="natural earth")
        )
