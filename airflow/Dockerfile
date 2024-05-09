FROM apache/airflow:2.6.0
COPY requirements.txt .
# RUN apt-get install python3.10 python3.10-venv python3.10-dev
# RUN python -m pip install --upgrade pip
# RUN pip install python==3.8
USER root
RUN sudo apt upgrade python3.9
# RUN python3 -m pip install --upgrade pip
# RUN pip install python
USER airflow
RUN pip install -U sentence-transformers
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000