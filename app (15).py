import streamlit as st
import os
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import requests
import json
import matplotlib.pyplot as plt

# --- Page config
st.set_page_config(page_title="AI PDF & Image Assistant", page_icon="📄", layout="wide")

# --- Custom Dark Theme CSS & JS ---
dark_theme = """
<style>
/* Dark background and light text */
body, .stApp {
    background-color: #121212;
    color: #e0e0e0;
}

/* Titles */
h1, h2, h3, h4, h5, h6, label, .stMarkdown {
    color: #ffffff !important;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

/* Inputs & text areas */
.stTextArea textarea, .stTextInput input {
    background-color: #1e1e1e;
    color: #f0f0f0;
    border: 1px solid #444;
    border-radius: 8px;
    padding: 10px;
    font-size: 14px;
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #00c6ff, #0072ff);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: bold;
    transition: all 0.3s ease;
    cursor: pointer;
}
.stButton button:hover {
    background: linear-gradient(90deg, #0072ff, #00c6ff);
    transform: scale(1.05);
}

/* File uploader area */
[data-testid="stFileUploader"] {
    background-color: #1e1e1e;
    border: 2px dashed #444;
    border-radius: 10px;
    padding: 12px;
}
[data-testid="stFileUploader"] section button {
    background: linear-gradient(90deg, #00c6ff, #0072ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: bold !important;
    padding: 8px 16px !important;
    transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"] section button:hover {
    background: linear-gradient(90deg, #0072ff, #00c6ff) !important;
    transform: scale(1.05) !important;
}

/* Tabs */
.stTabs [role="tablist"] {
    gap: 12px;
}
.stTabs [role="tab"] {
    background-color: #1e1e1e !important;
    color: #f0f0f0 !important;
    border-radius: 8px;
    padding: 8px 16px;
    transition: background 0.3s ease;
}
.stTabs [role="tab"]:hover {
    background-color: #292929 !important;
}

/* Scrollbars */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-thumb {
    background: #444;
    border-radius: 8px;
}
</style>

<script>
// Fade-in effect for main title
document.addEventListener("DOMContentLoaded", function() {
    const title = document.querySelector("h1");
    if (title) {
        title.style.opacity = 0;
        setTimeout(() => {
            title.style.transition = "opacity 2s";
            title.style.opacity = 1;
        }, 300);
    }
});
</script>
"""
st.markdown(dark_theme, unsafe_allow_html=True)

# --- Load secrets
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
DEEPGRAM_API_KEY = st.secrets.get("DEEPGRAM_API_KEY") or os.getenv("DEEPGRAM_API_KEY")

if not GROQ_API_KEY or not DEEPGRAM_API_KEY:
    st.error("⚠️ API keys missing! Please set them in Hugging Face/Streamlit secrets.")
    st.stop()

# --- PDF extraction
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    return " ".join([p.extract_text() or "" for p in reader.pages])

# --- Image OCR
def extract_text_from_image(file):
    try:
        img = Image.open(file).convert("RGB")
        img = ImageOps.grayscale(img)
        img = img.filter(ImageFilter.MedianFilter())
        return pytesseract.image_to_string(img, lang="eng").strip()
    except pytesseract.TesseractNotFoundError:
        return "⚠️ OCR unavailable. Tesseract not found in this environment."

# --- Groq Summarization
def summarize_text(text, model="llama-3.1-8b-instant"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [
        {"role": "system", "content": "Summarize the text clearly."},
        {"role": "user", "content": text}
    ]}
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"❌ Error from Groq: {resp.text}"

# --- Groq Q&A
def ask_question(text, question, model="llama-3.1-8b-instant"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [
        {"role": "system", "content": "You are a helpful assistant. Use only the provided document text to answer."},
        {"role": "user", "content": f"Document:\n{text}\n\nQuestion: {question}"}
    ]}
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"❌ Error from Groq: {resp.text}"

# --- Table/Chart generation
def generate_table_or_chart(text, instruction, model="llama-3.1-8b-instant"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    if "chart" in instruction.lower():
        system_prompt = """You are a data extraction assistant.
        If the user asks for a chart, analyze the document and return ONLY valid JSON in this format:
        {"labels": ["label1", "label2"], "values": [10,20], "chart_type": "pie" or "bar"}
        No explanation, just raw JSON."""
    else:
        system_prompt = "When asked to make a table, return it in Markdown format."
    payload = {"model": model, "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Document:\n{text}\n\nInstruction: {instruction}"}
    ]}
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"❌ Error from Groq: {resp.text}"

# --- Deepgram TTS
def text_to_speech(text, voice="aura-asteria-en", filename="output.wav"):
    headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}", "Content-Type": "application/json"}
    url = f"https://api.deepgram.com/v1/speak?model={voice}"
    payload = {"text": text}
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        with open(filename, "wb") as f:
            f.write(resp.content)
        return filename
    else:
        st.error(f"❌ Deepgram error: {resp.text}")
        return None

# --- Sidebar
st.sidebar.header("⚙️ Settings")
selected_model = st.sidebar.selectbox("Groq Model", ["llama-3.1-8b-instant"], index=0)
voice_model = st.sidebar.selectbox("Deepgram Voice", ["aura-asteria-en", "aura-luna-en", "aura-stella-en"], index=0)

# --- Main UI
st.title("📄 AI PDF & Image Assistant")
st.caption("✨ Dark mode | Summarizer | Q&A | Tables | Charts | Audio 🎙️")

uploaded_file = st.file_uploader("📤 Upload PDF or Image", type=["pdf", "png", "jpg", "jpeg"])
if uploaded_file:
    ext = uploaded_file.name.split(".")[-1].lower()
    text = extract_text_from_pdf(uploaded_file) if ext == "pdf" else extract_text_from_image(uploaded_file)

    if text.strip():
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📑 Extracted Text", "📝 Summary", "💬 Q&A", "📊 Tables/Charts", "🎙️ Audio"])

        with tab1:
            st.text_area("Full Extracted Text", text, height=300)

        with tab2:
            if st.button("Summarize Document"):
                with st.spinner("Summarizing..."):
                    summary = summarize_text(text, model=selected_model)
                st.write(summary)

        with tab3:
            user_q = st.text_input("Ask a question about the document:")
            if user_q:
                with st.spinner("Finding answer..."):
                    answer = ask_question(text, user_q, model=selected_model)
                st.success(answer)

        with tab4:
            instruction = st.text_input("Ask for a table/chart (e.g., 'Create a pie chart of optimizers')")
            if instruction:
                with st.spinner("Generating..."):
                    result = generate_table_or_chart(text, instruction, model=selected_model)
                try:
                    data = json.loads(result)
                    labels, values, chart_type = data["labels"], data["values"], data.get("chart_type", "bar")
                    fig, ax = plt.subplots()
                    if chart_type == "pie":
                        ax.pie(values, labels=labels, autopct='%1.1f%%')
                        ax.set_title("Pie Chart")
                    else:
                        ax.bar(labels, values)
                        ax.set_title("Bar Chart")
                    st.pyplot(fig)
                except Exception:
                    st.markdown(result)

        with tab5:
            summary_text = st.text_area("Enter text to convert into speech:", value=text[:500])
            if st.button("Generate Audio"):
                with st.spinner("Generating speech..."):
                    audio_file = text_to_speech(summary_text, voice=voice_model)
                if audio_file:
                    st.audio(audio_file, format="audio/wav")
    else:
        st.warning("⚠️ No text detected in file.")











