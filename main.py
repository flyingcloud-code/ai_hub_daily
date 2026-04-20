"""
AI_HUB Daily - Main Entry Point
支持两种运行模式: native / autocli
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.fetcher.reddit import fetch_reddit
from src.fetcher.x import fetch_x
from src.fetcher.hackernews import fetch_hackernews
from src.fetcher.github import fetch_github
from src.processor.core import process_items, detect_trends
from src.reporter.telegram import generate_report


def run_fetch(mode: str = "native"):
    """运行抓取"""
    print(f"🚀 Fetching data (mode: {mode})...")
    print("=" * 50)
    
    all_items = []
    
    # Reddit
    reddit_items = fetch_reddit(mode=mode)
    all_items.extend(reddit_items)
    print()
    
    # HackerNews (always native, has good public API)
    hn_items = fetch_hackernews()
    all_items.extend(hn_items)
    print()
    
    # X (mode dependent)
    x_items = fetch_x(mode=mode)
    all_items.extend(x_items)
    print()
    
    # GitHub (mode dependent)
    gh_items = fetch_github(mode=mode)
    all_items.extend(gh_items)
    print()
    
    print("=" * 50)
    print(f"📊 Total fetched: {len(all_items)} items")
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
    
    vault = Path("/Users/Shared/obsidian_share/mini-claw/AI_HUB")
    data_dir = vault / "02_Processed"
    output_dir = vault / "04_Daily_Report"
    
    print(f"\n📱 Generating report for {date}...")
    message = generate_report(data_dir, output_dir, date, yesterday)
    
    return message


def main():
    parser = argparse.ArgumentParser(description="AI_HUB Daily")
    parser.add_argument(
        "command",
        choices=["fetch", "process", "report", "all"],
        help="Command to run"
    )
    parser.add_argument(
        "--mode",
        choices=["native", "autocli"],
        default="native",
        help="Fetch mode: native (APIs) or autocli (CLI tool)"
    )
    parser.add_argument("--date", help="Date for report (YYYY-MM-DD)")
    parser.add_argument(
        "--output",
        help="Output directory",
        default="/Users/Shared/obsidian_share/mini-claw/AI_HUB"
    )
    
    args = parser.parse_args()
    
    vault = Path(args.output)
    date = datetime.now().strftime("%Y-%m-%d")
    
    if args.command == "fetch":
        items = run_fetch(mode=args.mode)
        
        # 保存
        raw_dir = vault / "01_Raw" / date
        raw_dir.mkdir(parents=True, exist_ok=True)
        with open(raw_dir / "all.json", "w") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Saved to {raw_dir / 'all.json'}")
    
    elif args.command == "process":
        raw_file = vault / "01_Raw" / date / "all.json"
        
        if not raw_file.exists():
            print(f"⚠️  No raw data found at {raw_file}")
            print("   Run: python main.py fetch [--mode native|autocli]")
            return
        
        with open(raw_file, "r") as f:
            items = json.load(f)
        
        processed = run_process(items)
        
        # 保存
        output_dir = vault / "02_Processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / f"{date}.json", "w") as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved to {output_dir / date}.json")
    
    elif args.command == "report":
        message = run_report(args.date)
        print("\n" + "=" * 50)
        print("REPORT:")
        print("=" * 50)
        print(message)
    
    elif args.command == "all":
        # 完整工作流
        items = run_fetch(mode=args.mode)
        
        # 保存 raw
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
        
        # 保存报告
        report_dir = vault / "04_Daily_Report"
        report_dir.mkdir(parents=True, exist_ok=True)
        with open(report_dir / f"{date}_telegram.txt", "w") as f:
            f.write(message)
        
        print("\n" + "=" * 50)
        print("✅ WORKFLOW COMPLETE")
        print("=" * 50)
        print(f"📁 Raw data:      {raw_dir}/all.json")
        print(f"📁 Processed:     {output_dir}/{date}.json")
        print(f"📁 Report:        {report_dir}/{date}_telegram.txt")
        print("\n" + "REPORT PREVIEW:")
        print("=" * 50)
        print(message[:1500] + "..." if len(message) > 1500 else message)


if __name__ == "__main__":
    main()
