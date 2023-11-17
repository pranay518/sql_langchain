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
import tiktoken,tokenize


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

# Define a custom output parser function to extract relevant information
# def custom_output_parser(response):
#     # Process the response and extract the relevant information
#     # Return the processed output as needed
#     processed_output = ""

#     return processed_output

# Create an instance of SQLDatabaseSequentialChain with the custom output parser
# db_chain = SQLDatabaseSequentialChain.from_llm(
#     llm,  # Your LLM instance (AzureChatOpenAI)
#     db,  # Your SQLDatabase instance
#     return_intermediate_steps=True,
#     output_parser=custom_output_parser
# )


from langsmith import Client
client = Client()
def send_feedback(run_id, score):
    client.create_feedback(run_id, "user_score", score=score)

# Define a function to split text into chunks
def chunk_text(text, chunk_size):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        chunks.append(chunk)
    return chunks

# Set the chunk size based on the GPT model's token limit
max_chunk_length = 8192
chunk_size = 60  # Adjust this based on the specific GPT model you are using


def count_tokens(chunk):
      tokens = chunk.split(" ")
      return len(tokens)

st.set_page_config(page_title='🦜🔗 Ask the SQL DB App')
st.title('🦜🔗 Ask the SQL DB App')

if st.button('Show schema of Database'):
    file_name = 'schema.png'
    check_output("start " + file_name, shell=True)

query_text = st.text_input('Enter your question:', placeholder='Ask something. Look at schema from the link above ')




# Form input and query
result = None

with st.form('myform', clear_on_submit=True):
    submitted = st.form_submit_button('Submit')

    if submitted:
        with st.spinner('Calculating...'):
            #try:
                # Chunk the query text
                #query_chunks = [query_text[i:i + chunk_size] for i in range(0, len(query_text), chunk_size)]
                query_chunks = [query_text[i:i + max_chunk_length] for i in range(0, len(query_text), max_chunk_length)]
                print(f" query_chunks: {query_chunks}")

                # Split the chunks into groups of 20
                for i in range(0, len(query_chunks), chunk_size):
                    chunk_group = query_chunks[i:i + chunk_size]
                    group_result = ""



                #query_chunks = chunk_text(query_text, chunk_size)

                # Initialize lists to store intermediate steps for each chunk
                sql_commands = []
                sql_results = []

                for chunk in query_chunks:
                    inputs = {"query": chunk}
                    tokens = count_tokens(chunk)
                    print(f"Tokens in chunk: {tokens}")
                    print(f" chunk: {chunk}")
                    response = db_chain(inputs, include_run_info=True)
                    sql_commands.append(response["intermediate_steps"][1])
                    sql_results.append(response["intermediate_steps"][3])

                # Combine the results for all chunks
                result = "\n\n".join(sql_results)

if result is not None:
    st.info(sql_results)
    st.code(sql_commands)
    # st.code(sql_results)
    col_blank, col_text, col1, col2 = st.columns([10, 2,1,1])


                # # You can choose to display or process sql_commands as needed
                # results_file = "results.txt"
                # with open(results_file, "w") as f:
                #     f.write(f"{result}\n\n")

            # except Exception as e:
            #     st.error(f"An error occurred: {e}")

# Rest of your code remains the same
