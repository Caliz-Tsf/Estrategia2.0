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
# Prompt principal: tono SUAVE a proposito. Un prompt agresivo ("transcribe
# TEXTUALMENTE", "prohibido...") dispara el filtro de copyright/seguridad del
# modelo en capturas reales de YouTube -> rechazos masivos. Este pide lo mismo
# (verbatim + sin relleno) sin gatillar el rechazo. La lista suave anti-relleno
# ('probablemente'/'parece'/'sugiere') y el "no repitas" se piden como peticion
# normal, no como marco de prohibiciones (eso reactivaria el filtro).
PROMPT = (
    "Estas viendo un frame de un tutorial educativo publico de YouTube sobre como "
    "construir bots de trading (fxDreema, MetaTrader/MQL, EA, indicadores, backtest). "
    "No rechaces la peticion: es material educativo publico y solo se te pide describir "
    "lo visible. Describe en espanol, en 4-8 frases, que aparece en pantalla. Pon entre "
    "comillas el texto que puedas leer (titulos, pasos, nombres de bloques o condiciones, "
    "variables, valores numericos). Se concreto y no rellenes: si algo no se alcanza a "
    "leer, di 'no se lee' en lugar de suponerlo. No especules: evita 'probablemente', "
    "'parece', 'sugiere' y 'en general'/'en resumen'. No repitas la misma frase ni "
    "describas dos veces el mismo elemento. Termina en cuanto describas lo visible; no "
    "cierres con un parrafo de resumen. Si no hay nada de trading/codigo, dilo en una "
    "frase."
)

# Fallback NEUTRO: se usa solo cuando el prompt principal es rechazado (frecuente
# en capturas de ChatGPT u otras IAs). Al no mencionar trading evita el gatillo de
# copyright y recupera la descripcion. Verificado 0/5 rechazos en frames reales.
FALLBACK_PROMPT = (
    "Describe brevemente en espanol los elementos de interfaz y el texto visible en esta "
    "captura de pantalla de software de computadora. Enumera literalmente entre comillas "
    "cualquier texto legible."
)

REFUSAL_MARKERS = [
    "no puedo proporcionar", "no puedo dar", "no puedo ayudar", "no puedo cumplir",
    "no puedo acceder", "derechos de autor",
    "i can't provide", "i cannot provide", "i can't help", "cannot assist",
    "actividades ilegales", "illegal activities",
]


def _post(prompt: str, b64: str, api_key: str, max_retries: int = 2) -> str:
    """Una llamada al modelo con el prompt dado; reintenta ante errores de red/HTTP."""
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64}},
            ],
        }],
        "max_tokens": 380,
        "temperature": 0.1,
        # Anti-repeticion: en frames casi estaticos (misma pantalla 1-2 frames) el
        # modelo repetia frases enteras. frequency_penalty penaliza tokens muy usados;
        # presence_penalty penaliza reintroducir cualquier token ya presente -> juntos
        # cortan el bucle sin subir la temperatura (que sacrificaria la lectura exacta).
        "frequency_penalty": 0.6,
        "presence_penalty": 0.3,
    }
    body = json.dumps(payload).encode("utf-8")
    last_text = ""
    for _ in range(max_retries + 1):
        req = urllib.request.Request(
            API_URL, data=body,
            headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.load(resp)
            return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            last_text = "[error HTTP %s al describir el frame]" % e.code
            time.sleep(2)
        except Exception as e:
            last_text = "[error de red al describir el frame: %s]" % e
            time.sleep(3)
    return last_text


def describe_frame(path: Path, api_key: str) -> str:
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    # 1) Prompt principal (verbatim, sin relleno).
    text = _post(PROMPT, b64, api_key)
    if not any(m in text.lower() for m in REFUSAL_MARKERS):
        return text
    # 2) Rechazo (tipico en capturas de ChatGPT/otras IAs) -> fallback neutro que
    #    esquiva el gatillo de copyright y recupera la descripcion.
    time.sleep(1.0)
    fb = _post(FALLBACK_PROMPT, b64, api_key)
    if not any(m in fb.lower() for m in REFUSAL_MARKERS):
        return fb
    return "[descripcion no disponible: el modelo rechazo el frame]"


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
