#!/usr/bin/env bash
# Final pass: sound design (NO color grade, NO card) + speed-up global.
# whoosh on cuts, impact on giant keywords. Optional music bed.
# Reels AION salen a 1.20x (preferencia de Ricardo: mas agiles). Override: SPEED=1.0
# Usage: bash build_final.sh <base.mp4> <out.mp4> [music.mp3]   (env: SPEED=1.20)
set -e
cd "$(dirname "$0")"
BASE="${1:-out/_v9_base.mp4}"
OUT="${2:-out/aion_0602_v9.mp4}"
MUSIC="${3:-}"
SPEED="${SPEED:-1.20}"   # velocidad final (atempo conserva el tono de voz). 1.0 = sin acelerar

# sound design timings (seconds): whoosh on each B-roll transition (in/out) +
# standalone face jump-cut; impact on each giant keyword.
# whoosh: cada corte visible + cada entrada/salida de B-roll (se omitio el corte
# 18.43 porque cae bajo el B-roll del peon y no se ve).
WH=(4.2 7.53 16.87 17.77 20.77 21.13 24.17 29.17 30.17 36.8 40.8 52.73 58.53 62.87 63.3 74.67)
# impacto desactivado a pedido: solo whoosh, sin golpes de impacto ni duck de voz.
IM=()

INPUTS=(-i "$BASE")
FILTER=""
ALABELS=""
idx=1
for t in "${WH[@]}"; do
  INPUTS+=(-i sfx/whoosh.wav)
  ms=$(awk "BEGIN{printf \"%d\", $t*1000}")
  FILTER+="[${idx}:a]adelay=${ms}:all=1,volume=0.85[w${idx}];"
  ALABELS+="[w${idx}]"
  idx=$((idx+1))
done
for t in "${IM[@]}"; do
  INPUTS+=(-i sfx/impact.wav)
  ms=$(awk "BEGIN{printf \"%d\", $t*1000}")
  FILTER+="[${idx}:a]adelay=${ms}:all=1,volume=0.95[i${idx}];"
  ALABELS+="[i${idx}]"
  idx=$((idx+1))
done

NA=$(( 1 + ${#WH[@]} + ${#IM[@]} ))
if [ -n "$MUSIC" ]; then
  INPUTS+=(-stream_loop -1 -i "$MUSIC")
  FILTER+="[${idx}:a]volume=0.14,afade=t=in:st=0:d=1.5[mus];"
  ALABELS+="[mus]"
  NA=$(( NA + 1 ))
fi

# duck the voice briefly around each impact so the hit punches through
DUCK="1"
for t in "${IM[@]}"; do
  a=$(awk "BEGIN{printf \"%.3f\", $t-0.03}")
  b=$(awk "BEGIN{printf \"%.3f\", $t+0.27}")
  DUCK+=" - 0.55*between(t,${a},${b})"
done
FILTER+="[0:a]volume=eval=frame:volume='${DUCK}'[voice];[voice]${ALABELS}amix=inputs=${NA}:normalize=0:dropout_transition=0,alimiter=limit=0.97[mix];[mix]atempo=${SPEED}[aout];[0:v]setpts=PTS/${SPEED}[vout]"

ffmpeg -y -loglevel error "${INPUTS[@]}" \
  -filter_complex "$FILTER" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 256k -shortest "$OUT"

echo "DONE -> $OUT  (speed ${SPEED}x)"
