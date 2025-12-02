import os
import pandas as pd
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from tqdm import tqdm

DATA_PATH = os.path.join("jobs_clean.csv")
CHROMA_PATH = "data/jobs_db"
EMBED_MODEL = "nomic-embed-text"

def ingest():
    print("Loading cleaned data...")
    if not os.path.exists(DATA_PATH):
        print(f"❌ Error: File '{DATA_PATH}' not found.")
        print("   Please run the data processing script to generate the cleaned data file.")
        return
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded {len(df)} records.")

    documents = []
    print("Creating documents for embedding...")
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Processing Rows"):
        doc = Document(
            page_content= row['text_to_embed'],
            metadata={
                "job_id": str(row['job_id']),
                "company_name": str(row['company_name']),
                "title": str(row['title']),
                "location": str(row['location']),
                "max_salary": str(row['max_salary']),
                "pay_period": str(row['pay_period'])
            }
        )
        documents.append(doc)

    print("Generating embeddings using Ollama...")
    embedder = OllamaEmbeddings(model=EMBED_MODEL)
    veector_store = Chroma.from_documents(
        documents=documents,
        embedding=embedder,
        collection_name="jobs_postings",
        persist_directory=CHROMA_PATH
    )
    print(f"Successfully ingested and embedded {len(documents)} documents into ChromaDB at '{CHROMA_PATH}'.")

if __name__ == "__main__":
    ingest()
