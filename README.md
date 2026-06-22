# NLP Sentiment Project

Bu proje, Streamlit ile bir duygu analiz arayüzü sunar. Gemini API yerine yerel kelime‑tabanlı (heuristic) analiz kullanılır, bu yüzden geçerli bir Google Gemini API anahtarına ihtiyaç yoktur.

## Çalıştırma
1. **Bağımlılıkları kurun**
   ```bash
   python -m pip install -r requirements.txt
   ```
2. **Uygulamayı başlatın**
   ```bash
   streamlit run streamlit_app.py
   ```
3. Tarayıcıda açılan sayfada metin girerek analiz yapabilirsiniz.

## Project Structure
- `backend/` – FastAPI server code and requirements.
- `frontend/` – Streamlit app code.
- `run_app.py` – Entry point to launch the full application.
- `requirements.txt` – Top‑level dependencies.
- `.env` – Environment variables (e.g., API keys).

## Notlar
- `google-generativeai` paketi hâlâ `requirements.txt` içinde bulunur, ancak kodda devre dışı bırakılmıştır.
- `.streamlit/secrets.toml` içinde bir placeholder API anahtarı bulunur; gerçek bir anahtar eklemek isterseniz kodu eski hâline döndürmeniz yeterlidir.

## Usage
- Open the Streamlit UI at `http://localhost:8501`.
- Use the FastAPI endpoints under `http://localhost:8000`.

## License
MIT License.
