import os
import pandas as pd

credential_file = "/Users/husnusensoy/Documents/code/learn-python-in-a-day/analytics-bootcamp-323516-04308ccfbcba.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_file

project_id = "analytics-bootcamp-323516"


def run_sql(query):
    return pd.read_gbq(query, project_id=project_id, dialect="standard", use_bqstorage_api=True)
