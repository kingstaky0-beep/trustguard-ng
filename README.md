# TrustGuard NG 🇳🇬

AI-powered scam and suspicious-message analyzer for the ForgeHacks Online 2026 hackathon.

## MVP features

- Analyze suspicious SMS/WhatsApp/social-media text.
- Explain detected scam indicators.
- Produce a 0–100 risk score.
- Provide a clear recommended action.
- Optional OpenAI-powered analysis.
- Rule-based fallback when no API key is configured.
- Screenshot upload endpoint with optional OCR support.

## Project structure

```text
trustguard-ng/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── analyzer.py
│   │   └── models.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── .gitignore
└── README.md
```

## 1. Backend

```bash
cd backend
python -m venv .venv
```

Windows:
```bash
.venv\Scripts\activate
```

Linux/macOS:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and optionally add an OpenAI API key.

Run:
```bash
uvicorn app.main:app --reload --port 8000
```

API docs:
`http://127.0.0.1:8000/docs`

## 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite.

## AI configuration

The backend works without an API key using a deterministic rule-based detector. For the hackathon demo, configure:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.5
```

The current OpenAI Python SDK exposes the Responses API through `client.responses.create(...)`; keep the key server-side and never place it in the React frontend.

## Important product note

TrustGuard is a safety-assistance tool, not a guarantee that a message is legitimate or fraudulent. Users should independently verify important financial or account-related requests through official channels.
