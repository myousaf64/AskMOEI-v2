# Ask MOEI v2.0

A bilingual (English / Arabic) AI assistant for UAE Ministry of Energy & Infrastructure maritime services. Answers are grounded in the official MOEI knowledge base — the assistant will not invent fees, documents, or links. Covers 10 maritime services including vessel registration, seafarer certificates, port compliance, and more.

## Requirements

- Python 3.10+
- An [OpenRouter](https://openrouter.ai) API key

## How to run

```bash
pip install -r requirements.txt

cp .env.example .env
# Edit .env and add your OpenRouter API key

streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Environment variables

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter key — never commit `.env` |

## Knowledge base

The 10 MOEI maritime service manuals are not included in this repository.

Place the PDFs in `knowledge_base/`. The loader reads every `.pdf` and `.txt` file in
that folder, so any filename works. Without them the app still starts, but every answer
falls back to the portal link.

Open an issue or contact [@myousaf64](https://github.com/myousaf64) for the file list
and setup instructions.
