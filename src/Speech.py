"""Text-to-speech for prediction results and treatment plans, via gTTS.

gTTS (Google Text-to-Speech) is a free, keyless wrapper around Google
Translate's speech endpoint -- no API key or account needed, matching the
app's other keyless integrations (Nominatim geocoding, Open-Meteo weather).
Its language codes line up directly with this app's lang keys ('hi'/'en').

A server-side engine was chosen over the browser's native SpeechSynthesis
API because it produces real, consistent audio regardless of the visiting
device/browser's installed voices -- important for Hindi, which many
browsers/OSes don't ship a voice for at all.
"""

import io
import re

from gtts import gTTS

_HEADER_RE = re.compile(r'^#{1,6}\s*', re.MULTILINE)
_EMPHASIS_RE = re.compile(r'\*{1,3}|_{1,3}')
_BULLET_RE = re.compile(r'^[ \t]*[-*•]\s+', re.MULTILINE)
_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]+",
    flags=re.UNICODE,
)
_WHITESPACE_RE = re.compile(r'[ \t]+')
_BLANK_LINES_RE = re.compile(r'\n{2,}')


def _plain_text(markdown_text):
    """Strip markdown syntax and emoji so the reader doesn't sound out symbols."""
    text = _HEADER_RE.sub('', markdown_text)
    text = _EMPHASIS_RE.sub('', text)
    text = _BULLET_RE.sub('', text)
    text = _EMOJI_RE.sub('', text)
    text = _WHITESPACE_RE.sub(' ', text)
    text = _BLANK_LINES_RE.sub('. ', text)
    return text.strip()


def synthesize_speech(text, lang='hi'):
    """Convert markdown or plain text to MP3 audio bytes.

    Returns None if synthesis fails (network error, empty text after
    stripping, etc) so callers can degrade gracefully -- e.g. hide the
    audio player and show a message -- instead of crashing the page.
    """
    plain = _plain_text(text)
    if not plain:
        return None
    try:
        tts = gTTS(text=plain, lang=lang)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        return buffer.getvalue()
    except Exception:
        return None
