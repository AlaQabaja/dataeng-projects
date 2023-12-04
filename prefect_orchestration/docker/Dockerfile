FROM python:3.11.0

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2 prefect prefect_sqlalchemy

WORKDIR /app
COPY ingest_data.py ingest_data.py 

ENTRYPOINT [ "python", "ingest_data.py" ]