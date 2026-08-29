import streamlit as st


def get_gemini_api_key():
    """Return the Gemini API key from Streamlit secrets."""
    return st.secrets["GEMINI_API_KEY"]


MODEL_NAME = "gemini-3.6-flash"

FALLBACK_MODEL = "gemini-3.5-flash-lite"