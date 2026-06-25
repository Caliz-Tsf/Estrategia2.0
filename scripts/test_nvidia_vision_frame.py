import base64
import json
import sys
import urllib.request

frame_path = sys.argv[1]
api_key = sys.argv[2]

with open(frame_path, "rb") as f:
    b64 = base64.b64encode(f.read()).decode("ascii")

payload = {
    "model": "meta/llama-3.2-90b-vision-instruct",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe en espanol que se ve en esta imagen de un video de trading/programacion de bots (EA, indicadores, fxDreema, backtest). Enfocate en texto en pantalla, codigo, parametros, graficos visibles."},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}}
        ]
    }],
    "max_tokens": 300
}

req = urllib.request.Request(
    "https://integrate.api.nvidia.com/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    },
    method="POST"
)

with urllib.request.urlopen(req) as resp:
    data = json.load(resp)

print(data["choices"][0]["message"]["content"])
