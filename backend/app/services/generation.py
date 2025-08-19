from transformers import pipeline
from app.services.optimization import generate_hashtags, generate_hooks

# Load a small local model
generator = pipeline("text-generation", model="distilgpt2")

# app/services/generation.py
from typing import List, Tuple

def derive_brand_voice(about: str) -> str:
    """
    Analyze user profile/about text and derive a 'brand voice'.
    """
    if "AI" in about:
        return "Analytical & Insightful"
    elif "marketing" in about:
        return "Creative & Engaging"
    return "Professional & Helpful"


def generate_post(topic: str, options: dict) -> Tuple[str, str, List[str]]:
    """
    Generate a post (title, body, tags) for a given topic.
    """
    title = f"Insights on {topic}"
    body = f"This post dives into {topic} with tone: {options.get('tone', 'neutral')}."
    tags = [topic.lower().replace(" ", ""), "growth", "trends"]
    return title, body, tags

