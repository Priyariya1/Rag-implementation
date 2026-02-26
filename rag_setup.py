from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()

text = """
Elon Musk founded SpaceX in 2002 with the mission of making life multi-planetary. 
The company focuses heavily on reusable rockets, such as the Falcon 9, which can land 
back on Earth after launch. This technology drastically lowers the cost of space travel. 
Beyond Earth's orbit, SpaceX's primary long-term goal is the colonization of Mars. 
They are currently developing the Starship spacecraft, a fully reusable system designed 
to carry both crew and cargo to the Moon, Mars, and beyond.
"""

# Split text
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=20
)

chunks = splitter.split_text(text)

docs = [Document(page_content=chunk) for chunk in chunks]

# Create embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

# Store in Chroma
vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./chroma_db"
)

print("Embeddings stored successfully!")