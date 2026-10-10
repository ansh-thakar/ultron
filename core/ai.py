import os
import requests
import streamlit as st

SYSTEM_PROMPT = (
    "You are ULTRON, an academic analytics assistant built into a student "
    "management system. You help students and teachers understand attendance, "
    "marks, performance trends, and study data. Be concise, use plain English, "
    "and format answers with short bullet points when helpful."
)

MODEL = "gemini-3.5-flash"


def _key():
    try:
        return st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    except Exception:
        return os.environ.get("GEMINI_API_KEY")


def ask_ultron(question, data_context=""):
    key = _key()
    if not key:
        return "⚠️ API key missing in secrets.toml"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={key}"
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"parts": [{"text": f"Data:\n{data_context}\n\nQ: {question}"}]}],
        "generationConfig": {"temperature": 0.6, "maxOutputTokens": 800},
    }

    try:
        r = requests.post(url, json=payload, timeout=20)
        if r.status_code == 200:
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        return f"❌ HTTP {r.status_code}"
    except Exception as e:
        return f"❌ {e}"