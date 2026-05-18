# Invoice Review Agent

Litestar + SvelteKit app that uploads invoice files, extracts document evidence locally, asks LLM to produce structured invoice JSON, validates the result with Pydantic, and gives the user a review screen before saving.

## Stack

- Backend: Python, Litestar, Pydantic, httpx
- Frontend: SvelteKit, TypeScript, Vite
- AI provider: OpenRouter chat completions
- Default model: `deepseek/deepseek-v4-flash`
- Storage: SQLite for local demo persistence
- Document extraction: text decode, `pdfplumber` for PDF text/tables, PyMuPDF PDF rendering, Tesseract OCR through `pytesseract`

## Project Structure

```text
backend/
  pyproject.toml
  .env.example
  src/invoice_agent/
    app.py
    routes/
    services/
    repositories/
    document/
    llm/
  data/

frontend/
  .env.example
  src/
    routes/
    lib/
      api/
      components/
      types/
```

## Setup

Create your env file:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Set your OpenRouter key:

```bash
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=deepseek/deepseek-v4-flash
OPENROUTER_REFERER=http://localhost:5173
FRONTEND_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
MAX_UPLOAD_BYTES=10485760
```

Frontend API URL is configured in `frontend/.env`:

```bash
PUBLIC_API_BASE_URL=http://localhost:8000
```

Install backend dependencies:

```bash
python3 -m venv backend/.venv
backend/.venv/bin/pip install --upgrade pip
backend/.venv/bin/pip install --upgrade setuptools
backend/.venv/bin/pip install -e backend
```

For image OCR and scanned PDF OCR, install the Tesseract system binary.

macOS:

```bash
brew install tesseract
```

Windows:

```powershell
winget install UB-Mannheim.TesseractOCR
```

If `winget` is unavailable, install the Windows build from the UB Mannheim Tesseract project, then add the install directory to `PATH`.

Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

Verify the binary is available:

```bash
tesseract --version
```

Install frontend dependencies:

```bash
cd frontend
npm install
```

## Run Locally

Backend:

```bash
PYTHONPATH=backend/src backend/.venv/bin/uvicorn invoice_agent.app:app --host 0.0.0.0 --port 8000
```

Frontend:

```bash
cd frontend
npm run dev
```

Open `http://localhost:5173` and upload `samples/acme-invoice.txt`, a text-based PDF, or an image invoice if Tesseract is installed.

## Verification

Backend tests:

```bash
PYTHONPATH=backend/src backend/.venv/bin/python -m unittest discover -s backend/tests -v
```

Frontend check:

```bash
cd frontend
npm run check
```

## Architecture

```text
SvelteKit UI
  -> Litestar API
  -> document evidence extraction
       -> text decode for .txt
       -> pdfplumber for PDF text and tables
       -> PyMuPDF + Tesseract for scanned PDFs
       -> Pillow + Tesseract for image invoices
  -> OpenRouter DeepSeek extraction call
  -> defensive JSON parsing
  -> Pydantic invoice model validation
  -> local draft storage
  -> human review and correction
```

The document layer collects evidence; the LLM layer interprets that evidence into invoice fields. Model output is treated as untrusted: the backend asks for JSON, extracts the first JSON object if the model wraps it in text, validates it with Pydantic, and returns warnings for review.
