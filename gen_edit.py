import json, re, unicodedata, os
HERE = os.path.dirname(os.path.abspath(__file__))

FPS = 30
W, H = 1080, 1920
GAP_MAX = 0.60      # solo cortar pausas claramente muertas (fin de frase/clip).
                    # Subido de 0.34: micro-pausas dentro de una frase (0.38-0.52s,
                    # p.ej. "informacion, necesite") NO se cortan -> sin saltos raros
                    # mientras habla.
GAP_KEEP = 0.16     # keep natural breathing room so sections don't feel clipped
TAIL_KEEP = 0.12    # trailing silence after last word

src = json.load(open(os.path.join(HERE, "transcript.json"), encoding="utf-8"))
words = src["words"]

# --- fix transcription errors for this reel (modelos de IA = ajedrez) ---
def fix(t):
    t = re.sub(r"\baderezo\b", "ajedrez", t, flags=re.IGNORECASE)
    t = re.sub(r"\bhikook\b", "Haiku", t, flags=re.IGNORECASE)
    t = re.sub(r"\bhaikook\b", "Haiku", t, flags=re.IGNORECASE)
    return t
for w in words:
    w["w"] = fix(w["w"])

# --- manual cuts: remove retake/duplicate speech (original seconds) ---
# Sin tomas dobles en este reel: el cierre "...ejecuta con tus caballos de
# guerra. Si quieres aprender mas sobre IA, sigueme" es habla continua unica.
MANUAL_CUTS = []

# Override de cola por corte (orig seconds del fin de palabra saliente, tail).
# "...tarea que realmente era extremadamente simple de hacer." (hacer. ~61.19):
# cortar justo al terminar la palabra para no mostrar la mano bajando a poner la pieza.
MANUAL_TAIL = [
    (61.0, 61.4, -0.14),   # cortar en ~61.05, apenas dicho "hacer": elimina el
                           # gesto de la mano hacia el telefono que viene despues.
]
def in_cut(t):
    return any(a <= t < b for a, b in MANUAL_CUTS)
words = [w for w in words if not in_cut(w["start"])]

# --- build keep intervals (original seconds) + cumulative removed offset ---
keep = []
seg_start = words[0]["start"]
cum = 0.0
out_words = []
for i, w in enumerate(words):
    if i > 0:
        g = w["start"] - words[i-1]["end"]
        if g > GAP_MAX:
            # cut here: close current interval, jump to this word.
            # Pausa larga (>0.8s) = fin de clip / corte de grabacion: recorta la
            # cola muerta mas pegado (0.07) para que el final de cada toma quede
            # limpio. Pausa corta = respiracion natural, deja un poco mas de aire.
            end_t = words[i-1]["end"]
            tail = 0.04 if g > 0.8 else 0.08   # mas apretado: menos espacio en las pausas
            # override por corte: "...simple de hacer" -> cortar justo al terminar
            # la palabra (antes de que baje la mano a poner la pieza).
            for a, b, tv in MANUAL_TAIL:
                if a <= end_t <= b:
                    tail = tv
                    break
            cut_end = end_t + tail
            keep.append([round(seg_start, 3), round(cut_end, 3)])
            seg_start = w["start"]
            cum += (g - tail)
    out_words.append({
        "text": w["w"],
        "os": round(w["start"] - cum, 3),
        "oe": round(max(w["end"] - cum, w["start"] - cum + 0.05), 3),
    })
# final interval with trailing trim
last_end = words[-1]["end"] + TAIL_KEEP
keep.append([round(seg_start, 3), round(last_end, 3)])

out_dur = sum(b - a for a, b in keep)
duration_frames = round(out_dur * FPS)

# --- segments for OffthreadVideo (trim original, place back-to-back) ---
segments = []
cursor = 0
for a, b in keep:
    dur = round((b - a) * FPS)
    segments.append({
        "fromFrame": cursor,
        "durationInFrames": dur,
        "trimBefore": round(a * FPS),
    })
    cursor += dur

# --- GIANT emphasis beats (senior-editor pick): word + original-time window ---
def norm(t):
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", t.lower())

# Reel "modelos de IA = ajedrez": no malgastes tu reina en trabajo de peon.
EMPHASIS = [
    ("ajedrez",  3.2, 4.0),    # hook: usar IA es igual a jugar ajedrez
    ("reina",    5.0, 5.8),    # tesis: no uses tu REINA como un peon
    ("peon",    24.0, 24.9),   # payoff tarea simple: "un texto, PEON"
    ("reina",   35.0, 35.9),   # payoff tarea compleja: "seguridad maxima, REINA"
    ("opus",    43.3, 44.3),   # spotlight del modelo caro que NO debes malgastar
    ("caballos",89.4, 90.4),   # cierre: "ejecuta con tus caballos de guerra"
]
def is_emph(orig_text, orig_start):
    # Sin auto-gigante de numeros: las versiones de modelo (5.5/4.8/4.5/4.0)
    # se amontonan 42-50s y ensucian. Solo gigantes elegidos a mano.
    n = norm(orig_text)
    for w, lo, hi in EMPHASIS:
        if n == w and lo <= orig_start <= hi:
            return True
    return False

# attach original start to out_words for emphasis lookup
for i, w in enumerate(out_words):
    w["orig_start"] = words[i]["start"]

# --- chunk words into caption pages (emphasis words become their own page) ---
PAGE_MAX_WORDS = 3
PAGE_MAX_DUR = 1.4
END_PUNCT = (".", "?", "!", ":")
pages = []          # each: {"emphasis": bool, "words": [...]}
cur = []
def flush():
    global cur
    if cur:
        pages.append({"emphasis": False, "words": cur})
        cur = []
for w in out_words:
    if is_emph(w["text"], w["orig_start"]):
        flush()
        pages.append({"emphasis": True, "words": [w]})
        continue
    cur.append(w)
    txt = w["text"]
    dur = cur[-1]["oe"] - cur[0]["os"]
    ends_sentence = txt.endswith(END_PUNCT)
    ends_clause = txt.endswith(",")
    if (len(cur) >= PAGE_MAX_WORDS or ends_sentence or dur >= PAGE_MAX_DUR
            or (ends_clause and len(cur) >= 2)):
        flush()
flush()

caption_pages = []
for idx, pg in enumerate(pages):
    wlist = pg["words"]
    start_f = round(wlist[0]["os"] * FPS)
    if idx + 1 < len(pages):
        end_f = round(pages[idx+1]["words"][0]["os"] * FPS)
    else:
        end_f = round(wlist[-1]["oe"] * FPS) + 14
    words_out = []
    for w in wlist:
        sf = round(w["os"] * FPS)
        ef = max(round(w["oe"] * FPS), sf + 1)
        txt = w["text"]
        if pg["emphasis"]:                       # gigantes limpios, sin puntuacion final
            txt = txt.strip(".,;:!?¿¡")
        words_out.append({"text": txt, "startFrame": sf, "endFrame": ef})
    caption_pages.append({
        "startFrame": start_f, "endFrame": end_f,
        "emphasis": pg["emphasis"], "words": words_out,
    })

# --- ensure GIANT keywords hold long enough to read (min ~0.6s) ---
MIN_GIANT = 18  # frames
for i, p in enumerate(caption_pages):
    if not p.get("emphasis"):
        continue
    want_end = p["startFrame"] + MIN_GIANT
    if p["endFrame"] >= want_end:
        continue
    p["endFrame"] = want_end
    j = i + 1
    while j < len(caption_pages) and caption_pages[j]["startFrame"] < want_end:
        if caption_pages[j]["endFrame"] <= want_end:
            caption_pages[j]["_drop"] = True  # fully covered, remove
            j += 1
        else:
            caption_pages[j]["startFrame"] = want_end  # resume right after giant
            break
caption_pages = [p for p in caption_pages if not p.get("_drop")]

edit = {
    "fps": FPS, "width": W, "height": H,
    "source": "source.mp4",
    "durationInFrames": duration_frames,
    "segments": segments,
    "captionPages": caption_pages,
}
json.dump(edit, open(os.path.join(HERE, "src", "edit.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print(f"Original duration: {src['duration']:.2f}s")
print(f"Output duration:   {out_dur:.2f}s  ({duration_frames} frames)")
print(f"Trimmed:           {src['duration']-out_dur:.2f}s of dead air")
print(f"Keep intervals:    {len(keep)}  -> {keep}")
print(f"Caption pages:     {len(caption_pages)}")
