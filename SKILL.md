---
name: aion-reel-editor
description: Edita un talking-head en un reel vertical 9:16 estilo AION (estilo v13 bloqueado) con captions blancos premium, keywords GIGANTES, cortes de dead air, zoom viral, sound design y capa de B-roll full-screen generada con IA. Usar cuando Ricardo pida editar/crear un reel, agregar B-rolls a un video, o producir contenido vertical estilo AION. Stack: Remotion + FFmpeg + faster-whisper + Higgsfield CLI (Nano Banana Pro -> Kling 3.0).
---

# AION Reel Editor

Skill reutilizable para convertir un talking-head en un reel vertical premium estilo AION.

**Carpeta de trabajo:** esta carpeta del skill es autocontenida. Primer uso (una vez):
`npm install` aquí (Remotion + fuentes). Luego copia el video a `public/source.mp4` y sigue el
pipeline. `src/edit.json` incluido es un ejemplo (reel 0602); se sobrescribe por reel con `gen_edit.py`.
La carpeta NO incluye `node_modules`: en el primer uso corre `npm install` aquí dentro para instalarlos.

## Antes de tocar nada
Lee **STYLE_LOCK.md** (parámetros exactos, bloqueados — captions, gigantes, cortes, zoom,
sound design y reglas de B-roll) y respétalo. Lee **README.md** para el detalle de comandos.
No reintroducir nada de la lista "NO incluir" (color grade, card CTA, SFX sub-bass, B-roll
abstracto/CGI, B-roll en PiP). Escribe en español venezolano (tú).

## Pipeline por reel
1. Copiar el video a `public/source.mp4`.
2. `ffmpeg -i public/source.mp4 -vn -ac 1 -ar 16000 audio_16k.wav` → `python transcribe.py`
   (faster-whisper large-v3 → `transcript.json`).
3. `python gen_edit.py` → `src/edit.json` (cortes de dead air, caption pages, keywords GIGANTES).
   Ajustar la lista `EMPHASIS` (palabra, t_min, t_max) y la función `fix` (errores de transcripción).
4. **B-roll (recomendado — da viralidad):** editar `broll_plan.json` con 3-5 beats
   (`startFrame`, `durationInFrames` ~90-130 = 3-4s, `image_prompt`, `motion_prompt`) ATADOS
   al guion en ese punto → `bash make_broll.sh` (genera imagen Nano Banana Pro 9:16 → anima
   Kling 3.0 5s → descarga a `public/broll/` → cablea `edit.json`). Regenerar uno: `bash make_broll.sh 2`.
5. `npx remotion render src/index.ts AionEdit out/_base.mp4 --codec=h264 --crf=18`
6. Ajustar `WH` (whoosh: cortes + cada entrada/salida de B-roll) e `IM` (impacto: keywords) en
   `build_final.sh` → `bash build_final.sh out/_base.mp4 out/FINAL.mp4 [music.mp3]`.

## Reglas de B-roll (críticas — calibradas con Ricardo)
- **Full-screen 9:16 SIEMPRE** (mismo tamaño que sus reels de referencia; nunca PiP). La voz
  y los captions NO se cortan: B-roll muteado encima del talking-head, `<Captions>` por encima.
- Contenido **real, documental, cinematográfico y atado al tema**. NO CGI/hologramas/neón.
  **El "empleado nuevo" SIEMPRE humano, nunca robot/android.** Variar el ritmo humano ↔ sistema/terminal ↔ humano.
- Generación con CLI **`higgs`** (NO `hf`). Modelos: `nano_banana_2` (imagen) y `kling3_0` (video).

## Requisitos
Node + `npm install` (Remotion), FFmpeg en PATH, Python + faster-whisper, Higgsfield CLI
autenticada (`higgs account status`). Ver memorias [[project-aion-reel-editor-broll]] y [[reference-higgsfield-cli]].
