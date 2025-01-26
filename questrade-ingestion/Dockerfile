FROM python:3.13.0

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2 requests pyyaml typing_extensions

WORKDIR /app
COPY ingest_data.py ingest_data.py
COPY utils.py utils.py
COPY questrade.py questrade.py
COPY access_token.yaml access_token.yaml

ENTRYPOINT [ "python", "ingest_data.py" ]