# REFLECTION.md

## AI Usage
Used Claude Code throughout for scaffolding, prompt design, CSS, retrieval, and persistence. Overruled it on 2 key decisions: chose BM25 over vector embeddings to avoid extra dependencies, and hardcoded a 10-service URL catalog instead of letting the model generate links, eliminating an entire class of hallucinations.

## What I Built
- RAG pipeline over 10 official MOEI maritime PDFs, chunked at 500 words with 80-word overlap
- BM25 retrieval (K1=1.5, B=0.75) returning top 4 chunks per query
- GPT-4o-mini via OpenRouter at temperature=0.15 with json_object response format, 0 parse failures in testing
- 12-intent classifier routing to 1 of 10 verified direct MOEI service URLs
- Bilingual auto-detection (EN/AR) with RTL layout flip for Arabic responses
- 4 user profiles (Citizen, Resident, Business, Visitor) adjusting tone and detail level
- SQLite cross-session memory retaining up to 20 turns per session
- Admin analytics tab tracking queries, fallback rate, language split, and top intents over a 7-day window

## What I Plan to Add
- Semantic search using sentence-transformers and FAISS once the knowledge base grows beyond 50 documents
- Confidence threshold on the routing card, only showing the direct link when is_fallback is false
- OCR pass over PDFs to extract fees and required documents currently locked in images
- Persistent admin auth for multi-operator deployments
- Webhook to the live MOEI portal for real-time service availability
