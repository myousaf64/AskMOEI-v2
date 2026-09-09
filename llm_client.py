"""
llm_client.py
OpenRouter (OpenAI-compatible) API client.
Returns a structured dict: answer, intent, service_name, service_link, nudges, is_fallback.
"""

import os
import json
import re
from openai import OpenAI
from services_catalog import find_service, catalog_summary, FALLBACK_URL


# ── Valid intent values ────────────────────────────────────────────────────────
VALID_INTENTS = {
    "vessel_registration", "vessel_renewal", "vessel_deletion", "vessel_mortgage",
    "boat_renewal", "license_inquiry", "fee_inquiry", "document_inquiry",
    "seafarer", "port_compliance", "general", "out_of_scope",
}


def _client(custom_key: str = "") -> OpenAI:
    # Priority: custom_key (session) > OPENROUTER_API_KEY (env) > OPENAI_API_KEY (env)
    key = custom_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    return OpenAI(
        api_key=key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/myousaf64/AskMOEI-v2",
            "X-Title": "Ask MOEI v2.0",
        },
    )


def _system_prompt(user_profile: str) -> str:
    catalog = catalog_summary()
    return f"""You are Ask MOEI v2.0 — the official bilingual AI assistant for the UAE Ministry of Energy & Infrastructure, specialising in maritime services.

USER PROFILE: {user_profile}

AVAILABLE SERVICES (from the official knowledge base):
{catalog}

STRICT RULES:
1. Answer ONLY from the CONTEXT passages provided. Never invent fees, document names, or links.
2. If the context does not contain sufficient information, set is_fallback to true and say so clearly and politely.
3. Detect the user's language: reply in Arabic if they write in Arabic, English otherwise.
4. Tone: Citizens get plain, reassuring language. Businesses get formal, structured detail. Residents and Visitors get clear guidance assuming less familiarity.
5. Structure every answer: (a) direct answer, (b) what is needed / required info, (c) next step / how to apply.
6. All services are applied for via https://www.moei.gov.ae — guide the user through Services Directory → Maritime Transportation.

RESPONSE: return ONLY valid JSON — no markdown fences, no prose outside the object:
{{
  "answer": "<plain text answer in the user's language>",
  "intent": "<one of: vessel_registration|vessel_renewal|vessel_deletion|vessel_mortgage|boat_renewal|license_inquiry|fee_inquiry|document_inquiry|seafarer|port_compliance|general|out_of_scope>",
  "service_name": "<short English name of the matched service, or null>",
  "service_key": "<exact key from the service list above, e.g. pleasure_boat_renewal, or null>",
  "nudges": ["<follow-up suggestion max 8 words>", "<follow-up suggestion max 8 words>"],
  "is_fallback": <true|false>
}}

NUDGES: anticipate the user's next logical step. Max 2. If Arabic query, write nudges in Arabic too.
"""


def _user_prompt(query: str, chunks: list[dict], history: list[dict]) -> str:
    ctx = (
        "\n\n---\n\n".join(f"[Source: {c['name']}]\n{c['text']}" for c in chunks)
        if chunks else "No relevant documents found in the knowledge base."
    )
    hist = (
        "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in history[-6:]
        )
        if history else ""
    )
    return f"""CONTEXT FROM KNOWLEDGE BASE:
{ctx}

RECENT CONVERSATION:
{hist}

USER QUESTION: {query}

Return valid JSON only."""


def ask_moei(
    query: str,
    context_chunks: list[dict],
    chat_history: list[dict],
    user_profile: str = "Citizen",
    custom_api_key: str = "",
) -> dict:
    """Call the LLM and return a normalised result dict. Never raises."""
    is_arabic = bool(re.search(r"[؀-ۿ]", query))

    try:
        client = _client(custom_key=custom_api_key)
        resp = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": _system_prompt(user_profile)},
                {"role": "user",   "content": _user_prompt(query, context_chunks, chat_history)},
            ],
            temperature=0.15,
            max_tokens=900,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content.strip()
        data = json.loads(raw)

    except json.JSONDecodeError:
        data = {"answer": raw, "intent": "general", "is_fallback": True}
    except Exception as exc:
        msg = (
            "عذراً، حدث خطأ في الاتصال. يرجى المحاولة مرة أخرى أو زيارة موقع موي."
            if is_arabic
            else f"Sorry, I'm unable to connect right now. Please try again or visit moei.gov.ae. ({str(exc)[:80]})"
        )
        return {
            "answer":       msg,
            "intent":       "error",
            "service_name": None,
            "service_link": FALLBACK_URL,
            "nudges":       [],
            "is_fallback":  True,
        }

    # Validate intent
    intent = data.get("intent", "general")
    if intent not in VALID_INTENTS:
        intent = "general"

    # Resolve service from catalog — prefer LLM's service_key, fall back to keyword match
    service_key = data.get("service_key") or ""
    from services_catalog import SERVICES
    service = SERVICES.get(service_key) or find_service(query=query, intent=intent)

    return {
        "answer":       data.get("answer", "I'm sorry, I couldn't generate a response."),
        "intent":       intent,
        "service_name": data.get("service_name") or (service["name"] if service else None),
        "service_link": service["url"] if service else FALLBACK_URL,
        "nudges":       (data.get("nudges") or [])[:2],
        "is_fallback":  bool(data.get("is_fallback", False)),
    }
