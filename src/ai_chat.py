import requests

def ask_mistral(message, context=""):
    url = "http://localhost:11434/api/generate"
    
    full_prompt = f"""
You are Fail2LearnBot, an expert in failed chemical experiments.

Here is the context from real lab data:
{context}

Now answer the following user question clearly and scientifically:
{message}
"""

    payload = {
        "model": "mistral",
        "prompt": full_prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()["response"].strip()
        else:
            return "❌ Mistral did not respond properly."
    except:
        return "❌ Could not connect to Mistral. Is Ollama running?"
