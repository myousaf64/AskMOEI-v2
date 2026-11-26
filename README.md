# Ask MOEI v2.0

## What it is

A bilingual (English / Arabic) RAG assistant for UAE Ministry of Energy & Infrastructure
maritime services. Answers are grounded in the official MOEI knowledge base: the assistant
will not invent fees, documents, or links, and falls back to the portal link when the
knowledge base cannot answer. It covers 10 maritime services, including vessel
registration, renewal, deletion and mortgage, seafarer certificates, and port compliance.

## Demo

<!-- TODO: screenshot or GIF -->
![Ask MOEI chat](docs/demo.png)

## Stack

- **UI:** Streamlit (`app.py`), wide layout, with per-message EN/AR language badges.
- **Retrieval:** a hand-written BM25 index over the PDF knowledge base
  (`knowledge_base_loader.py`), with PDFs read by `pdfplumber`.
- **Generation:** an OpenAI-compatible client against OpenRouter (`llm_client.py`), which
  returns a structured answer with intent, service name, link and fallback flag.
- **Catalog:** the 10 services and their official links (`services_catalog.py`).
- **Sessions:** SQLite-backed history and analytics (`session_store.py`).
- Python >= 3.10, managed with [uv](https://docs.astral.sh/uv/).

## Quickstart

```bash
uv sync

cp .env.example .env
# Edit .env and add your OpenRouter API key

uv run streamlit run app.py
```

The app opens at `http://localhost:8501`.

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter key. Never commit `.env`. |

## Results

- Answers are retrieved by BM25 from the service manuals, then grounded by the model.
- When a query falls outside the knowledge base, the assistant returns the official portal
  link instead of a guess.
- Arabic and English queries are detected per message and answered in kind.

The 10 MOEI maritime service manuals are **not** included in this repository. Place the
PDFs in `knowledge_base/`; the loader reads every `.pdf` and `.txt` in that folder. Without
them the app still starts, but every answer falls back to the portal link. Open an issue or
contact [@myousaf64](https://github.com/myousaf64) for the file list.

## License

MIT. See [`LICENSE`](LICENSE).
