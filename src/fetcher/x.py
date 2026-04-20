"""
AI_HUB Daily - X/Twitter Fetcher
"""

import json
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict

from ..utils.config import config


def run_autocli(cmd: str, timeout: int = 60) -> tuple:
    """运行 autocli 命令"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"


def check_login() -> bool:
    """检查 X 登录状态"""
    success, stdout, _ = run_autocli("autocli social x status")
    return success and "active" in stdout.lower()


def fetch_x(topics: List[str] = None, limit: int = 20) -> List[Dict]:
    """
    抓取 X/Twitter 内容
    
    需要提前登录: autocli social x login --browser
    """
    if topics is None:
        topics = ["AI", "ArtificialIntelligence", "MachineLearning", "LLM", "ChatGPT", "Claude"]
    
    print("📱 Fetching X/Twitter...")
    
    # 检查登录
    if not check_login():
        print("⚠️  X not logged in. Run: autocli social x login --browser")
        return []
    
    all_items = []
    threshold = config.get_threshold("x")
    
    for topic in topics:
        # 搜索 hashtag 和 cashtag
        cmd = f'autocli social x search "#{topic} OR ${topic}" --limit {limit} --json 2>/dev/null'
        success, stdout, stderr = run_autocli(cmd, timeout=30)
        
        if not success or not stdout:
            continue
        
        try:
            items = json.loads(stdout)
            if isinstance(items, list):
                all_items.extend(items)
                print(f"  ✓ '{topic}': {len(items)} items")
        except Exception as e:
            print(f"  ✗ '{topic}': parse error - {e}")
    
    # 过滤
    seen = set()
    filtered = []
    
    for item in all_items:
        item_id = item.get("id")
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)
        
        # 时间过滤
        created = item.get("created_at") or item.get("publishedAt")
        if created:
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if datetime.now(dt.tzinfo) - dt > timedelta(hours=24):
                    continue
            except:
                pass
        
        # Engagement
        metrics = item.get("public_metrics", {})
        likes = metrics.get("like_count", 0) or item.get("likes", 0)
        retweets = metrics.get("retweet_count", 0) or item.get("retweets", 0)
        
        # 质量过滤
        if likes >= threshold.get("likes", 20) or retweets >= threshold.get("retweets", 5):
            filtered.append({
                "platform": "X",
                "title": item.get("text", "")[:200],
                "text": item.get("text", ""),
                "url": f"https://x.com/i/web/status/{item.get('id')}" if item.get('id') else item.get("url"),
                "author": item.get("author", {}).get("username", "unknown"),
                "published_at": created,
                "engagement": {"likes": likes, "retweets": retweets},
                "raw": item
            })
    
    print(f"✅ X: {len(filtered)} items after filtering")
    return filtered


if __name__ == "__main__":
    items = fetch_x()
    print(f"\nTotal: {len(items)} items")
