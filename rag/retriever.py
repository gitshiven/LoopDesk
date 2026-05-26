from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from rag.loader import load_docs
import os

CHROMA_PATH = "chroma_db"

def build_vectorstore():
    chunks = load_docs()
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"Vector store built and saved to {CHROMA_PATH}")
    return vectorstore

def get_retriever(category: str = None):
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    if category:
        retriever = vectorstore.as_retriever(
            search_kwargs={
                "k": 4,
                "filter": {"category": category}
            }
        )
    else:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return retriever