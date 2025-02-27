import os
import re
from nltk.corpus import stopwords
import nltk
import pandas as pd
nltk.download("stopwords")
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import FunctionTransformer

def text_preprocessing(s):
    """
    - Lowercase the sentence
    - Change "'t" to "not"
    - Remove "@name"
    - Isolate and remove punctuations except "?"
    - Remove other special characters
    - Remove stop words except "not" and "can"
    - Remove trailing whitespace
    """
    s = s.lower()
    # Change 't to 'not'
    s = re.sub(r"\'t", " not", s)
    # Remove @name
    s = re.sub(r'(@.*?)[\s]', ' ', s)
    # Isolate and remove punctuations except '?'
    s = re.sub(r'([\'\"\!\?\\/\,])', r' \1 ', s)
    s = re.sub(r'[^\w\s\?\.\']', ' ', s)
    # Remove number
    s = re.sub(r'[0-9]', '', s)
    # Remove some special characters
    s = re.sub(r'([\;\:\|•«\n])', ' ', s)
    # Remove stopwords except 'not' and 'can'
    s = " ".join([word for word in s.split()
                  if word not in stopwords.words('english')
                  or word in ['not', 'can']])
    # Remove trailing whitespace
    s = re.sub(r'\s+', ' ', s).strip()

    return s

def clean_data():
    df = pd.read_csv('/opt/airflow/data/arxiv.csv')
    clean_cols = ['abstract']

    txt_pipe = Pipeline([('clean_text', FunctionTransformer(lambda x: x.applymap(text_preprocessing)))])
    col_trans = ColumnTransformer(
        transformers=[('txt_pipe', txt_pipe, clean_cols)]
        )
    
    df[clean_cols] = col_trans.fit_transform(df)
    graph_path = '/opt/airflow/data/graphs_info/'
    if not os.path.exists(graph_path):
        os.mkdir(graph_path)
    folder_path = os.path.join(graph_path, '2024')
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)       
    path = folder_path + '/2024_paper_info.csv'
    if not os.path.exists(path):
        os.mkdir(path)  
    df.to_csv(path)