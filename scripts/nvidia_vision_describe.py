"""
Describe un lote de frames de video via NVIDIA NIM (meta/llama-3.2-90b-vision-instruct).
Uso: python nvidia_vision_describe.py <frames_dir> <api_key> <output_json>

Frames deben llamarse frame_NNN.jpg (orden = orden temporal). Si existe
un archivo frames_timestamps.txt junto al directorio (una linea por frame,
mm:ss), se usa para etiquetar cada descripcion con su timestamp real.

Reintenta hasta 2 veces si la respuesta es un rechazo de seguridad
(frecuente como falso positivo en capturas de trading/MT5).
"""
import base64
import json
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "meta/llama-3.2-90b-vision-instruct"
MAX_WORKERS = 5  # free tier NVIDIA NIM: 40 req/min, 5 en paralelo no lo excede
PROMPT = (
    "Describe en espanol, en maximo 6-8 frases y sin usar titulos ni listas con "
    "vinetas, que se ve en esta imagen de un video de trading/programacion de bots "
    "(EA, indicadores, fxDreema, backtest, MetaTrader). Menciona solo el texto en "
    "pantalla, codigo, parametros, graficos y valores que realmente puedas leer. "
    "Si no hay nada relevante de trading/codigo, dilo en una frase."
)

REFUSAL_MARKERS = [
    "no puedo proporcionar", "no puedo dar", "no puedo ayudar",
    "i can't provide", "i cannot provide", "i can't help", "cannot assist",
    "actividades ilegales", "illegal activities",
]


def describe_frame(path: Path, api_key: str, max_retries: int = 2) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}},
            ],
        }],
        "max_tokens": 350,
        "temperature": 0.3,
        "frequency_penalty": 0.4,
    }
    body = json.dumps(payload).encode("utf-8")

    last_text = ""
    for attempt in range(max_retries + 1):
        req = urllib.request.Request(
            API_URL, data=body,
            headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.load(resp)
            text = data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            text = "[error HTTP %s al describir el frame]" % e.code
            time.sleep(2)
            last_text = text
            continue
        except Exception as e:
            text = "[error de red al describir el frame: %s]" % e
            time.sleep(3)
            last_text = text
            continue
        last_text = text
        lowered = text.lower()
        if not any(m in lowered for m in REFUSAL_MARKERS):
            return text
        time.sleep(1.5)
    return "[descripcion no disponible: el modelo rechazo el frame %d veces]" % (max_retries + 1)


def main():
    frames_dir = Path(sys.argv[1])
    api_key = sys.argv[2]
    output_json = Path(sys.argv[3])

    frames = sorted(frames_dir.glob("frame_*.jpg"))
    timestamps_file = frames_dir / "frames_timestamps.txt"
    timestamps = []
    if timestamps_file.exists():
        timestamps = [l.strip() for l in timestamps_file.read_text(encoding="utf-8").splitlines() if l.strip()]

    results = [None] * len(frames)

    def worker(i_path):
        i, frame_path = i_path
        ts = timestamps[i] if i < len(timestamps) else None
        print("Describiendo %s (%d/%d)..." % (frame_path.name, i + 1, len(frames)), file=sys.stderr)
        # No dejar que un frame ilegible (borrado por otro proceso, corrupto, etc.)
        # tumbe el lote entero: se degrada a una nota de error por-frame.
        try:
            desc = describe_frame(frame_path, api_key)
        except FileNotFoundError:
            desc = "[frame no disponible: el archivo desaparecio antes de leerlo]"
        except Exception as e:
            desc = "[error al procesar el frame: %s]" % e
        return i, {"frame": frame_path.name, "timestamp": ts, "description": desc}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for i, result in pool.map(worker, enumerate(frames)):
            results[i] = result

    output_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK: %d frames descritos -> %s" % (len(results), output_json), file=sys.stderr)


if __name__ == "__main__":
    main()
