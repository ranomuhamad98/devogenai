import pandas as pd
from google.cloud import bigquery

client = bigquery.Client()

def upload_df_to_bq(table_id,dataframe,project_id):
    QUERY = (f"drop table if exists {table_id}")
    client.query(QUERY)  # API request

    modelParser = pd.read_csv(dataframe)
    modelParser.to_gbq(table_id, project_id=project_id)