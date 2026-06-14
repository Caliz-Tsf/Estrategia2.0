"""
fw_transcribe.py -- faster-whisper wrapper para process-video.ps1
Uso: python fw_transcribe.py <audio> --model <model> [--language <lang>] --output_dir <dir>
Salida: <output_dir>/<stem>.txt con la transcripcion completa.
"""
import argparse
import io
import sys
from pathlib import Path

# Forzar stdout UTF-8 para evitar UnicodeEncodeError en consola Windows (cp1252)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('audio', help='Ruta al archivo de audio (WAV)')
    p.add_argument('--model', default='small',
                   choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'])
    p.add_argument('--language', default=None, help='Codigo de idioma (ej: es, en). None=autodetectar')
    p.add_argument('--output_dir', default='.', help='Directorio donde se escribe el .txt')
    p.add_argument('--device', default='cuda', choices=['cuda', 'cpu'])
    p.add_argument('--compute_type', default='float16',
                   choices=['float16', 'int8_float16', 'int8', 'float32'])
    args = p.parse_args()

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print('[fw] ERROR: faster-whisper no instalado. Ejecuta: pip install faster-whisper', flush=True)
        sys.exit(1)

    print(f'[fw] Cargando modelo {args.model} en {args.device} ({args.compute_type})...', flush=True)
    try:
        model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    except Exception as e:
        if args.device == 'cuda':
            print(f'[fw] CUDA no disponible ({e}), reintentando en CPU...', flush=True)
            model = WhisperModel(args.model, device='cpu', compute_type='int8')
        else:
            print(f'[fw] ERROR cargando modelo: {e}', flush=True)
            sys.exit(1)

    lang_arg = args.language if args.language else None
    print(f'[fw] Transcribiendo {args.audio} (idioma={lang_arg or "auto"})...', flush=True)

    def run_transcription(m):
        segs, inf = m.transcribe(args.audio, language=lang_arg, beam_size=5)
        print(f'[fw] Idioma detectado: {inf.language} (prob={inf.language_probability:.2f})', flush=True)
        parts = []
        for seg in segs:  # iteracion lazy — CUDA error ocurre aqui
            text = seg.text.strip()
            if text:
                parts.append(text)
                print(f'[fw] [{seg.start:6.1f}s] {text}', flush=True)
        return parts

    text_parts = None
    try:
        text_parts = run_transcription(model)
    except (RuntimeError, Exception) as e:
        if 'cublas' in str(e).lower() or 'cuda' in str(e).lower() or 'cudnn' in str(e).lower():
            print(f'[fw] CUDA runtime error ({e}). Reintentando en CPU int8...', flush=True)
            from faster_whisper import WhisperModel as WM
            model_cpu = WM(args.model, device='cpu', compute_type='int8')
            text_parts = run_transcription(model_cpu)
        else:
            print(f'[fw] ERROR en transcripcion: {e}', flush=True)
            sys.exit(1)

    full_text = '\n'.join(text_parts or [])

    stem = Path(args.audio).stem
    out_path = Path(args.output_dir) / f'{stem}.txt'
    out_path.write_text(full_text, encoding='utf-8')
    print(f'[fw] Listo. Texto guardado en: {out_path}', flush=True)
    print(f'[fw] Total caracteres: {len(full_text)}', flush=True)


if __name__ == '__main__':
    main()
