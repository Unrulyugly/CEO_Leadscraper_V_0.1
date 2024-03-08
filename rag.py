import os
import json
import dotenv
import requests
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

config = dotenv.dotenv_values(".env")
OPENAI_API_KEY= config['OPENAI_API_KEY']
SERPER_API_KEY= config['SERPER_API_KEY']

def get_ceo_info(email_url):
    search_query = f"CEO of {email_url}"
    url = "https://google.serper.dev/search"

    payload = json.dumps({"q": search_query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    response_json = response.json()
    
    organic_results = response_json.get('organic', [])
    
    return organic_results
    
input_file = 'input.txt'
output_file = 'output.txt'

with open(input_file, 'r') as file:
    lines = file.readlines()

for line in lines:
    at_pos = line.find('@')
    if at_pos != -1:
        email_url = line[at_pos+1:].strip()
        result = get_ceo_info(email_url)
        with open("data.txt", "w") as text_file:
              for item in result:
                 text_file.write(json.dumps(item) + "\n")

data = TextLoader('data.txt').load()
def get_info_from(data):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )
    splitDocs = splitter.split_documents(data)
    return splitDocs
def create_db(data):
    embedding = OpenAIEmbeddings(openai_api_key= OPENAI_API_KEY)
    persist_directory = "chroma_db"
    vectordb = Chroma.from_documents(
        documents=data, embedding=embedding, persist_directory=persist_directory
    )
    vectordb.persist()

    ids = [str(i) for i in range(1, len(data) + 1)]
    vectordb = Chroma.from_documents(data, embedding, ids=ids)
    return vectordb

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def create_chain(vectordb):
    model = ChatOpenAI(
        model="gpt-3.5-turbo-1106",
        temperature=0.1
    )

    prompt = ChatPromptTemplate.from_template("""
    <|system|>>
You are a  Lead Extraction Specialist, your role is to Identify and extract information about the company and  first and last names of CEOs, Founders, or individuals holding equivalent positions based on information about the company which can be found in context.

The context contains relevance information you must use to answer your query

Think step by step before answering the question. You will get a $100 tip if you provide correct answer.

CONTEXT: {context}
</s>
<|user|>
Question: {input}
</s>
<|assistant|>                                      
    """)

    # chain = prompt | model
    chain = create_stuff_documents_chain(
        llm=model,
        prompt=prompt
    )

    retriever = vectordb.as_retriever(search_kwargs={"k": 1})

    retrieval_chain = create_retrieval_chain(
        retriever,
        chain
    )

    return retrieval_chain

data = TextLoader('data.txt').load()
vectordb = create_db(data)
chain = create_chain(vectordb)
response = chain.invoke({
    "input": "what is the name of the present presidents or CEO of the company , reply only with the first and last name nothing else "
})
with open(output_file, 'a') as outfile:
            outfile.write(f"\n{response['answer']}\n{line}")
for collection in vectordb._client.list_collections():
  ids = collection.get()['ids']
  if len(ids): collection.delete(ids)
vectordb._collection.delete(ids=[ids[-1]])
