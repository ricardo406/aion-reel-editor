<div align="center">

# 🎬 Aion Reel Editor

### Convierte un video hablando a cámara en un reel vertical premium estilo AION — automáticamente.

Captions blancos premium · keywords **GIGANTES** · cortes de aire muerto · zoom viral · sound design · capa de **B-roll** full-screen generada con IA.

**Skill para [Claude Code](https://claude.com/claude-code)** · Stack: Remotion + FFmpeg + faster-whisper + Higgsfield CLI

</div>

---

## ¿Qué hace?

Le das un **talking-head** (tú hablando a cámara) y te devuelve un **reel 9:16 listo para publicar**:

- ✂️ **Corta el aire muerto** automáticamente (transcribe con IA y elimina pausas/silencios).
- 🔤 **Captions premium** sincronizados al milisegundo, con **palabras clave GIGANTES** para frenar el scroll.
- 🎞️ **B-roll full-screen** generado con IA (Nano Banana Pro → Kling 3.0), atado a lo que dices en cada punto.
- 🔊 **Sound design**: whoosh en los cortes, mezcla limpia, música opcional.
- ⚡ **Zoom y punch virales** + salida acelerada para mantener el ritmo.

Todo el estilo está **bloqueado y calibrado** (ver [`STYLE_LOCK.md`](STYLE_LOCK.md)) para que cada reel salga consistente.

---

## 🚀 Instalación rápida

> Guía completa paso a paso para principiantes: **[`COMO_INSTALAR.md`](COMO_INSTALAR.md)**

1. **Descarga** el ZIP (botón verde `Code → Download ZIP`) y descomprime.
2. Mueve la carpeta `aion-reel-editor` a tu directorio de skills de Claude Code:
   - Windows: `C:\Users\TU_USUARIO\.claude\skills\`
   - Mac/Linux: `~/.claude/skills/`
3. Dentro de la carpeta, instala una sola vez:
   ```bash
   npm install
   ```
4. Abre Claude Code y pídele **editar/crear un reel**. El skill se activa solo.

### Requisitos
- **Node 18+** (Remotion) · **FFmpeg** en el PATH · **Python** con `faster-whisper` (`pip install faster-whisper`)
- **Higgsfield CLI** autenticada (`higgs account status`) — solo si vas a usar B-roll con IA

---

## 🎯 El pipeline (por cada reel)

1. Copia tu video a `public/source.mp4`.
2. Transcribe: `python transcribe.py` → `transcript.json`.
3. Genera la edición: `python gen_edit.py` → cortes, caption pages y keywords GIGANTES.
4. **B-roll (recomendado):** edita `broll_plan.json` y corre `bash make_broll.sh`.
5. Render: `npx remotion render src/index.ts AionEdit out/_base.mp4 --codec=h264 --crf=18`
6. Sound design final: `bash build_final.sh out/_base.mp4 out/FINAL.mp4 [music.mp3]`

Detalle completo en [`SKILL.md`](SKILL.md).

---

## 📦 Qué incluye este repo

Solo el **motor del skill** — código, scripts, instrucciones y SFX. **No** incluye `node_modules` (se instala con `npm install`) ni videos de ejemplo: tú trabajas con tus propios videos.

---

<div align="center">

Hecho con ☕ por **AION** · Sistema de edición de reels para creadores.

</div>
