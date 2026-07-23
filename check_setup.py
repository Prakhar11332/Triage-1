import requests
import cv2
import sys

print("=" * 50)
print("TriageAI — Setup Diagnostic")
print("=" * 50)

# ── 1. Hotspot / Ollama connection ───────────────────
print("\n[1] Checking Ollama connection...")
try:
    r = requests.get("http://localhost:11434/api/tags", timeout=5)
    if r.status_code == 200:
        models = [m["name"] for m in r.json().get("models", [])]
        print(f"  Ollama is running")
        if models:
            print(f"  Models available: {', '.join(models)}")
            if any("gemma" in m for m in models):
                print("    Gemma model found — ready for TriageAI")
            else:
                print("  No Gemma model found. Run: ollama pull gemma3:4b")
        else:
            print("  No models downloaded yet. Run: ollama pull gemma3:4b")
    else:
        print(f" Ollama responded with status {r.status_code}")
except requests.exceptions.ConnectionError:
    print("  Cannot reach Ollama at localhost:11434")
    print(" → Make sure Ollama is running: ollama serve")
except requests.exceptions.Timeout:
    print("  Ollama timed out — may be starting up, try again in a few seconds")

# ── 2. Camera check ──────────────────────────────────
print("\n[2] Checking camera...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("  Camera index 0 not found")
    print("  → Try index 1 or 2, or check USB/FaceTime camera permissions")
else:
    ret, frame = cap.read()
    if ret:
        h, w = frame.shape[:2]
        print(f" Camera working — frame size: {w}x{h}")
    else:
        print(" Camera opened but couldn't read a frame")
    cap.release()

print("\n" + "=" * 50)
print("Diagnostic complete.")
print("=" * 50)
