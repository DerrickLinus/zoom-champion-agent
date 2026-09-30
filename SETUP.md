# Hongshan Companion setup

## 1. Configure Bailian

Copy `backend/.env.example` to `backend/.env` and fill in `DASHSCOPE_API_KEY`.
Keep this file private. It is ignored by Git.

The current defaults use the Bailian compatible OpenAI endpoint and `qwen-plus`.
The story agent may take up to 90 seconds because it generates route-specific chapters.
Voice transcription uses `paraformer-v2` and accepts a short, time-limited HTTPS audio URL through `/api/voice/transcribe`. The frontend language switch supports Chinese and English contexts; the English knowledge corpus still needs official bilingual content review before production.

## 2. Start the backend

```powershell
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Check `http://127.0.0.1:8765/health` and confirm `bailian_enabled` is `true`.

## 3. Start the frontend

Copy `.env.example` to `.env.local` if the backend is not running at the default URL.

```powershell
npm install
npm run dev
```

Open the Vite URL shown in the terminal. The frontend must be able to reach the backend URL in `VITE_API_BASE`.

## 4. Important security note

Never put `DASHSCOPE_API_KEY` in the frontend `.env.local` or commit `backend/.env`.
