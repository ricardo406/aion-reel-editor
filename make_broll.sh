#!/usr/bin/env bash
# AION B-roll pipeline: genera imágenes (Nano Banana Pro 9:16) -> anima (Kling 3.0 5s)
# -> descarga a public/broll/ -> cablea src/edit.json. Reusable por reel.
#
# Fuente de verdad: broll_plan.json  (beats: id, startFrame, durationInFrames,
#   phrase, image_prompt, motion_prompt). Edita ese archivo para cada video.
#
# Requiere: higgs (CLI Higgsfield, alias 'higgs'/'higgsfield' — NO 'hf'), python, ffmpeg.
# Uso:  bash make_broll.sh            # genera todo lo que falte y cablea edit.json
#       bash make_broll.sh 2 4        # solo regenera esos beats (índices)
set -e
cd "$(dirname "$0")"
PLAN=broll_plan.json
IMG=refs/broll_img
mkdir -p "$IMG" public/broll
N=$(python -c "import json;print(len(json.load(open('$PLAN',encoding='utf-8'))['beats']))")

# beats a procesar (args o todos)
if [ "$#" -gt 0 ]; then BEATS=("$@"); else BEATS=($(seq 0 $((N-1)))); fi

field(){ python -c "import json;print(json.load(open('$PLAN',encoding='utf-8'))['beats'][$1]['$2'])"; }
jget(){ python -c "import json;d=json.load(open('$1',encoding='utf-8'));print(d[0].get('$2') or '')" 2>/dev/null; }

echo "== 1/3 imágenes (Nano Banana Pro 9:16 2k) =="
for i in "${BEATS[@]}"; do
  ( P=$(field $i image_prompt)
    higgs generate create nano_banana_2 --prompt "$P" --aspect_ratio 9:16 --resolution 2k \
      --wait --wait-timeout 15m --json > "$IMG/beat${i}.json" 2>"$IMG/beat${i}.err"
    echo "  img beat$i: $(jget "$IMG/beat${i}.json" result_url | head -c 80)" ) &
done; wait

echo "== 2/3 animación (Kling 3.0 5s 9:16 pro, sound off) =="
for i in "${BEATS[@]}"; do
  ( ID=$(jget "$IMG/beat${i}.json" id)
    M=$(field $i motion_prompt)
    higgs generate create kling3_0 --start-image "$ID" --prompt "$M" --aspect_ratio 9:16 \
      --duration 5 --mode pro --sound off --wait --wait-timeout 20m --json \
      > "$IMG/vid${i}.json" 2>"$IMG/vid${i}.err"
    BID=$(field $i id)
    curl -sL -o "public/broll/${BID}.mp4" "$(jget "$IMG/vid${i}.json" result_url)"
    echo "  vid beat$i -> public/broll/${BID}.mp4 ($(ls -la public/broll/${BID}.mp4 | awk '{print $5}')b)" ) &
done; wait

echo "== 3/3 cableando src/edit.json =="
python -c "
import json
edit=json.load(open('src/edit.json',encoding='utf-8'))
plan=json.load(open('$PLAN',encoding='utf-8'))
edit['broll']=[{'startFrame':b['startFrame'],'durationInFrames':b['durationInFrames'],
                'src':'broll/'+b['id']+'.mp4'} for b in plan['beats']]
json.dump(edit,open('src/edit.json','w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('  broll wired:',len(edit['broll']),'clips')
print('  whoosh times (edita WH en build_final.sh):',
      ' '.join(f\"{b['startFrame']/plan['fps']:.1f}/{(b['startFrame']+b['durationInFrames'])/plan['fps']:.1f}\" for b in plan['beats']))
"
echo "DONE. Ahora: npx remotion render src/index.ts AionEdit out/_base.mp4 --codec=h264 --crf=18  &&  bash build_final.sh out/_base.mp4 out/FINAL.mp4"
