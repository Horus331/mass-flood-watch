#!/bin/bash
# post.sh "update text" [--stage N --status "..." --note "..."]  -> updates docs/progress.json, commits, pushes
cd "$(dirname "$0")/.." && python3 tools/progress.py "$@" && git add docs/progress.json && git commit -qm "Work log: $(echo "$1" | cut -c1-70)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01SiES76oibK6J65JoLEiesB" && for i in 1 2 3 4 5 6; do git pull -q --rebase && git push -q && echo pushed && break; sleep 6; done
