#!/bin/bash
# Publish a whole-district replay pack: Turing's pack_site.slurm pushes it to the branch district-data (its deploy key reaches only this
# repository); this copies it to the data site Horus331/mfw-data-d3 (GitHub Pages, one push) and leaves the small stub on the main site.
#   bash tools/publish_district.sh <folder on district-data> <site key> ["<title>"]
#   e.g. bash tools/publish_district.sh d3_sep2023_t d3_sep2023 "District 3 · Sept 11, 2023"
# Then commit docs/site/data/<site key>/ on main yourself (batched with the viewer change that goes with it).
set -eo pipefail
cd "$(dirname "$0")/.."
SRC=$1; KEY=${2:-$1}; TITLE=${3:-$KEY}; BASE=https://horus331.github.io/mfw-data-d3/$KEY/
git fetch -q origin district-data
T=$(mktemp -d); git archive FETCH_HEAD "$SRC" | tar -x -C "$T"
D=$(mktemp -d); git clone -q --depth 1 https://github.com/Horus331/mfw-data-d3 "$D"
python3 tools/district_stub.py "$T/$SRC" "$D/$KEY" "docs/site/data/$KEY" "$BASE" "$KEY" --index "$D/index.json" --title "$TITLE"
python3 proto/build_network.py "$KEY" || true; cp "docs/site/data/$KEY/network.json" "$D/$KEY/" 2>/dev/null || true
( cd "$D" && git add -A && git -c user.name="Mohab Eldokla" -c user.email="Horus331@users.noreply.github.com" commit -qm "$KEY: whole-district replay (from mass-flood-watch district-data/$SRC)" && git push -q origin HEAD:main )
echo "data: $BASE   stub: docs/site/data/$KEY (commit it on main)"
