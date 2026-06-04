# AION Reel Style Lock — v13 (2026-06-02)

Estilo oficial de edición de reels de Ricardo, calibrado contra 3 reels de referencia.

## Captions (estilo referencia, clonado frame-por-frame)
- Fuente base: **Plus Jakarta Sans 800** (grotesca ancha+bold, 'g' de un piso — NO Inter).
- Color: **blanco sólido UNIFORME** `#FFFFFF`. CERO colores, CERO atenuado de palabras.
- **ESTÁTICO**: la frase aparece con fade rápido (3 frames) y NO se mueve. SIN karaoke, SIN escala, SIN drift. La referencia es 100% estática → lo "pro" es la contención.
- Tamaño **50px**. Posición `top: 55%` (centrado, como la referencia).
- Sombra halo suave parejo (no stroke, no offset duro):
  `0 0 12px rgba(0,0,0,0.55), 0 0 22px rgba(0,0,0,0.32), 0 2px 5px rgba(0,0,0,0.55)`
- Páginas: máx 3 palabras / 1.4s, corte por puntuación.

## Keywords GIGANTES (firma de Ricardo)
- Fuente: **Playfair Display Italic 700** (serif de lujo, contraste con el sans).
- Tamaño 128px, Title-case, centrado `top: 48%`, pop con overshoot.
- Sombra: `0 0 18px rgba(0,0,0,0.55), 0 0 34px rgba(0,0,0,0.34), 0 3px 8px rgba(0,0,0,0.55)`.
- Hold mínimo 18 frames (0.6s) para que se lean.
- Selección: lista `EMPHASIS` en `gen_edit.py` por (palabra, t_min, t_max) en tiempo original + cualquier número 2+ dígitos. Para 0602: incorrecta, Claude, necesario, skills(CTA).

## Cortes (dead air)
- `GAP_MAX = 0.34`, `GAP_KEEP = 0.16` (solo pausas claramente muertas, con aire natural — NO sobre-recortar).

## Zoom / detalles virales (`AionEdit.tsx`)
- Zoom alternado por segmento para disfrazar jump cuts: par `base 1.04`, impar `base 1.10` (punch-in/out intencional).
- Slow push-in `base → base+0.04` por segmento.
- Cut snap: `+0.06 → 0` en 8 frames al inicio de cada corte.
- Punch sincronizado con keywords: `+0.09 → 0` en 9 frames.

## Sound design (`build_final.sh` + `sfx/`)
- **Whoosh** en cada corte (pink noise swell, brillante, vol 0.85).
- **Impacto** en cada keyword gigante: cuerpo 110Hz + click 1.2kHz (AUDIBLE en altavoces pequeños — NO sub-bass), vol 0.95.
- **Duck de voz** 0.55x ~0.25s en cada impacto para que penetre.
- Mix: `amix normalize=0` + `alimiter=0.97`.
- **Speed-up final 1.20x** (preferencia de Ricardo — reels más ágiles): `build_final.sh`
  aplica `atempo=1.20` (conserva el tono de voz) + `setpts=PTS/1.20`, re-encodea a H.264 crf18.
  Sube velocidad y encoge espacios parejo sin desincronizar B-roll/captions/gigantes.
  Override con `SPEED=1.0` (env) si un reel necesita velocidad normal.

## B-roll (capa v14+ — clonado de reels de referencia de alta viralidad)
- **FULL-SCREEN 9:16 SIEMPRE.** Mismo tamaño/encuadre que los reels de referencia — el
  B-roll TAPA todo el cuadro (cover), nunca PiP ni inset. ⚠️ Requisito explícito de Ricardo:
  "que sean del mismo tamaño que los reels que te envié" → la viralidad vive ahí.
- **La voz y los captions NO se cortan**: el B-roll va MUTEADO encima del talking-head;
  la voz de abajo sigue, y `<Captions>` se renderiza por encima del B-roll.
- **3-4 B-rolls bien localizados** (hasta 5 con hook). Duración **~3-4s** c/u. El hook puede
  cerrar justo en el primer keyword GIGANTE (reveal de la cara en el punchword).
- **Contenido: real, documental, cinematográfico y ATADO al tema** (IA/código/skills).
  NADA de hologramas, glowing UI, neón, RGB ni CGI abstracto (rechazado por Ricardo).
  Variar el ritmo: humano ↔ sistema/terminal ↔ humano ↔ tactil. No todo solemne.
- **Generación:** Higgsfield CLI (`higgs`, NO `hf`). Imagen **Nano Banana Pro** (`nano_banana_2`,
  9:16, 2k) → animar **Kling 3.0** (`kling3_0`, 9:16, 5s, mode pro, sound off). Plan en
  `broll_plan.json`; pipeline en `make_broll.sh`. Style ref de prompts: Deakins / Greig Fraser.
- **Remotion** (`AionEdit.tsx` → `BrollClip`): cover + fade 3 frames (lee como corte) + push
  sutil 1.0→1.05. Capa entre los segmentos y `<Captions>`.
- **Sound design:** whoosh en CADA transición de B-roll (entrada y salida) — corte snappy.

## NO incluir (rechazado por el usuario)
- ❌ Color grade (se ve mal — colores ORIGINALES siempre).
- ❌ Card CTA de fondo oscuro (se ve horrible).
- ❌ SFX en sub-bass (inaudibles).
- ❌ B-roll abstracto/CGI (hologramas, barras de luz, engranajes brillantes) o metáforas
  que no tengan que ver con el tema. ❌ B-roll en PiP/inset (siempre full-screen).

## Pendiente
- ⏳ Música de fondo (necesita FAL_KEY o track).

## Pipeline por reel
1. `transcribe.py` (faster-whisper large-v3) → transcript.json
2. `gen_edit.py` → src/edit.json (cortes + caption pages + giants)
3. copiar video a `public/source.mp4`
4. **B-roll** (opcional): editar `broll_plan.json` (beats + prompts atados al guion) →
   `bash make_broll.sh` (genera, anima, descarga, cablea edit.json) → ajustar `WH` en
   `build_final.sh` a las entradas/salidas de B-roll que imprime el script.
5. `npx remotion render src/index.ts AionEdit out/_base.mp4 --codec=h264 --crf=18`
6. `bash build_final.sh out/_base.mp4 out/FINAL.mp4 [music.mp3]`
