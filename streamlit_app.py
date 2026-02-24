import streamlit as st
import requests

st.set_page_config(page_title="RAG Chatbot", page_icon="🚀")

st.title("🚀 SpaceX & Tesla RAG Assistant")
st.markdown("Ask questions about Elon Musk's ventures based on our local database.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call FastAPI backend
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"question": prompt}
                )
                if response.status_code == 200:
                    answer = response.json().get("answer")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("Error: Could not reach backend.")
            except Exception as e:
                st.error(f"Connection failed: {e}")
with st.sidebar:
    st.header("Upload Knowledge")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
    if st.button("Process Document") and uploaded_file:
        with st.spinner("Analyzing PDF..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            res = requests.post("http://127.0.0.1:8000/upload", files=files)
            if res.status_code == 200:
                st.success(res.json()["info"])