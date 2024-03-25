import os
import dotenv
from fastapi import FastAPI
from langserve import add_routes
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.pydantic_v1 import BaseModel
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader , DirectoryLoader
from langchain.tools.retriever import create_retriever_tool
from langchain import hub

config = dotenv.dotenv_values(".env")
OPENAI_API_KEY = config['OPENAI_API_KEY']
SERPER_API_KEY= config['SERPER_API_KEY']
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

loader = DirectoryLoader('./', glob="./*.txt", loader_cls=TextLoader,use_multithreading=True)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1250, chunk_overlap=175,)
new_docs = text_splitter.split_documents(docs)
doc_strings = [doc.page_content for doc in new_docs]
embedding = OpenAIEmbeddings(openai_api_key= OPENAI_API_KEY)
persist_directory = "chroma_db"
vectordb = Chroma.from_documents(
    documents=new_docs, embedding=embedding, persist_directory=persist_directory
)

vectordb.persist()

ids = [str(i) for i in range(1, len(new_docs) + 1)]
vectordb = Chroma.from_documents(new_docs, embedding, ids=ids)
retriever = vectordb.as_retriever(search_kwargs={"k": 3})
model=ChatOpenAI(model="gpt-3.5-turbo-1106",temperature=0.1)
prompt = hub.pull("vinci/ceo-agent")
retriever_tool=create_retriever_tool(
    retriever,
    "Company-search",
    description="Use this tool when retrieving information about a company")
tools = [retriever_tool]
agent= create_openai_functions_agent(
    llm=model,
    prompt=prompt,
    tools=tools
)
agentExecutor=AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True, handle_parsing_errors=True, max_iterations=3
)
class Input(BaseModel):
    input: str

class Output(BaseModel):
    output: str
app = FastAPI(
    title="CEO-AGENT",
    version="0.1",
    description="API for serving a langchain agent that can retrieve information from google searches."
)

add_routes(
    app, agentExecutor.with_types(input_type=Input, output_type=Output).with_config(
        {"run_name": "agent"}
    ), path="/agent"
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
