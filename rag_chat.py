from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

load_dotenv()

# 1️⃣ Load embeddings (Fixed: Using standard LangChain class)
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

# 2️⃣ Load existing vector DB
vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # Get top 2 most relevant chunks

# 3️⃣ Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="models/gemini-3-flash-preview",
    temperature=0.1 # Lower temperature = more factual/less creative
)

# 4️⃣ Prompt template
prompt = ChatPromptTemplate.from_template("""
You are a knowledgeable assistant. 

Based on the provided context, give a detailed and descriptive answer to the question. 
If the information is not present, say you don't know.

Context:
{context}

Question:
{question}

Detailed Answer:
""")

# 5️⃣ Execution Logic
question = "What does SpaceX focus on?"

# Retrieve relevant chunks
docs = retriever.invoke(question)

if not docs:
    print("\nFinal Answer:\nNo relevant documents found in the database.")
else:
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Define the chain
    chain = prompt | llm | StrOutputParser()

    # Invoke
    response = chain.invoke({
        "context": context,
        "question": question
    })

    print("\nFinal Answer:\n")
    print(response)