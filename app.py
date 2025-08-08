# LexLite AI Legal Assistant (MVP)
# Requirements: streamlit, openai, PyMuPDF

import streamlit as st
import fitz  # PyMuPDF
import openai

# --- CONFIGURATION ---
openai.api_key = st.secrets["OPENAI_API_KEY"]  # store your key securely in Streamlit Secrets
st.set_page_config(page_title="LexLite - Legal Doc AI", page_icon="📄", layout="centered")

# --- BASIC BRANDING ---
st.title("LexLite 🔖")
st.subheader("Your AI-Powered Legal Document Assistant")
st.markdown("""
Upload any contract or legal document (PDF), and LexLite will:
- Summarize it in plain English
- Let you ask questions like: *"What are the termination terms?"*
""")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload your legal document (PDF only)", type=["pdf"])

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text[:7000]  # limit input to avoid token overload

if uploaded_file:
    with st.spinner("Extracting text and analyzing with AI..."):
        doc_text = extract_text_from_pdf(uploaded_file)

        # --- AI SUMMARY ---
        summary_prompt = f"""
        Summarize the following legal document in plain English. Highlight key terms (termination, liability, confidentiality, etc.):

        {doc_text}
        """
        summary = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": summary_prompt}]
        )
        st.success("Summary Complete!")
        st.markdown("### 🔢 Document Summary")
        st.write(summary.choices[0].message.content)

        # --- Q&A ---
        st.markdown("---")
        st.markdown("### 🤔 Ask a Question About This Document")
        user_question = st.text_input("E.g. What are the confidentiality terms?")

        if user_question:
            qa_prompt = f"""
            Here's a legal document:
            {doc_text}

            Based on this text, answer the question: {user_question}
            """
            answer = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": qa_prompt}]
            )
            st.markdown("**Answer:**")
            st.write(answer.choices[0].message.content)

# --- FOOTER ---
st.markdown("---")
st.caption("LexLite AI © 2025 | For demonstration purposes only. Not legal advice.")
