from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain
from dotenv import load_dotenv
import os
import time
import shutil

print("APP STARTED")

load_dotenv()

app = FastAPI()

# Ensure data directory exists
os.makedirs("./data", exist_ok=True)
os.makedirs("./chroma_db", exist_ok=True)

# GLOBAL OBJECTS

vectorstore = None
rag_chain = None

# VECTORSTORE INITIALIZER

def get_vectorstore():
    global vectorstore

    if vectorstore is None:
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001"
        )

        vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )

    return vectorstore

# RAG CHAIN INITIALIZER

def get_rag_chain():
    global rag_chain

    if rag_chain is None:
        vs = get_vectorstore()

        llm = ChatGoogleGenerativeAI(
            model="models/gemini-3-flash-preview",
            temperature=0.3
        )

        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )

        rag_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vs.as_retriever(),
            memory=memory,
            return_source_documents=True
        )

    return rag_chain


# HEALTH CHECK

@app.get("/")
def home():
    return {"status": "working"}

# FILE UPLOAD

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    file_location = f"./data/{file.filename}"

    # Save file
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)

    loader = PyPDFLoader(file_location)
    new_docs = loader.load_and_split()

    vs = get_vectorstore()

    batch_size = 3
    for i in range(0, len(new_docs), batch_size):
        batch = new_docs[i: i + batch_size]
        vs.add_documents(batch)
        time.sleep(5)

    return {"info": f"File '{file.filename}' processed successfully!"}


# CHAT ENDPOINT

class QueryRequest(BaseModel):
    question: str


@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        chain = get_rag_chain()

        result = chain.invoke({"question": request.question})

        return {
            "answer": result["answer"],
            "source_documents": [
                doc.page_content for doc in result["source_documents"]
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# LOCAL RUN

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)