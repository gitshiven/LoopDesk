from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def load_docs():
    docs_path = "docs"
    all_docs = []

    for filename in os.listdir(docs_path):
        if filename.endswith(".txt"):
            filepath = os.path.join(docs_path, filename)
            loader = TextLoader(filepath, encoding="utf-8")
            docs = loader.load()

            # Tag each doc with its category
            for doc in docs:
                if "billing" in filename:
                    doc.metadata["category"] = "billing"
                elif "technical" in filename:
                    doc.metadata["category"] = "technical"
                else:
                    doc.metadata["category"] = "general"

            all_docs.extend(docs)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(all_docs)
    print(f"Loaded {len(chunks)} chunks from {len(all_docs)} documents")
    return chunks