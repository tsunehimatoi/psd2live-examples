#!/bin/bash
# usage: run_edits.sh tag space
cd /workspace/art; T=$1; S=$2; mkdir -p edit_try/$T
i=0
while IFS='|' read -r name prompt; do
  /workspace/tools/venv-hf/bin/python /workspace/tools/hf_edit.py head_H0.jpg edit_try/$T/$name.png "$prompt" --space $S --retries 1 2>&1 | tail -2
done <<'LIST'
bangs|remove the bangs/front hair and side locks, complete the forehead and face behind them, keep everything else identical
noeyes|remove the eyes, leaving blank smooth skin where the eyes were, keep everything else identical
bald|remove all hair, bald head with ears, keep everything else identical
green|change background to flat green #00FF00, keep everything else identical
LIST
