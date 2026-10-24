# Acme AI Use Case Assessor

A simple Streamlit app that assesses AI use cases against
Acme Financial Services' 8 AI requirements (AI-001 to AI-008).

## Install

1. Create a virtual environment:
   ```
   python -m venv venv
   ```
2. Activate it:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Install the packages:
   ```
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and put your real OpenAI API key in it (`OPENAI_API_KEY`).

## Run

```
streamlit run app.py
```

The app opens in your browser at http://localhost:8501.
