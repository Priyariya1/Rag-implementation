from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os
import time
from fastapi import UploadFile, File
from langchain_community.document_loaders import PyPDFLoader
import shutil

from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.chains import ConversationalRetrievalChain

print("APP STARTED")

# Create the data directory automatically if it doesn't exist
if not os.path.exists("./data"):
    os.makedirs("./data")

load_dotenv()

app = FastAPI()

@app.get("/")
def test():
    return {"status": "working"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Define the location first
    file_location = f"./data/{file.filename}"
    
    # Save the file to that location
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
    
    # Now the loader can find the file location
    loader = PyPDFLoader(file_location)
    new_docs = loader.load_and_split()
    
    # Batching logic (to avoid that 429 error from before)
    batch_size = 3 
    for i in range(0, len(new_docs), batch_size):
        batch = new_docs[i : i + batch_size]
        vectorstore.add_documents(batch)
        time.sleep(10)  # Calm down the API calls
        
    return {"info": f"File '{file.filename}' processed successfully!"}

# Setup Embeddings & Vector DB
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

# Setup LLM & Memory
llm = ChatGoogleGenerativeAI(
    model="models/gemini-3-flash-preview",
    temperature=0.3
)

# Buffer memory for chat history
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

#  Create Conversational Retrieval Chain
# This combines retriever, LLM, and Memory automatically
rag_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory,
    return_source_documents=True
)

class QueryRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(request: QueryRequest):
    try:
        result = rag_chain.invoke({"question": request.question})
        
        return {
            "answer": result["answer"],
            "source_documents": [doc.page_content for doc in result["source_documents"]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)