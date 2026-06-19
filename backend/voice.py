import os

# ── LAZY LOADING ──────────────────────────────────────────────────────────────
_whisper_model = None

def get_whisper():
    global _whisper_model
    if _whisper_model is None:
        import whisper
        print("Loading Whisper...")
        _whisper_model = whisper.load_model("base")
        print("✅ Whisper ready")
    return _whisper_model

def transcribe_audio(audio_path):
    model = get_whisper()
    result = model.transcribe(
        audio_path,
        language="en",
        fp16=False,
        verbose=False
    )
    return result["text"].strip()

def text_to_speech(text, output_path="response.mp3"):
    from gtts import gTTS
    tts = gTTS(text=text[:500], lang="en", slow=False)
    tts.save(output_path)
    return output_path