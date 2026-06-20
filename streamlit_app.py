import streamlit as st
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv

# Load environment variables (for local testing)
load_dotenv()

# Set Page Config
st.set_page_config(
    page_title="AI Duygu Analizi",
    page_icon="🧠",
    layout="centered"
)

# API Configuration
# On Streamlit Cloud, we use st.secrets. Locally, we use .env
API_KEY = st.secrets.get("API_KEY") or os.getenv("API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
    HAS_GEMINI = True
else:
    HAS_GEMINI = False

# Header Design
st.title("🧠 AI Sentiment Analysis (Duygu Analizi)")
st.markdown("""
Bu uygulama, girdiğiniz metnin duygu durumunu (Pozitif/Negatif) yapay zeka kullanarak analiz eder.
Google Gemini AI desteği ile güçlendirilmiştir.
""")

# Input Section
text_input = st.text_area(
    "Analiz edilecek metni girin:",
    height=150,
    placeholder="Örn: Bugün hava çok güzel, kendimi harika hissediyorum!"
)

def get_gemini_sentiment(text):
    if not HAS_GEMINI:
        return None
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Analyze the sentiment of the following text and return ONLY a JSON response in this format:
        {{"positive": score, "negative": score}}
        where score is a float between 0 and 1.

        Text: "{text}"
        """
        response = model.generate_content(prompt)
        content = response.text
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        st.error(f"Gemini API Hatası: {e}")
    return None

def heuristic_analysis(text):
    text_lower = text.lower()
    positive_words = ["iyi", "güzel", "harika", "sevindim", "mutlu", "aşk", "seviyorum", "başarılı", "good", "great", "happy", "love"]
    negative_words = ["kötü", "berbat", "üzgün", "nefret", "başarısız", "korkunç", "bad", "terrible", "sad", "hate"]

    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    total = pos_count + neg_count
    if total == 0:
        return {"positive": 0.5, "negative": 0.5, "method": "Kelime Analizi (Nötr)"}

    pos_score = pos_count / total
    return {"positive": pos_score, "negative": 1.0 - pos_score, "method": "Kelime Analizi (Heuristic)"}

# Analysis Trigger
if st.button("Duygu Durumunu Analiz Et", use_container_width=True):
    if not text_input.strip():
        st.warning("Lütfen bir metin girin.")
    else:
        with st.spinner("Yapay Zeka analiz ediyor..."):
            result = None
            method = "Gemini AI"

            if HAS_GEMINI:
                result = get_gemini_sentiment(text_input)
                if not result:
                    result = heuristic_analysis(text_input)
                    method = result["method"]
            else:
                result = heuristic_analysis(text_input)
                method = result["method"]

        # Results Display
        st.divider()
        st.success(f"Analiz Tamamlandı (Yöntem: {method})")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pozitiflik", f"{result['positive']:.2%}")
        with col2:
            st.metric("Negatiflik", f"{result['negative']:.2%}")

        # Final Verdict
        if result['positive'] > result['negative']:
            st.info("Bu metin genel olarak **Pozitif** bir duygu taşıyor. 😊")
        elif result['positive'] < result['negative']:
            st.info("Bu metin genel olarak **Negatif** bir duygu taşıyor. 😔")
        else:
            st.info("Bu metin **Nötr** bir duygu taşıyor. 😐")

# Footer
st.divider()
st.caption("Geliştiren: Betül Altınkaynak Demirel | Streamlit Cloud Deployment Ready")
