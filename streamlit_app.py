import streamlit as st
import requests
import os

# CONFIG
st.set_page_config(page_title="RAG Chatbot", page_icon="🚀")

# Dynamic API URL (Local + Production support)
API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"  # Default for local development
)

# UI HEADER
st.title("🚀 RAG Assistant")
st.markdown("Ask questions based on your uploaded PDF knowledge base.")

# SIDEBAR - DOCUMENT UPLOAD

with st.sidebar:
    st.header(" Upload Knowledge")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if st.button("Process Document"):
        if uploaded_file:
            with st.spinner("Analyzing PDF in batches... this may take a minute."):
                try:
                    files = {
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf",
                        )
                    }

                    res = requests.post(f"{API_URL}/upload", files=files)

                    if res.status_code == 200:
                        st.success(res.json().get("info"))

                    elif res.status_code == 429:
                        st.warning(
                            "⚠ API quota exceeded. Please wait before uploading again."
                        )

                    else:
                        st.error(f"Error: {res.status_code} - {res.text}")

                except requests.exceptions.RequestException as e:
                    st.error(f" Connection failed: {e}")
        else:
            st.info("Please select a PDF file first.")

# MAIN CHAT INTERFACE

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What would you like to know?"):

    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            try:
                response = requests.post(
                    f"{API_URL}/chat",
                    json={"question": prompt},
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No response received.")
                    st.markdown(answer)

                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )

                elif response.status_code == 429:
                    st.warning(
                        "⚠ Google's free tier is busy. Please wait 30 seconds and try again."
                    )

                else:
                    st.error(
                        f"Error {response.status_code}: {response.text}"
                    )

            except requests.exceptions.RequestException as e:
                st.error(f" Connection failed: {e}")