from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

class GeminiEmbeddings:
    def embed_documents(self, texts):
        embeddings = []
        for text in texts:
            response = client.models.embed_content(
                model="models/gemini-embedding-001",
                contents=text
            )
            # FIX HERE
            embeddings.append(response.embeddings[0].values)
        return embeddings

    def embed_query(self, text):
        response = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=text
        )
        # FIX HERE
        return response.embeddings[0].values