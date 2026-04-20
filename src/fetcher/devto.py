"""
AI_HUB Daily - Dev.to Fetcher
使用 Dev.to 公开 API 抓取 AI/ML 热门文章
"""

import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict

from ..utils.config import config

DEVTO_API = "https://dev.to/api/articles"

# Dev.to 的 AI 相关 tag
TAGS = ["machinelearning", "artificialintelligence", "deeplearning", "llm", "chatgpt"]


def fetch_devto(tags: List[str] = None, per_page: int = 10, top_days: int = 7) -> List[Dict]:
    """
    抓取 Dev.to 热门 AI 文章
    
    Args:
        tags: Dev.to tag 列表
        per_page: 每个 tag 抓取数量
        top_days: 热门时间窗口（天）
    
    Returns:
        过滤后的内容列表
    """
    if tags is None:
        tags = TAGS
    
    print("📱 Fetching Dev.to...")
    
    all_items = []
    seen_ids = set()
    
    for tag in tags:
        try:
            params = {
                "tag": tag,
                "per_page": per_page,
                "top": top_days,
            }
            resp = requests.get(DEVTO_API, params=params, timeout=15)
            if resp.status_code != 200:
                continue
            
            articles = resp.json()
            if not isinstance(articles, list):
                continue
            
            count = 0
            for a in articles:
                aid = str(a.get("id", ""))
                if aid in seen_ids:
                    continue
                seen_ids.add(aid)
                
                reactions = a.get("positive_reactions_count", 0)
                comments = a.get("comments_count", 0)
                
                # 质量过滤：至少 5 reactions
                if reactions < 5 and comments < 3:
                    continue
                
                all_items.append({
                    "platform": "Dev.to",
                    "title": a.get("title", ""),
                    "text": (a.get("description") or "")[:500],
                    "url": a.get("url", ""),
                    "author": a.get("user", {}).get("username", "unknown"),
                    "published_at": a.get("published_at", ""),
                    "engagement": {
                        "likes": reactions,
                        "comments": comments,
                        "views": a.get("page_views_count", 0),
                    },
                    "tags": a.get("tag_list", []),
                    "raw": a,
                })
                count += 1
            
            print(f"  ✓ #{tag}: {count} items")
        
        except Exception as e:
            print(f"  ✗ #{tag}: {e}")
    
    print(f"✅ Dev.to: {len(all_items)} items after filtering")
    return all_items


if __name__ == "__main__":
    items = fetch_devto()
    print(f"\nTotal: {len(items)} items")
    for item in items[:5]:
        r = item["engagement"]["likes"]
        print(f"  [{r}❤️] {item['title'][:60]}")
