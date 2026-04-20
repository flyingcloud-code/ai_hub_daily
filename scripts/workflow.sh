#!/bin/bash
# AI_HUB Daily Workflow
# 完整工作流：抓取 → 处理 → 生成报告

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VAULT_BASE="${AI_HUB_VAULT:-/Users/Shared/obsidian_share/mini-claw/AI_HUB}"
DATE=$(date +%Y-%m-%d)

echo "🚀 AI_HUB Daily Workflow - $DATE"
echo "================================"
echo ""

# 检查依赖
if ! command -v autocli &> /dev/null; then
    echo "⚠️  Warning: autocli not found in PATH"
fi

# 创建目录
mkdir -p "$VAULT_BASE"/01_Raw/"$DATE"
mkdir -p "$VAULT_BASE"/02_Processed
mkdir -p "$VAULT_BASE"/04_Daily_Report

# Step 1: 抓取内容
echo "📥 Step 1: Fetching content..."
cd "$PROJECT_ROOT"

# Reddit
python3 -m src.fetcher.reddit > "$VAULT_BASE/01_Raw/$DATE/reddit.json" 2>&1 || echo "⚠️  Reddit fetch failed"

# X/Twitter (需要登录)
python3 -m src.fetcher.x > "$VAULT_BASE/01_Raw/$DATE/x.json" 2>&1 || echo "⚠️  X fetch failed (may need login)"

# 合并所有数据
python3 << EOF
import json
import glob
from pathlib import Path

vault = Path("$VAULT_BASE")
raw_dir = vault / "01_Raw" / "$DATE"

all_items = []
for json_file in raw_dir.glob("*.json"):
    if json_file.name == "summary.json":
        continue
    try:
        with open(json_file, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                all_items.extend(data)
                print(f"✓ Loaded {len(data)} from {json_file.stem}")
    except Exception as e:
        print(f"✗ Failed to load {json_file}: {e}")

# 保存汇总
with open(raw_dir / "all.json", "w") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)

print(f"✅ Total: {len(all_items)} items")
EOF

echo ""

# Step 2: 处理内容
echo "⚙️  Step 2: Processing content..."
python3 << EOF
import json
import sys
sys.path.insert(0, "$PROJECT_ROOT")

from src.processor.core import process_items, detect_trends
from pathlib import Path

vault = Path("$VAULT_BASE")
raw_file = vault / "01_Raw" / "$DATE" / "all.json"
output_dir = vault / "02_Processed"

if not raw_file.exists():
    print("⚠️  No raw data found")
    exit(0)

with open(raw_file, "r") as f:
    items = json.load(f)

print(f"📊 Processing {len(items)} items...")

# 处理
processed = process_items(items)

# 保存
output_dir.mkdir(parents=True, exist_ok=True)
with open(output_dir / "$DATE.json", "w") as f:
    json.dump(processed, f, ensure_ascii=False, indent=2)

print(f"✅ Saved {len(processed)} processed items")
EOF

echo ""

# Step 3: 生成 Telegram 报告
echo "📱 Step 3: Generating Telegram report..."
python3 << EOF
import sys
sys.path.insert(0, "$PROJECT_ROOT")

from src.reporter.telegram import generate_report
from pathlib import Path
from datetime import datetime, timedelta

vault = Path("$VAULT_BASE")
data_dir = vault / "02_Processed"
output_dir = vault / "04_Daily_Report"

date = "$DATE"
yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

message = generate_report(data_dir, output_dir, date, yesterday)
print(f"✅ Report generated")
EOF

echo ""

# 完成
echo "================================"
echo "✅ AI_HUB Workflow Complete!"
echo ""
echo "📊 Summary:"
echo "  • Raw data: 01_Raw/$DATE/"
echo "  • Processed: 02_Processed/$DATE.json"
echo "  • Report: 04_Daily_Report/${DATE}_telegram.txt"
echo ""
echo "📤 To send to Telegram:"
echo "  cat 04_Daily_Report/${DATE}_telegram.txt | your-bot-command"
