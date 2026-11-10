#!/usr/bin/env bash
# Local/static checks; no network, no installs, no execution of untrusted datasets.
set -euo pipefail
cd "$(dirname "$0")/.."
test -f skills/signalforge/SKILL.md
test -f SECURITY.md
test -f .claude-plugin/plugin.json
test -f .claude-plugin/marketplace.json
test -f LICENSE
test -f evals/triggers.json
grep -q '^name: signalforge$' skills/signalforge/SKILL.md
grep -q '^description:' skills/signalforge/SKILL.md
jq -e '.name=="signalforge" and .version=="0.2.0"' .claude-plugin/plugin.json >/dev/null
jq -e '.plugins | any(.name=="signalforge")' .claude-plugin/marketplace.json >/dev/null
jq -e '.skill=="signalforge" and ([.queries[] | select(.trigger==true)]|length)>=5 and ([.queries[] | select(.trigger==false)]|length)>=3' evals/triggers.json >/dev/null
python -m compileall -q signalforge
python -m unittest discover -s tests -q
echo "PASS: SignalForge static checks and offline unit tests"
