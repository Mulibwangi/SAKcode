#!/usr/bin/env bash
# Run the full cubic-box pipeline for a coefficient bound (see PREREG_box50.md).
#   bash run_box.sh 50 [workers] [rank_workers]
# Outputs go to ./box<BOUND>/ next to this script; the box-30 results in this folder are the reference.
set -euo pipefail
BOUND="${1:?coefficient bound, e.g. 50}"
W="${2:-32}"
RW="${3:-8}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$HERE/box$BOUND"
ECL="$HERE/.venv-eclib/bin/python"
mkdir -p "$OUT"
for f in cubic_faces.py descent_check.py lfun_check.py rank_check.py box_analytic.py sha_check.py dual_sha_check.py box_report.py; do
  cp "$HERE/$f" "$OUT/"
done
cd "$OUT"
step() { echo "=== $1  $(date +%T)"; }
step "1 local test + point search";   python3 cubic_faces.py --box "$BOUND"            > faces.log    2>&1; tail -2 faces.log
step "2 mwrank descent";              "$ECL" descent_check.py --workers "$W"            > descent.log  2>&1; tail -3 descent.log
step "3 analytic closure";            python3 box_analytic.py --workers "$RW"           > analytic.log 2>&1; tail -3 analytic.log
step "4a Sha[psi]";                   python3 sha_check.py --workers "$W" --record /nonexistent > sha.log 2>&1; tail -2 sha.log
step "4b dual Sha";                   python3 dual_sha_check.py --workers "$W"          > dual.log     2>&1; tail -2 dual.log
step "5 analytic rank <= 1";          python3 rank_check.py --workers "$RW"             > rank.log     2>&1; tail -2 rank.log
step "6 report";                      python3 box_report.py --ref "$HERE"               > report.log   2>&1
cat report.log
step "done"
