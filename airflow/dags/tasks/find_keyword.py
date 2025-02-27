import pickle

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer


def find_keyword():
    df = pd.read_csv(f'/opt/airflow/data/graphs_info/2024/2024_paper_info.csv')
    for i in range(1,13):
        with open(f'/opt/airflow/data/graphs_info/2024/{i}_month/partition.pkl', 'rb') as f:
            partition = pickle.load(f)
        set_partition = set(partition.values())
        key_list = df.loc[list(partition.keys())].abstract.values
        val_list = np.array(list(partition.values()))
        partition_nodes = {pid: key_list[np.where(val_list == pid)] for pid in set_partition}
        keywords_group = dict()
        tf_idf = TfidfVectorizer()
        top_n = 5
        for pid in set_partition :
            output = tf_idf.fit_transform(partition_nodes[pid])
            feature_names = tf_idf.get_feature_names_out()
            tfidf_scores = output.max(0).toarray()[0]
            important_words = {word: score for word, score in zip(feature_names, tfidf_scores)}
            important_words_sorted = dict(sorted(important_words.items(), key=lambda x: x[1], reverse=True))
            annotation_text = "/ ".join(list(important_words_sorted.keys())[:top_n])
            keywords_group[pid] = annotation_text
        with open(f'/opt/airflow/data/graphs_info/2024/{i}_month/topics.pkl', 'wb') as f:
            pickle.dump(keywords_group, f)      