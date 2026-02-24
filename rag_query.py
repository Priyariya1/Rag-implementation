from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
import os

load_dotenv()

# Same embedding model
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# Load existing vector DB
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever()

query = "What does SpaceX focus on?"

# ✅ New way (instead of get_relevant_documents)
docs = retriever.invoke(query)

print("Retrieved Documents:\n")

for doc in docs:
    print(doc.page_content)
    print("-" * 50)