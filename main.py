"""
AI_HUB Daily - Main Entry Point
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.fetcher.reddit import fetch_reddit
from src.fetcher.x import fetch_x
from src.processor.core import process_items, detect_trends
from src.reporter.telegram import generate_report


def run_fetch():
    """运行抓取"""
    print("🚀 Fetching data...")
    
    all_items = []
    
    # Reddit
    reddit_items = fetch_reddit()
    all_items.extend(reddit_items)
    
    # X (需要登录)
    x_items = fetch_x()
    all_items.extend(x_items)
    
    print(f"\n📊 Total fetched: {len(all_items)} items")
    return all_items


def run_process(items):
    """运行处理"""
    print("\n⚙️  Processing...")
    processed = process_items(items)
    print(f"✅ Processed: {len(processed)} items")
    return processed


def run_report(date: str = None):
    """运行报告生成"""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 默认路径
    vault = Path("/Users/Shared/obsidian_share/mini-claw/AI_HUB")
    data_dir = vault / "02_Processed"
    output_dir = vault / "04_Daily_Report"
    
    print(f"\n📱 Generating report for {date}...")
    message = generate_report(data_dir, output_dir, date, yesterday)
    
    return message


def main():
    parser = argparse.ArgumentParser(description="AI_HUB Daily")
    parser.add_argument("command", choices=["fetch", "process", "report", "all"], 
                       help="Command to run")
    parser.add_argument("--date", help="Date for report (YYYY-MM-DD)")
    
    args = parser.parse_args()
    
    if args.command == "fetch":
        items = run_fetch()
        # 保存
        import json
        date = datetime.now().strftime("%Y-%m-%d")
        vault = Path("/Users/Shared/obsidian_share/mini-claw/AI_HUB")
        raw_dir = vault / "01_Raw" / date
        raw_dir.mkdir(parents=True, exist_ok=True)
        with open(raw_dir / "all.json", "w") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
    
    elif args.command == "process":
        import json
        date = datetime.now().strftime("%Y-%m-%d")
        vault = Path("/Users/Shared/obsidian_share/mini-claw/AI_HUB")
        raw_file = vault / "01_Raw" / date / "all.json"
        
        with open(raw_file, "r") as f:
            items = json.load(f)
        
        processed = run_process(items)
        
        # 保存
        output_dir = vault / "02_Processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / f"{date}.json", "w") as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)
    
    elif args.command == "report":
        message = run_report(args.date)
        print("\n" + "=" * 50)
        print(message)
    
    elif args.command == "all":
        # 完整工作流
        items = run_fetch()
        
        # 保存 raw
        import json
        date = datetime.now().strftime("%Y-%m-%d")
        vault = Path("/Users/Shared/obsidian_share/mini-claw/AI_HUB")
        raw_dir = vault / "01_Raw" / date
        raw_dir.mkdir(parents=True, exist_ok=True)
        with open(raw_dir / "all.json", "w") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        
        # 处理
        processed = run_process(items)
        
        # 保存 processed
        output_dir = vault / "02_Processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / f"{date}.json", "w") as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)
        
        # 生成报告
        message = run_report(date)
        print("\n" + "=" * 50)
        print("REPORT PREVIEW:")
        print("=" * 50)
        print(message[:1000] + "..." if len(message) > 1000 else message)


if __name__ == "__main__":
    main()
