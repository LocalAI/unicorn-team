#!/usr/bin/env bash
# platform-context.sh — SessionStart hook that injects active platform-docs
# project context into every conversation.
#
# Output: JSON with additionalContext field for Claude Code SessionStart hook.
# Exits silently (exit 0) if no registry or active project is configured.

REGISTRY="$HOME/.claude/platform-docs-registry.json"

if [ ! -f "$REGISTRY" ]; then
    exit 0
fi

# Read active project path and name from registry (stdlib json only)
read -r ACTIVE DOCS_PATH PROJECT_NAME <<< "$(python3 -c "
import json, sys
try:
    r = json.load(open('$REGISTRY'))
    a = r.get('active', '')
    p = r.get('projects', {}).get(a, {})
    print(a, p.get('path', ''), p.get('name', a))
except Exception:
    print('', '', '')
" 2>/dev/null)"

if [ -z "$DOCS_PATH" ] || [ ! -d "$DOCS_PATH" ]; then
    exit 0
fi

# Verify manifest exists
if [ ! -f "$DOCS_PATH/platform-docs.yaml" ]; then
    exit 0
fi

# Find latest platform rollup report
REPORTS_DIR="$DOCS_PATH/current-state/platform"
LATEST_REPORT=""
if [ -d "$REPORTS_DIR" ]; then
    LATEST_REPORT=$(ls -t "$REPORTS_DIR"/*.md 2>/dev/null | head -1)
fi
REPORT_DATE=""
if [ -n "$LATEST_REPORT" ]; then
    REPORT_DATE=$(basename "$LATEST_REPORT" | grep -o '[0-9]\{8\}-[0-9]\{4\}' | head -1)
fi

# Count open debt items
BACKLOG_DIR="$DOCS_PATH/backlog"
DEBT_COUNT=0
if [ -d "$BACKLOG_DIR" ]; then
    DEBT_COUNT=$(find "$BACKLOG_DIR" -name "DEBT-*.md" -not -name "TEMPLATE*" -not -name "README*" 2>/dev/null | wc -l | tr -d ' ')
fi

# Build and output JSON using Python for correct escaping
CTX="Active platform-docs project: $PROJECT_NAME ($ACTIVE). Docs: $DOCS_PATH."
if [ -n "$REPORT_DATE" ]; then
    CTX="$CTX Latest rollup: $REPORT_DATE."
fi
if [ "$DEBT_COUNT" -gt 0 ]; then
    CTX="$CTX Open debt: $DEBT_COUNT items."
fi

CTX_JSON=$(CTX="$CTX" python3 -c "
import json, os
print(json.dumps({
    'continue': True,
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': os.environ['CTX']
    }
}, indent=2))
" 2>/dev/null) || exit 0
echo "$CTX_JSON"
