import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os 

def transform_data():
    model = SentenceTransformer('WhereIsAI/UAE-Large-V1')

    df = pd.read_csv('/opt/airflow/data/graphs_info/2024/2024_paper_info.csv')
    words = df.abstract.values
    vectors = model.encode(words)
    df['abs_vector'] = vectors.tolist()
    
    for i in range(1,13):
        rows_month_i = df.loc[df.month==i]
        # if (len(rows_month_i) == 0): break
        df_node = pd.DataFrame(columns=['target', 'source', 'weight'])
        vector = list(rows_month_i['abs_vector'].values)
        index_vector = rows_month_i.index
        if (len(vector) > 0):
            sims = cosine_similarity(vector, vector)
            for j in range(len(vector)):
                for k in range(len(vector)):
                    if j<=k:
                        sims[j, k] = False
        else: sims = np.array([])
        indices = np.argwhere(sims > 0.65)

        for index in indices:
            target = index_vector[index[0]]
            source = index_vector[index[1]]
            weight = sims[index[0], index[1]]
            app_df = pd.DataFrame({'target': [target], 'source': [source], 'weight': [weight]})
            df_node = pd.concat([df_node, app_df])
        if not os.path.exists(f'/opt/airflow/data/graphs_info/2024/{i}_month'):
            os.mkdir(f'/opt/airflow/data/graphs_info/2024/{i}_month')  
        df_node.to_csv(f'/opt/airflow/data/graphs_info/2024/{i}_month/graph.csv')