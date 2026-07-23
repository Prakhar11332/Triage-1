import requests
import base64

# Load your image and convert it to base64
# (this is how we send images to AI models)
with open("/Users/prakhargoyal/Desktop/test.jpg", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

# This is the prompt — what we're asking Gemma to do
prompt = """You are TriageAI, an emergency medical triage assistant trained on the START triage protocol.

A paramedic is showing you an injured patient. Analyze what you see and respond with:

1. TRIAGE COLOR: (RED / YELLOW / GREEN / BLACK)
2. REASON: (one sentence why)
3. IMMEDIATE ACTION: (one sentence what the paramedic should do right now)

Be direct. Lives depend on speed."""

# Send image + prompt to Gemma running in Ollama
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "gemma4:latest",
        "prompt": prompt,
        "images": [image_data],
        "stream": False
    }
)

# Print the result

result = response.json()
print("\n--- FULL RESPONSE ---")
print(result)  # this shows us everything Ollama sent back
print("--------------------\n")