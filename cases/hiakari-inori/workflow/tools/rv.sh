#!/bin/bash
# usage: rv.sh out_prefix 'params-json' [left top w h]
P=${2:-{\}}; L=${3:-0}; T=${4:-0}; W=${5:-2048}; H=${6:-3072}; E=${7:-1600}
python3 /workspace/tools/mview.py view "{\"op\":\"render_model\",\"request\":{\"target_long_edge\":$E,\"parameters\":$P,\"background\":\"transparent\",\"viewport\":{\"mode\":\"canvas_rect\",\"left\":$L,\"top\":$T,\"width\":$W,\"height\":$H}}}" $1 | tail -2
