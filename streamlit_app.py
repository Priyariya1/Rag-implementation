import streamlit as st
import requests

st.set_page_config(page_title="RAG Chatbot", page_icon="🚀")

st.title("🚀 RAG Assistant")
st.markdown("Ask questions about on our local database.")

# SIDEBAR- Document Upload 
with st.sidebar:
    st.header("Upload Knowledge")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
    
    if st.button("Process Document"):
        if uploaded_file:
            with st.spinner("Analyzing PDF in batches... this may take a minute."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    res = requests.post("http://127.0.0.1:8000/upload", files=files)
                    
                    if res.status_code == 200:
                        st.success(f" {res.json().get('info')}")
                    elif res.status_code == 429:
                        st.warning(" API Quota exceeded. Please wait 60 seconds before uploading more.")
                    else:
                        st.error(f"Error: {res.status_code}")
                except Exception as e:
                    st.error(f"Connection failed: {e}")
        else:
            st.info("Please select a PDF file first.")

# --- MAIN CHAT INTERFACE ---

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What would you like to know?"):
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
                
                # Error Handling logic
                elif response.status_code == 429:
                    error_msg = " Google's free tier is a bit busy. Please wait about 30 seconds and try again!"
                    st.warning(error_msg)
                else:
                    st.error(f"Error {response.status_code}: Could not get a response.")
                    
            except Exception as e:
                st.error(f"Connection failed: {e}")