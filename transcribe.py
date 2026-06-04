import json, sys
from faster_whisper import WhisperModel

import os
HERE = os.path.dirname(os.path.abspath(__file__))
AUDIO = os.path.join(HERE, "audio_16k.wav")
OUT = os.path.join(HERE, "transcript.json")

# large-v3 = max accuracy for Spanish; int8 keeps it runnable on CPU
print("Loading model large-v3 (int8)...", flush=True)
model = WhisperModel("large-v3", device="cpu", compute_type="int8")

print("Transcribing...", flush=True)
segments, info = model.transcribe(
    AUDIO,
    language="es",
    word_timestamps=True,
    vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=300),
    beam_size=5,
)

out = {"language": info.language, "duration": info.duration, "segments": [], "words": []}
full_text = []
for seg in segments:
    s = {"start": round(seg.start, 3), "end": round(seg.end, 3), "text": seg.text.strip()}
    out["segments"].append(s)
    full_text.append(seg.text.strip())
    if seg.words:
        for w in seg.words:
            out["words"].append({"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3)})
    print(f"[{seg.start:6.2f} -> {seg.end:6.2f}] {seg.text.strip()}", flush=True)

out["full_text"] = " ".join(full_text)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(out['words'])} words, {len(out['segments'])} segments to {OUT}", flush=True)
