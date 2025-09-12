import streamlit as st
import os
from pypdf import PdfReader
from PIL import Image, ImageOps, ImageFilter
import pytesseract
import requests
import json
import matplotlib.pyplot as plt

# --- Page config
st.set_page_config(page_title="✨ PDF Vibes ✨", page_icon="🔥", layout="wide")

# --- Gen Z Theme CSS ---
genz_theme = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --primary-bg: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --secondary-bg: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    --accent-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    --neon-pink: #ff006e;
    --neon-blue: #00f5ff;
    --neon-purple: #8338ec;
    --dark-surface: #1a1a2e;
    --darker-surface: #16213e;
    --glass-bg: rgba(255, 255, 255, 0.1);
}

body, .stApp {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
    font-family: 'Inter', sans-serif !important;
    color: #ffffff !important;
}

/* Glassmorphism containers */
.main .block-container {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(20px) !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 2rem !important;
    margin-top: 1rem !important;
}

/* Neon text effects */
h1 {
    background: var(--accent-gradient) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: 800 !important;
    font-size: 3rem !important;
    text-align: center !important;
    text-shadow: 0 0 30px rgba(79, 172, 254, 0.5) !important;
    margin-bottom: 0.5rem !important;
}

h2, h3, h4, h5, h6 {
    color: var(--neon-blue) !important;
    font-weight: 600 !important;
    text-shadow: 0 0 10px rgba(0, 245, 255, 0.3) !important;
}

/* Caption with emojis */
.stApp > div > div > div > div > div:nth-child(2) {
    text-align: center !important;
    font-size: 1.2rem !important;
    background: var(--secondary-bg) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    font-weight: 500 !important;
    margin-bottom: 2rem !important;
}

/* Cyberpunk buttons */
.stButton button {
    background: var(--accent-gradient) !important;
    color: white !important;
    border: none !important;
    border-radius: 15px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3) !important;
    position: relative !important;
    overflow: hidden !important;
}

.stButton button:hover {
    transform: translateY(-3px) scale(1.05) !important;
    box-shadow: 0 15px 40px rgba(79, 172, 254, 0.5) !important;
    background: var(--secondary-bg) !important;
}

.stButton button:before {
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: -100% !important;
    width: 100% !important;
    height: 100% !important;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
    transition: left 0.5s !important;
}

.stButton button:hover:before {
    left: 100% !important;
}

/* Neon input fields */
.stTextInput input, .stTextArea textarea {
    background: rgba(26, 26, 46, 0.8) !important;
    border: 2px solid var(--neon-purple) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px rgba(131, 56, 236, 0.2) !important;
}

.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--neon-pink) !important;
    box-shadow: 0 0 30px rgba(255, 0, 110, 0.4) !important;
    outline: none !important;
}

/* File uploader glow */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 2px dashed var(--neon-blue) !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
    backdrop-filter: blur(10px) !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--neon-pink) !important;
    box-shadow: 0 0 40px rgba(0, 245, 255, 0.2) !important;
    transform: scale(1.02) !important;
}

[data-testid="stFileUploader"] section button {
    background: var(--primary-bg) !important;
    color: white !important;
    border: none !important;
    border-radius: 15px !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
}

[data-testid="stFileUploader"] section button:hover {
    background: var(--secondary-bg) !important;
    transform: translateY(-2px) scale(1.05) !important;
    box-shadow: 0 12px 35px rgba(240, 147, 251, 0.5) !important;
}

/* Holographic tabs */
.stTabs [role="tablist"] {
    background: rgba(255, 255, 255, 0.05) !important;
    backdrop-filter: blur(15px) !important;
    border-radius: 15px !important;
    padding: 8px !important;
    margin-bottom: 2rem !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.stTabs [role="tab"] {
    background: transparent !important;
    color: rgba(255, 255, 255, 0.7) !important;
    border-radius: 10px !important;
    padding: 12px 20px !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: none !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

.stTabs [role="tab"][aria-selected="true"] {
    background: var(--accent-gradient) !important;
    color: white !important;
    box-shadow: 0 8px 25px rgba(79, 172, 254, 0.4) !important;
    transform: translateY(-2px) !important;
}

.stTabs [role="tab"]:hover:not([aria-selected="true"]) {
    background: rgba(255, 255, 255, 0.1) !important;
    color: white !important;
    transform: translateY(-1px) !important;
}

/* Sidebar styling */
.css-1d391kg {
    background: rgba(22, 33, 62, 0.9) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.stSelectbox > div > div {
    background: rgba(26, 26, 46, 0.8) !important;
    border: 2px solid var(--neon-purple) !important;
    border-radius: 10px !important;
    color: white !important;
}

/* Success/Error messages with glow */
.stSuccess {
    background: rgba(0, 255, 127, 0.1) !important;
    border: 1px solid #00ff7f !important;
    border-radius: 12px !important;
    box-shadow: 0 0 20px rgba(0, 255, 127, 0.2) !important;
}

.stError {
    background: rgba(255, 0, 110, 0.1) !important;
    border: 1px solid var(--neon-pink) !important;
    border-radius: 12px !important;
    box-shadow: 0 0 20px rgba(255, 0, 110, 0.2) !important;
}

.stWarning {
    background: rgba(255, 193, 7, 0.1) !important;
    border: 1px solid #ffc107 !important;
    border-radius: 12px !important;
    box-shadow: 0 0 20px rgba(255, 193, 7, 0.2) !important;
}

/* Spinner animation */
.stSpinner {
    border-color: var(--neon-blue) var(--neon-pink) var(--neon-purple) var(--neon-blue) !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px !important;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
}

::-webkit-scrollbar-thumb {
    background: var(--accent-gradient) !important;
    border-radius: 10px !important;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--secondary-bg) !important;
}

/* Floating animation */
@keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
    100% { transform: translateY(0px); }
}

.floating {
    animation: float 3s ease-in-out infinite !important;
}

/* Pulse animation for important elements */
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(79, 172, 254, 0.7); }
    70% { box-shadow: 0 0 0 10px rgba(79, 172, 254, 0); }
    100% { box-shadow: 0 0 0 0 rgba(79, 172, 254, 0); }
}

.pulse {
    animation: pulse 2s infinite !important;
}
</style>
"""

st.markdown(genz_theme, unsafe_allow_html=True)

# --- Load secrets from Hugging Face environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

if not GROQ_API_KEY or not DEEPGRAM_API_KEY or not HF_TOKEN:
    st.error("⚠️ Yo, we're missing some API keys! Set GROQ_API_KEY, DEEPGRAM_API_KEY, HF_TOKEN in your Hugging Face secrets 💯")
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
        return "⚠️ OCR is down rn. Tesseract not vibing in this environment 😔"

# --- Groq Summarization
def summarize_text(text, model="llama-3.1-8b-instant"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [
        {"role": "system", "content": "Summarize this text in a clear, concise way that hits different 💯"},
        {"role": "user", "content": text}
    ]}
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"❌ Groq ain't responding: {resp.text}"

# --- Groq Q&A
def ask_question(text, question, model="llama-3.1-8b-instant"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": [
        {"role": "system", "content": "You're the AI bestie that gives straight answers based on the document. Keep it real! 🔥"},
        {"role": "user", "content": f"Document:\n{text}\n\nQuestion: {question}"}
    ]}
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"❌ Groq's not cooperating rn: {resp.text}"

# --- Table/Chart generation
def generate_table_or_chart(text, instruction, model="llama-3.1-8b-instant"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    if "chart" in instruction.lower():
        system_prompt = """Return ONLY valid JSON that slaps:
        {"labels": ["label1", "label2"], "values": [10,20], "chart_type": "pie" or "bar"}"""
    else:
        system_prompt = "When asked for a table, make it clean with Markdown format that looks fire 🔥"
    payload = {"model": model, "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Document:\n{text}\n\nInstruction: {instruction}"}
    ]}
    resp = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"❌ Groq's having a moment: {resp.text}"

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
        st.error(f"❌ Deepgram said nah: {resp.text}")
        return None

# --- Hugging Face Diffusion Image Generation
def generate_image_from_prompt(prompt, model="stabilityai/stable-diffusion-2"):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    api_url = f"https://api-inference.huggingface.co/models/{model}"
    payload = {"inputs": prompt}
    response = requests.post(api_url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"❌ HF API is acting sus: {response.text}")
        return None

# --- Sidebar with more personality
st.sidebar.header("⚙️ Customize Your Vibe")
st.sidebar.markdown("*Make it yours bestie* ✨")

selected_model = st.sidebar.selectbox("🧠 AI Brain", ["llama-3.1-8b-instant"], index=0)
voice_model = st.sidebar.selectbox("🎤 Voice Vibes", ["aura-asteria-en", "aura-luna-en", "aura-stella-en"], index=0)
diffusion_model = st.sidebar.selectbox("🎨 Art Generator", [
    "stabilityai/stable-diffusion-2",
    "runwayml/stable-diffusion-v1-5"
], index=0)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Pro tip:** Upload any PDF or image and watch the magic happen!")

# --- Main UI with Gen Z flair
st.markdown('<div class="floating">', unsafe_allow_html=True)
st.title("🔥 PDF BESTIE 🔥")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<p style="text-align: center; font-size: 1.2rem; margin-bottom: 2rem;">✨ Your AI sidekick for docs • No cap just facts • Aesthetic vibes only ✨</p>', unsafe_allow_html=True)

# File uploader with Gen Z messaging
uploaded_file = st.file_uploader("📤 Drop your files here bestie", type=["pdf", "png", "jpg", "jpeg"], help="PDFs and images are welcome! ✨")

if uploaded_file:
    ext = uploaded_file.name.split(".")[-1].lower()
    
    with st.spinner("✨ Reading your file... this is about to be iconic ✨"):
        text = extract_text_from_pdf(uploaded_file) if ext == "pdf" else extract_text_from_image(uploaded_file)

    if text.strip():
        # Tabs with emojis and Gen Z language
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📖 RAW TEXT", "💎 TLDR", "💬 ASK ME", "📊 VISUALS", "🎵 AUDIO", "🎨 AI ART"
        ])

        with tab1:
            st.markdown("### The full tea ☕")
            st.text_area("Everything we found in your file:", text, height=300)

        with tab2:
            st.markdown("### Get the summary that hits different 💯")
            if st.button("✨ SUMMARIZE IT ✨", key="summarize"):
                with st.spinner("🧠 AI is cooking up your summary..."):
                    summary = summarize_text(text, model=selected_model)
                st.success("**Here's the tea:**")
                st.write(summary)

        with tab3:
            st.markdown("### Ask your questions bestie! 🤔")
            user_q = st.text_input("What do you wanna know?", placeholder="e.g., What's the main point of this doc?")
            if user_q:
                with st.spinner("🔍 Finding the perfect answer..."):
                    answer = ask_question(text, user_q, model=selected_model)
                st.success("**AI spilled the facts:**")
                st.write(answer)

        with tab4:
            st.markdown("### Make it visual! 📊")
            instruction = st.text_input("Tell me what chart/table you want:", placeholder="Create a pie chart of the main topics")
            if instruction:
                with st.spinner("🎨 Creating something beautiful..."):
                    result = generate_table_or_chart(text, instruction, model=selected_model)
                try:
                    # Try to parse as JSON for charts
                    data = json.loads(result)
                    labels, values, chart_type = data["labels"], data["values"], data.get("chart_type", "bar")
                    
                    # Create matplotlib chart with dark theme
                    plt.style.use('dark_background')
                    fig, ax = plt.subplots(figsize=(10, 6))
                    fig.patch.set_facecolor('#1a1a2e')
                    ax.set_facecolor('#1a1a2e')
                    
                    if chart_type == "pie":
                        colors = ['#ff006e', '#8338ec', '#3a86ff', '#06ffa5', '#ffbe0b']
                        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors[:len(values)])
                        ax.set_title("Your Data Visualization ✨", color='white', fontsize=16, pad=20)
                    else:
                        bars = ax.bar(labels, values, color=['#ff006e', '#8338ec', '#3a86ff', '#06ffa5', '#ffbe0b'][:len(values)])
                        ax.set_title("Your Data Visualization 📊", color='white', fontsize=16, pad=20)
                        ax.tick_params(colors='white')
                        
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()
                except Exception:
                    # If not JSON, display as markdown table
                    st.markdown("**Your table is ready! 📋**")
                    st.markdown(result)

        with tab5:
            st.markdown("### Turn text into audio vibes 🎵")
            summary_text = st.text_area("Text to turn into speech:", value=text[:500], help="Pro tip: Shorter text = faster audio!")
            if st.button("🎤 MAKE IT SPEAK", key="tts"):
                with st.spinner("🎵 Creating your audio masterpiece..."):
                    audio_file = text_to_speech(summary_text, voice=voice_model)
                if audio_file:
                    st.success("**Your audio is ready! 🔥**")
                    st.audio(audio_file, format="audio/wav")

        with tab6:
            st.markdown("### AI Art Generator 🎨")
            user_prompt = st.text_area("Describe the image you want:", 
                                     value="A futuristic cityscape with neon lights and flying cars", 
                                     help="Be descriptive! The more details, the better the art ✨")
            if st.button("🎨 CREATE ART", key="image_gen"):
                with st.spinner("🎨 AI artist is working their magic..."):
                    img_bytes = generate_image_from_prompt(user_prompt, model=diffusion_model)
                if img_bytes:
                    st.success("**Your AI art is fire! 🔥**")
                    st.image(img_bytes, caption="Generated with AI ✨", use_column_width=True)
    else:
        st.warning("🤔 Hmm, couldn't find any text in that file. Try a different one?")
else:
    # Welcome message when no file is uploaded
    st.markdown("""
    <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.05); 
                backdrop-filter: blur(10px); border-radius: 20px; margin: 2rem 0;">
        <h3 style="color: #00f5ff; margin-bottom: 1rem;">Ready to process your files? 🚀</h3>
        <p style="color: rgba(255,255,255,0.8); font-size: 1.1rem;">
            Upload a PDF or image above and I'll help you:<br>
            📝 Summarize the content<br>
            💬 Answer questions about it<br>
            📊 Create charts and tables<br>
            🎵 Convert text to speech<br>
            🎨 Generate AI artwork<br><br>
            <strong style="color: #ff006e;">Let's make some magic happen! ✨</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)











