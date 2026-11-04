#!/bin/sh
# One line of context at session start, only when it's useful:
# no team yet, or the last retro is older than RETRO_DAYS (default 14).
team=".claude/team.md"
[ -d .git ] || git rev-parse --git-dir >/dev/null 2>&1 || exit 0
if [ ! -f "$team" ]; then
  echo "badetitou-team: no .claude/team.md in this project. Offer the team-setup skill if the user starts real work here."
  exit 0
fi
last=$(sed -n 's/^Last retro: *\([0-9-]\{10\}\).*/\1/p' "$team" | head -1)
[ -n "$last" ] || { echo "badetitou-team: no retro recorded yet; offer the team-retro skill at a natural pause."; exit 0; }
days=${RETRO_DAYS:-14}
then=$(date -j -f %Y-%m-%d "$last" +%s 2>/dev/null || date -d "$last" +%s 2>/dev/null) || exit 0
age=$(( ($(date +%s) - then) / 86400 ))
[ "$age" -ge "$days" ] && echo "badetitou-team: last retro was $age days ago ($last); offer the team-retro skill at a natural pause."
exit 0
