# AION Reel Editor — Skill reutilizable

Editor de reels estilo AION (estilo v13 bloqueado). Talking-head → reel vertical premium con captions estilo referencia, keywords gigantes, cortes de dead air, zoom viral y sound design.

Stack: **Remotion** (captions/composición) + **FFmpeg** (audio/SFX) + **faster-whisper** (transcripción).

## Requisitos (una vez)
- Node 18+ y `npm install` dentro de esta carpeta (instala Remotion + fuentes).
- FFmpeg en el PATH.
- Python con `faster-whisper` (para transcribir).

## Cómo editar un reel nuevo
1. Copia tu video a `public/source.mp4`.
2. Transcribe:  `python transcribe.py`  (usa `audio_16k.wav`; extráelo con
   `ffmpeg -i public/source.mp4 -vn -ac 1 -ar 16000 audio_16k.wav`)
3. Genera el plan de edición:  `python gen_edit.py`
   - Ajusta la lista `EMPHASIS` en `gen_edit.py` (palabra, t_min, t_max) para elegir
     qué keywords salen GIGANTES en este video. Números 2+ dígitos salen gigantes solos.
   - Corrige errores de transcripción en `gen_edit.py` (función `fix`).
4. **B-roll full-screen** (opcional, recomendado — da viralidad):
   - Edita `broll_plan.json`: 3-5 beats con `startFrame`, `durationInFrames` (~90-130 = 3-4s),
     y `image_prompt`/`motion_prompt` ATADOS a lo que dices en ese punto del guion.
   - `bash make_broll.sh`  → genera imagen (Nano Banana Pro 9:16) + anima (Kling 3.0 5s),
     descarga a `public/broll/` y cablea `src/edit.json`. (Usa la CLI `higgs`, NO `hf`.)
   - Regenerar solo algunos: `bash make_broll.sh 2 4`.
5. Render del video:  `npx remotion render src/index.ts AionEdit out/_base.mp4 --codec=h264 --crf=18`
6. Sound design + mezcla:  `bash build_final.sh out/_base.mp4 out/FINAL.mp4 [music.mp3]`
   - Edita los tiempos `WH` (whoosh en cortes y en cada transición de B-roll) e `IM`
     (impacto en keywords) en `build_final.sh` (los imprime `gen_edit.py` y `make_broll.sh`).

## Estilo bloqueado
Ver **STYLE_LOCK.md** — todos los parámetros exactos (fuente Plus Jakarta 800, blanco
uniforme estático, halo elegante, Playfair italic en gigantes, zoom alternado, SFX audibles).

## NO hacer (rechazado por Ricardo)
- ❌ Color grade (colores originales siempre)
- ❌ Card CTA de fondo oscuro
- ❌ SFX en sub-bass (inaudibles)
- ❌ B-roll en mockups generados (si se usa B-roll, material real)

## Archivos clave
- `src/Captions.tsx` — sistema de captions (normal + gigantes)
- `src/AionEdit.tsx` — composición + zoom/punch virales + **capa B-roll full-screen**
- `gen_edit.py` — cortes, caption pages, selección de gigantes
- `broll_plan.json` — plan de B-roll (beats + prompts) — editar por reel
- `make_broll.sh` — pipeline B-roll (Higgsfield CLI: Nano Banana Pro → Kling 3.0)
- `build_final.sh` — audio final (SFX + duck de voz + música opcional)
- `sfx/` — whoosh + impacto sintetizados
