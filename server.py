from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
import base64
import uvicorn

app = FastAPI(title="TriageAI Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma4:latest"

PROMPT = """You are TriageAI, an emergency medical triage assistant trained on the START triage protocol.

A paramedic is showing you an injured patient. Analyze what you see and respond with:

1. TRIAGE COLOR: (RED / YELLOW / GREEN / BLACK)
2. REASON: (one sentence why)
3. IMMEDIATE ACTION: (one sentence what the paramedic should do right now)

Be direct. Lives depend on speed."""


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("index.html", "r") as f:
        return f.read()


@app.get("/hospitals.json")
async def serve_hospitals():
    return FileResponse("hospitals.json", media_type="application/json")


@app.post("/triage")
async def triage(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image_data = base64.b64encode(image_bytes).decode("utf-8")

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": PROMPT,
                "images": [image_data],
                "stream": False,
            },
            timeout=60,
        )
        result = response.json()
        return JSONResponse({"result": result.get("response", "No response from model")})
    except requests.exceptions.ConnectionError:
        return JSONResponse({"error": "Cannot reach Ollama. Is it running?"}, status_code=503)
    except requests.exceptions.Timeout:
        return JSONResponse({"error": "Ollama timed out. Try a smaller image."}, status_code=504)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)