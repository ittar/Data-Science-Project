FROM apache/airflow:2.7.1
COPY requirements.txt .

USER root
RUN sudo apt upgrade python3.9

USER airflow
RUN pip install -U sentence-transformers
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000