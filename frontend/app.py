#frontend/app.py
import streamlit as st
import requests
import os
import pandas as pd
import time
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="Müşteri Duygu Analiz Paneli",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

API_KEY = os.getenv("API_KEY", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Inject premium CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* App header custom styling */
    .app-header {
        background: linear-gradient(135deg, #1f6feb 0%, #111e38 100%);
        padding: 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Section containers as premium cards */
    .premium-card {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Sentiment badges */
    .sentiment-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        font-size: 14px;
        text-align: center;
    }
    .badge-pos {
        background-color: rgba(46, 164, 79, 0.15);
        color: #3fb950;
        border: 1px solid rgba(46, 164, 79, 0.3);
    }
    .badge-neg {
        background-color: rgba(207, 34, 46, 0.15);
        color: #f85149;
        border: 1px solid rgba(207, 34, 46, 0.3);
    }
    
    /* Progress bar design */
    .custom-bar-container {
        background-color: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        height: 20px;
        width: 100%;
        overflow: hidden;
        margin: 15px 0;
        display: flex;
    }
    .custom-bar-pos {
        height: 100%;
        background: linear-gradient(90deg, #2ea44f, #3fb950);
        border-radius: 10px 0 0 10px;
        transition: width 0.6s ease;
    }
    .custom-bar-neg {
        height: 100%;
        background: linear-gradient(90deg, #cf222e, #f85149);
        border-radius: 0 10px 10px 0;
        transition: width 0.6s ease;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - API Configuration & Monitoring
with st.sidebar:
    st.image("https://img.icons8.com/nolan/96/artificial-intelligence.png", width=80)
    st.markdown("## Sistem Durumu")
    
    # Check Backend Health
    health_ok = False
    model_loaded = False
    latency = 0
    try:
        start_time = time.time()
        health_resp = requests.get(f"{BACKEND_URL}/health", timeout=3)
        latency = int((time.time() - start_time) * 1000)
        if health_resp.status_code == 200:
            health_ok = True
            model_loaded = health_resp.json().get("model_loaded", False)
    except Exception:
        health_ok = False
        
    if health_ok:
        if model_loaded:
            st.success("🟢 API Çevrimiçi")
            st.info(f"⚡ Gecikme: {latency} ms\n🤖 Model: DistilBERT hazır")
        else:
            st.warning("🟡 API Çevrimiçi (Model Yükleniyor...)")
    else:
        st.error("🔴 API Çevrimdışı (Bağlanılamadı)")
        
    st.divider()
    st.markdown("### Bağlantı Detayları")
    st.text_input("Backend URL", value=BACKEND_URL, disabled=True)
    st.text_input("API Anahtarı", value="••••••••••••" if API_KEY else "Tanımlanmadı", disabled=True)
    
    st.divider()
    st.caption("AI Destekli Yorum Analiz Sistemi v1.0")

# App Header
st.markdown("""
<div class="app-header">
    <h1 style="margin: 0; font-size: 32px; font-weight: 700;">🧠 AI Müşteri Yorum Analiz Sistemi</h1>
    <p style="margin: 5px 0 0 0; opacity: 0.85; font-size: 16px;">
        FastAPI ve DistilBERT modelleri ile desteklenen anlık duygu durum analiz paneli.
    </p>
</div>
""", unsafe_allow_html=True)

# Initialize Session State
if 'history' not in st.session_state:
    st.session_state.history = []

# Tabs for Single or Batch Mode
tab1, tab2, tab3 = st.tabs(["✍️ Tekli Yorum Analizi", "📁 Toplu Yorum Analizi (Batch)", "📜 Analiz Geçmişi"])

# 1. Single Comment Analysis
with tab1:
    st.markdown("### Tek Bir Metin Analiz Edin")
    text = st.text_area(
        "Müşteri yorumunu buraya yapıştırın veya yazın:",
        height=120,
        placeholder="Örn: Siparişim çok hızlı geldi, paketleme harikaydı. Çok memnun kaldım!"
    )
    
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        analyze_btn = st.button("Duygu Durumunu Analiz Et", use_container_width=True, type="primary")
        
    if analyze_btn:
        if not text.strip():
            st.warning("Lütfen geçerli bir metin girin.")
        elif not health_ok:
            st.error("Backend servisi aktif değil. Lütfen backend sunucusunu başlatın.")
        else:
            with st.spinner("Yapay zeka yorumu analiz ediyor..."):
                headers = {"x-api-key": API_KEY}
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/predict",
                        json={"text": text},
                        headers=headers,
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        pos_score = result["positive"]
                        neg_score = result["negative"]
                        
                        # Save to history
                        sentiment_label = "Pozitif 😊" if pos_score > neg_score else "Negatif 😔"
                        st.session_state.history.append({
                            "Tarih": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "Metin": text,
                            "Pozitif": pos_score,
                            "Negatif": neg_score,
                            "Sonuç": sentiment_label
                        })
                        
                        # UI Display
                        st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
                        st.markdown("#### Analiz Sonucu")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.metric("Pozitiflik Oranı", f"{pos_score:.2%}")
                        with c2:
                            st.metric("Negatiflik Oranı", f"{neg_score:.2%}")
                            
                        # Custom Visual Bar
                        pos_width = int(pos_score * 100)
                        neg_width = 100 - pos_width
                        st.markdown(f"""
                        <div class="custom-bar-container">
                            <div class="custom-bar-pos" style="width: {pos_width}%;"></div>
                            <div class="custom-bar-neg" style="width: {neg_width}%;"></div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if pos_score > neg_score:
                            st.markdown("<span class='sentiment-badge badge-pos'>Genel Duygu: POZİTİF 😊</span>", unsafe_allow_html=True)
                        else:
                            st.markdown("<span class='sentiment-badge badge-neg'>Genel Duygu: NEGATİF 😔</span>", unsafe_allow_html=True)
                            
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                    elif response.status_code == 401:
                        st.error("API Anahtarı hatası (Unauthorized). Lütfen .env dosyasındaki API_KEY'i kontrol edin.")
                    else:
                        st.error(f"API Hatası (Kod: {response.status_code}): {response.text}")
                except Exception as e:
                    st.error(f"Bağlantı Hatası: {e}")

# 2. Batch Comment Analysis
with tab2:
    st.markdown("### Dosya Yükleyerek Toplu Analiz Edin")
    st.write("Desteklenen formatlar: `.csv` (tek sütunlu veya 'text'/'yorum' başlığı olan) veya `.txt` (satır satır yorumlar).")
    
    uploaded_file = st.file_uploader("Dosya Seçin", type=["csv", "txt"])
    
    if uploaded_file is not None:
        try:
            comments = []
            if uploaded_file.name.endswith(".csv"):
                df_upload = pd.read_csv(uploaded_file)
                # Find the column containing comments
                col_name = None
                for col in df_upload.columns:
                    if col.lower() in ['text', 'yorum', 'comment', 'review', 'mesaj', 'metin']:
                        col_name = col
                        break
                if col_name is None:
                    col_name = df_upload.columns[0] # Fallback to first column
                
                comments = df_upload[col_name].dropna().astype(str).tolist()
            else: # .txt file
                comments = [line.decode("utf-8").strip() for line in uploaded_file if line.decode("utf-8").strip()]
                
            st.success(f"Başarıyla {len(comments)} yorum yüklendi.")
            
            if st.button("Toplu Analizi Başlat", type="primary"):
                if not health_ok:
                    st.error("Backend sunucusu çevrimdışı.")
                else:
                    results = []
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    headers = {"x-api-key": API_KEY}
                    
                    for i, comment in enumerate(comments):
                        status_text.text(f"Analiz ediliyor ({i+1}/{len(comments)})...")
                        try:
                            response = requests.post(
                                f"{BACKEND_URL}/predict",
                                json={"text": comment},
                                headers=headers,
                                timeout=10
                            )
                            if response.status_code == 200:
                                res = response.json()
                                pos = res["positive"]
                                neg = res["negative"]
                                verdict = "Pozitif 😊" if pos > neg else "Negatif 😔"
                                results.append({
                                    "Yorum": comment,
                                    "Pozitif (%)": f"{pos:.2%}",
                                    "Negatif (%)": f"{neg:.2%}",
                                    "Duygu Durumu": verdict
                                })
                            else:
                                results.append({
                                    "Yorum": comment,
                                    "Pozitif (%)": "Hata",
                                    "Negatif (%)": "Hata",
                                    "Duygu Durumu": f"Hata ({response.status_code})"
                                })
                        except Exception as e:
                            results.append({
                                "Yorum": comment,
                                "Pozitif (%)": "Bağlantı Hatası",
                                "Negatif (%)": "Bağlantı Hatası",
                                "Duygu Durumu": "Hata"
                            })
                        
                        # Update progress
                        progress_bar.progress((i + 1) / len(comments))
                    
                    status_text.text("Toplu analiz tamamlandı!")
                    df_results = pd.DataFrame(results)
                    
                    # Display metrics summary
                    pos_count = sum(1 for r in results if "Pozitif" in r["Duygu Durumu"])
                    neg_count = sum(1 for r in results if "Negatif" in r["Duygu Durumu"])
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Toplam Analiz", len(comments))
                    col2.metric("Pozitif Yorum sayısı", pos_count)
                    col3.metric("Negatif Yorum sayısı", neg_count)
                    
                    # Display Table
                    st.dataframe(df_results, use_container_width=True)
                    
                    # Download results
                    csv = df_results.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Sonuçları CSV Olarak İndir",
                        data=csv,
                        file_name='duygu_analiz_sonuclari.csv',
                        mime='text/csv',
                    )
        except Exception as e:
            st.error(f"Dosya okuma hatası: {e}")

# 3. History Section
with tab3:
    st.markdown("### Analiz Geçmişi")
    if not st.session_state.history:
        st.info("Henüz analiz yapmadınız. Yorumlarınızı analiz ettikçe burada listelenecektir.")
    else:
        df_hist = pd.DataFrame(st.session_state.history)
        st.dataframe(df_hist, use_container_width=True)
        
        if st.button("Geçmişi Temizle"):
            st.session_state.history = []
            st.rerun()
