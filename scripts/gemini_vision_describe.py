"""
Describe un lote de frames de video via Google Gemini 2.5 (vision), usando el
endpoint OpenAI-compatible de Gemini. Hermano de nvidia_vision_describe.py para
el A/B de calidad de descripcion (brazo C = Gemini vs brazo A/B = NVIDIA NIM).

Uso: python gemini_vision_describe.py <frames_dir> <api_key> <output_json> [modelo]

  modelo (opcional): gemini-2.5-flash (default) | gemini-2.5-pro

Frames deben llamarse frame_NNN.jpg (orden = orden temporal). Si existe un
archivo frames_timestamps.txt junto al directorio (una linea por frame, mm:ss),
se usa para etiquetar cada descripcion con su timestamp real.

Reintenta si la respuesta es un rechazo de seguridad (falso positivo frecuente
en capturas de trading/MT5) o si hay rate-limit (HTTP 429).
"""
import base64
import json
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

API_URL = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
DEFAULT_MODEL = "gemini-2.5-flash"
# Free tier de Gemini = 10 RPM. Serial (1 worker) + PACING_SEC entre llamadas
# mantiene el ritmo por debajo del limite y evita el 429 masivo. Sube MAX_WORKERS
# / baja PACING solo con tier pago.
MAX_WORKERS = 1
PACING_SEC = 5.0
PROMPT = (
    "Describe en espanol, en maximo 6-8 frases y sin usar titulos ni listas con "
    "vinetas, que se ve en esta imagen de un video de trading/programacion de bots "
    "(EA, indicadores, fxDreema, backtest, MetaTrader). Menciona solo el texto en "
    "pantalla, codigo, parametros, graficos y valores que realmente puedas leer. "
    "Se literal con el texto exacto que aparezca (nombres de bloques, condiciones, "
    "numeros). Si no hay nada relevante de trading/codigo, dilo en una frase."
)

REFUSAL_MARKERS = [
    "no puedo proporcionar", "no puedo dar", "no puedo ayudar",
    "i can't provide", "i cannot provide", "i can't help", "cannot assist",
    "actividades ilegales", "illegal activities",
]


def describe_frame(path: Path, api_key: str, model: str, max_retries: int = 3) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    payload = {
        "model": model,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": PROMPT},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}},
            ],
        }],
        "max_tokens": 600,
        "temperature": 0.3,
        # Gemini 2.5 Flash razona por defecto y el "thinking" consume el
        # presupuesto de max_tokens en imagenes complejas -> respuesta truncada.
        # reasoning_effort=none apaga el thinking (endpoint OpenAI-compat).
        "reasoning_effort": "none",
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
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.load(resp)
            text = data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            # 429 = rate limit -> backoff largo y reintentar.
            if e.code == 429:
                time.sleep(20 * (attempt + 1))
                last_text = "[error HTTP 429 (rate limit) al describir el frame]"
                continue
            detail = ""
            try:
                detail = e.read().decode("utf-8", "replace")[:200]
            except Exception:
                pass
            text = "[error HTTP %s al describir el frame] %s" % (e.code, detail)
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
        if text and not any(m in lowered for m in REFUSAL_MARKERS):
            return text
        time.sleep(1.5)
    return last_text or "[descripcion no disponible tras %d intentos]" % (max_retries + 1)


def main():
    frames_dir = Path(sys.argv[1])
    api_key = sys.argv[2]
    output_json = Path(sys.argv[3])
    model = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_MODEL

    frames = sorted(frames_dir.glob("frame_*.jpg"))
    timestamps_file = frames_dir / "frames_timestamps.txt"
    timestamps = []
    if timestamps_file.exists():
        timestamps = [l.strip() for l in timestamps_file.read_text(encoding="utf-8").splitlines() if l.strip()]

    results = [None] * len(frames)

    def worker(i_path):
        i, frame_path = i_path
        ts = timestamps[i] if i < len(timestamps) else None
        print("Describiendo %s (%d/%d) [gemini:%s]..." % (frame_path.name, i + 1, len(frames), model), file=sys.stderr)
        try:
            desc = describe_frame(frame_path, api_key, model)
        except FileNotFoundError:
            desc = "[frame no disponible: el archivo desaparecio antes de leerlo]"
        except Exception as e:
            desc = "[error al procesar el frame: %s]" % e
        # Pacing entre llamadas para respetar el limite de 10 RPM del free tier.
        if PACING_SEC > 0:
            time.sleep(PACING_SEC)
        return i, {"frame": frame_path.name, "timestamp": ts, "description": desc}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for i, result in pool.map(worker, enumerate(frames)):
            results[i] = result

    output_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("OK: %d frames descritos -> %s" % (len(results), output_json), file=sys.stderr)


if __name__ == "__main__":
    main()
