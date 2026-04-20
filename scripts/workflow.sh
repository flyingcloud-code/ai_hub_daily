#!/bin/bash
# AI_HUB Daily Workflow
# 支持两种模式: native / autocli

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 默认配置
MODE="${AI_HUB_MODE:-native}"
VAULT_BASE="${AI_HUB_VAULT:-/Users/Shared/obsidian_share/mini-claw/AI_HUB}"
DATE=$(date +%Y-%m-%d)

echo "🚀 AI_HUB Daily Workflow - $DATE"
echo "Mode: $MODE"
echo "================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    exit 1
fi

# 运行
python3 "$PROJECT_ROOT/main.py" all --mode "$MODE" --output "$VAULT_BASE"

echo ""
echo "================================"
echo "✅ Workflow Complete!"
