#!/bin/sh
# Shallow-clone or update every repo in catalog/references.json into vendor/<name>,
# so skills can read upstream docs locally instead of fetching them each time.
set -e
cd "$(dirname "$0")/.."
python3 -c 'import json;[print(r["name"],r["repo"],r.get("ref","main")) for r in json.load(open("catalog/references.json"))["references"]]' |
while read -r name repo ref; do
  dir="vendor/$name"
  if [ -d "$dir/.git" ]; then
    git -C "$dir" fetch -q --depth 1 origin "$ref" && git -C "$dir" reset -q --hard FETCH_HEAD
  else
    git clone -q --depth 1 --branch "$ref" "$repo" "$dir"
  fi
  echo "$name $(git -C "$dir" rev-parse --short HEAD)"
done
