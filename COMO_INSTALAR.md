# Cómo instalar el skill "Aion Reel Editor"

Este es un **skill de Claude Code**. Para usarlo:

## 1. Descomprime el zip
Vas a obtener la carpeta `aion-reel-editor`.

## 2. Muévela a tu carpeta de skills de Claude Code
- **Windows:** `C:\Users\TU_USUARIO\.claude\skills\`
- **Mac/Linux:** `~/.claude/skills/`

La ruta final debe quedar así: `.../.claude/skills/aion-reel-editor/SKILL.md`

## 3. Instala lo necesario (una sola vez)
Dentro de la carpeta del skill:
```
npm install
```
Y asegúrate de tener en tu sistema:
- **Node 18+** (para Remotion)
- **FFmpeg** en el PATH
- **Python** con `faster-whisper`  → `pip install faster-whisper`
- **Higgsfield CLI** autenticada (`higgs account status`) — solo si vas a usar B-roll con IA

## 4. Úsalo
Abre Claude Code y pídele editar/crear un reel. El skill se activa solo.
Lee `README.md` y `STYLE_LOCK.md` para el detalle del pipeline y el estilo.

> Nota: el zip NO incluye `node_modules` ni videos de ejemplo (por eso pesa poco).
> Tú trabajas con tus propios videos: cópialos a `public/source.mp4` y sigue el README.
