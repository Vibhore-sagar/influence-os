# app/services/optimization.py
import random

def generate_hashtags(topic: str):
    base = [
        "#AI", "#ArtificialIntelligence", "#MachineLearning", "#DeepLearning",
        "#DataScience", "#Tech", "#Innovation", "#FutureOfWork",
        "#AITrends", "#Productivity"
    ]
    random.shuffle(base)
    candidates = base[:8]
    best = candidates[:random.randint(3, 5)]
    return candidates, best

def generate_hooks(topic: str):
    hook_a = f"Ever wondered about {topic}? 🤔"
    hook_b = f"Here’s what nobody tells you about {topic} 👇"
    return [hook_a, hook_b]
