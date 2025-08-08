# LexLite (Free Trial MVP) — Option 1: session-based usage limits
# Requirements: streamlit, openai, PyMuPDF
# Secrets: set OPENAI_API_KEY in Streamlit Secrets
# NOTE: This approach limits per browser session. It resets if the user refreshes/changes device.
# For real accounts & persistent limits, we’ll upgrade to Option 2 later.

import streamlit as st
import fitz  # PyMuPDF
import openai

# ---------- CONFIG ----------
st.set_page_config(page_title="LexLite AI", page_icon="⚖️", layout="centered")
openai.api_key = st.secrets["OPENAI_API_KEY"]

FREE_LIMIT = 3  # total AI actions allowed for free (summary or Q&A each counts as 1)
STRIPE_LINK = "https://buy.stripe.com/your-checkout-link"  # <-- put your Stripe Payment Link here

# ---------- STATE ----------
if "use_count" not in st.session_state:
    st.session_state.use_count = 0
if "doc_text" not in st.session_state:
    st.session_state.doc_text = None

# ---------- UI ----------
st.title("LexLite AI")
st.subheader("Your AI-Powered Legal Document Assistant")

st.caption("Free trial: **3 AI actions** (summaries or answers). Upgrade for unlimited use.")

# helper: show remaining usage / upgrade CTA
def usage_bar():
    remaining = max(0, FREE_LIMIT - st.session_state.use_count)
    st.progress(min(st.session_state.use_count / FREE_LIMIT, 1.0))
    st.info(f"Free actions left: **{remaining}** of {FREE_LIMIT}")
    if remaining == 0:
        st.error("You've reached the free trial limit.")
        st.markdown(f"[Upgrade to LexLite Pro →]({STRIPE_LINK})")

# ---------- FILE UPLOAD ----------
uploaded = st.file_uploader("Upload a legal document (PDF)", type=["pdf"])
if uploaded is not None and st.session_state.doc_text is None:
    with st.spinner("Extracting text..."):
        doc = fitz.open(stream=uploaded.read(), filetype="pdf")
        text_chunks = []
        for page in doc:
            text_chunks.append(page.get_text())
        # Keep first ~25k chars to avoid token overload but still handle longer docs
        st.session_state.doc_text = ("\n".join(text_chunks))[:25000]
    st.success("Document loaded!")

# ---------- ACTION GATE ----------
def can_use_ai():
    return st.session_state.use_count < FREE_LIMIT

def count_use():
    st.session_state.use_count += 1

# ---------- SUMMARY ----------
st.markdown("### 📝 Generate Summary")
if st.button("Summarize Document", disabled=st.session_state.doc_text is None):
    if not can_use_ai():
        usage_bar()
    else:
        with st.spinner("Summarizing with AI..."):
            prompt = f"""
Summarize this legal document in clear plain English.
Highlight key sections: parties, scope, term, termination, confidentiality, liability, IP, payment, governing law, and unusual risks.

Document:
{st.session_state.doc_text}
"""
            res = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # or gpt-4o if you prefer
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
        count_use()
        st.success("Summary ready.")
        st.markdown(res.choices[0].message.content)
        usage_bar()

# ---------- Q&A ----------
st.markdown("### 🤖 Ask a Question About This Document")
q = st.text_input("Example: What are the termination conditions?")
if st.button("Get Answer", disabled=not q or st.session_state.doc_text is None):
    if not can_use_ai():
        usage_bar()
    else:
        with st.spinner("Thinking..."):
            prompt = f"""
You are a legal assistant. Answer the user's question based strictly on the document below.
If the answer isn't in the text, say so briefly.

Document:
{st.session_state.doc_text}

Question: {q}
"""
            res = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
        count_use()
        st.markdown("**Answer:**")
        st.write(res.choices[0].message.content)
        usage_bar()

st.markdown("---")
st.caption("Demo only. Not legal advice. © LexLite 2025")
