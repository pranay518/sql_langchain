import streamlit as st
import langchain
from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain
from langchain.chat_models import ChatOpenAI
from langsmith import Client
from langchain.smith import RunEvalConfig, run_on_dataset
from pydantic import BaseModel, Field
from langchain.chat_models import AzureChatOpenAI
import os
from dotenv import load_dotenv
import openai
import pyodbc
import sqlalchemy
from sqlalchemy import create_engine, text, exc
from sqlalchemy.dialects.mssql import pymssql
from subprocess import check_output
#from common.prompts import MSSQL_PROMPT
from langchain_experimental.sql.base import SQLDatabaseSequentialChain


# Define the connection parameters
server = "INPUNL658\MSSQLSERVER01"
database = 'EnoviaReadAreaTest2'
username = "Pran"
password = 'Sandseco122021'
driver = 'ODBC Driver 17 for SQL Server'


conn_str = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
db = SQLDatabase.from_uri(conn_str)


load_dotenv()
openai.api_type = "azure"
openai.api_version = "2023-05-15"
#llm = ChatOpenAI(temperature=0)
llm = AzureChatOpenAI(
                deployment_name=os.getenv("OPENAI_GPT_DEPLOYMENT_NAME"),
                temperature=0,
                openai_api_version="2023-05-15",
                openai_api_type="azure",
                openai_api_base=os.getenv("OPENAI_API_BASE"),
                openai_api_key=os.getenv('OPENAI_API_KEY')
                #request_timeout=REQUEST_TIMEOUT,
            )
#db_chain = SQLDatabaseChain.from_llm(llm, db, prompt=MSSQL_PROMPT,top_k=10,return_intermediate_steps=True)
db_chain = SQLDatabaseChain.from_llm(llm, db,return_intermediate_steps=True)

from langsmith import Client
client = Client()
def send_feedback(run_id, score):
    client.create_feedback(run_id, "user_score", score=score)


query_file = "queries.txt"

# Load the list of queries to process
with open(query_file, "r") as f:
    queries = f.readlines()

# Process each query and save the results to a file
results_file = "results.txt"
with open(results_file, "w") as f:
    for query in queries:
        result = db_chain({"query": query})
        f.write(f"{query}\n{result['result']}\n\n")

print("Batch processing complete!")