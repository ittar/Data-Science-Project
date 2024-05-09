import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

def transform_data():
    model = SentenceTransformer('WhereIsAI/UAE-Large-V1')

    df = pd.read_csv(f'/opt/airflow/data/{name}.csv')
    words = df.abstract.values
    vectors = model.encode(words)
    df['abs_vector'] = vectors.tolist()
    
    for i in range(1,13):
        rows_month_i = df.loc[df.month==i]
        if (len(rows_month_i)): break
        vector = list(rows_month_i['abs_vector'].values)
        sims = cosine_similarity(vector, vector)
        for j in range(len(vector)):
            for k in range(len(vector)):
                if j<=k:
                    sims[j, k] = False
        indices = np.argwhere(sims > 0.65)
        df_node = pd.DataFrame(columns=['target', 'source', 'weight'])

        for index in indices:
            target = index[0]
            source = index[1]
            weight = sims[index[0], index[1]]
            app_df = pd.DataFrame({'target': [target], 'source': [source], 'weight': [weight]})
            tmp_df = pd.concat([tmp_df, app_df])

        df_node.to_csv(f'/opt/airflow/data/{i}/graph.csv')