import streamlit as st
import openai
import os
from dotenv import load_dotenv
import PyPDF2

# Load API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.set_page_config(page_title="🤖 AI Chatbot", page_icon="📄")
st.title("🤖 AI Chatbot")

# --- Toggle system prompt ---
show_prompt = st.sidebar.toggle("⚙️ Customize GPT")

default_prompt = "You are a helpful assistant that answers questions based on the uploaded file, or from general knowledge if no file is uploaded."
if show_prompt:
    system_prompt = st.sidebar.text_area("System Prompt", value=default_prompt)
else:
    system_prompt = default_prompt

# --- Reset Button ---
if st.sidebar.button("🔁 Reset Chat"):
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.rerun()

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# --- File Upload (Multiple files, button style) ---
with st.container():
    uploaded_files = st.file_uploader("Upload Files", type=["txt", "pdf"], accept_multiple_files=True, label_visibility="collapsed")

# --- Extract content from files ---
file_text = ""
if uploaded_files:
    contents = []
    for uploaded_file in uploaded_files:
        if uploaded_file.type == "text/plain":
            contents.append(uploaded_file.read().decode("utf-8"))
        elif uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            contents.append("\n".join([page.extract_text() or "" for page in reader.pages]))
    file_text = "\n\n".join(contents)

# --- Display previous messages ---
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User Input Box ---
user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if file_text:
        prompt = f"""The user uploaded one or more files with the following content:\n\n{file_text[:2000]}\n\nBased on the file(s), answer this question: {user_input}"""
    else:
        prompt = user_input

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        st.session_state.messages[0],  # system prompt
                        {"role": "user", "content": prompt}
                    ],
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"❌ OpenAI Error: {e}")
