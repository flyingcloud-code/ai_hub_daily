"""
AI_HUB Daily - HackerNews Fetcher
使用官方 API: https://github.com/HackerNews/API
"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict

from ..utils.config import config


BASE_URL = "https://hacker-news.firebaseio.com/v0"


def fetch_item(item_id: int) -> Dict:
    """抓取单个条目"""
    url = f"{BASE_URL}/item/{item_id}.json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json() or {}
    except:
        return {}


def fetch_top_stories(limit: int = 30) -> List[Dict]:
    """抓取 Top Stories"""
    url = f"{BASE_URL}/topstories.json"
    
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        story_ids = resp.json()[:limit]
        
        items = []
        for sid in story_ids:
            item = fetch_item(sid)
            if item and item.get("type") == "story":
                # 转换为统一格式
                items.append({
                    "platform": "HackerNews",
                    "title": item.get("title", ""),
                    "text": item.get("text", "")[:2000],
                    "url": item.get("url") or f"https://news.ycombinator.com/item?id={sid}",
                    "author": item.get("by", "unknown"),
                    "published_at": datetime.fromtimestamp(
                        item.get("time", 0)
                    ).isoformat(),
                    "engagement": {
                        "points": item.get("score", 0),
                        "comments": item.get("descendants", 0)
                    },
                    "hn_id": sid
                })
            time.sleep(0.05)  # 礼貌间隔
        
        return items
    except Exception as e:
        print(f"  ✗ HN top stories failed: {e}")
        return []


def fetch_hackernews(
    limit: int = 30,
    min_points: int = None,
    min_comments: int = None
) -> List[Dict]:
    """
    抓取 HackerNews 内容
    
    Args:
        limit: 抓取数量
        min_points: 最小分数
        min_comments: 最小评论数
    
    Returns:
        过滤后的内容列表
    """
    threshold = config.get_threshold("hackernews")
    min_points = min_points or threshold.get("points", 20)
    min_comments = min_comments or threshold.get("comments", 5)
    
    print("📱 Fetching HackerNews...")
    
    items = fetch_top_stories(limit)
    
    # 过滤：24h + 质量
    cutoff = datetime.now() - timedelta(hours=24)
    filtered = []
    
    for item in items:
        # 时间过滤
        try:
            pub_time = datetime.fromisoformat(item["published_at"])
            if pub_time < cutoff:
                continue
        except:
            pass
        
        # 质量过滤
        eng = item["engagement"]
        if eng["points"] >= min_points or eng["comments"] >= min_comments:
            filtered.append(item)
    
    print(f"✅ HN: {len(filtered)} items after filtering (from {len(items)} raw)")
    return filtered


if __name__ == "__main__":
    items = fetch_hackernews()
    print(f"\nTotal: {len(items)} items")
    for item in items[:3]:
        print(f"- {item['title'][:60]}... (points: {item['engagement']['points']})")
