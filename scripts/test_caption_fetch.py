"""
Prueba de velocidad: obtener transcripcion via captions de YouTube
(youtube-transcript-api) en vez de whisper. Solo mide tiempo y muestra
una porcion del resultado -- no escribe nada al vault.

Uso: python test_caption_fetch.py <video_id_or_url>
"""
import sys
import time

from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url_or_id: str) -> str:
    if "watch?v=" in url_or_id:
        return url_or_id.split("watch?v=")[1].split("&")[0]
    if "youtu.be/" in url_or_id:
        return url_or_id.split("youtu.be/")[1].split("?")[0]
    return url_or_id


def main():
    video_id = extract_video_id(sys.argv[1])
    print("Video ID: %s" % video_id)

    t0 = time.time()
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id, languages=["es", "en"])
    elapsed = time.time() - t0

    full_text = " ".join(snippet.text for snippet in transcript)
    word_count = len(full_text.split())

    print("Tiempo de fetch: %.2f s" % elapsed)
    print("Snippets: %d" % len(transcript))
    print("Palabras totales: %d" % word_count)
    print("Idioma detectado: %s" % transcript.language_code)
    print("--- primeros 500 caracteres ---")
    print(full_text[:500])


if __name__ == "__main__":
    main()
