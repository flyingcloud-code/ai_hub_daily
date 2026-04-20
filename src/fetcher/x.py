"""
AI_HUB Daily - X/Twitter Fetcher
支持两种模式:
1. Native: X API v2 (需要 Bearer Token)
2. Autocli: 通过 autocli 命令
"""

import json
import os
import subprocess
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional

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
    except FileNotFoundError:
        return False, "", "autocli not found"


def has_autocli() -> bool:
    """检查 autocli 是否安装"""
    success, _, _ = run_autocli("autocli --version")
    return success


def get_bearer_token() -> Optional[str]:
    """从环境变量获取 X Bearer Token"""
    return os.environ.get("X_BEARER_TOKEN") or os.environ.get("TWITTER_BEARER_TOKEN")


def fetch_x_native(
    queries: List[str] = None,
    limit: int = 25
) -> List[Dict]:
    """使用 X API v2"""
    token = get_bearer_token()
    if not token:
        print("⚠️  X_BEARER_TOKEN not set, skipping native fetch")
        print("   Get one at: https://developer.twitter.com/en/portal/dashboard")
        return []
    
    if queries is None:
        queries = ["AI", "ChatGPT", "Claude"]
    
    query = " OR ".join([f'"{q}"' for q in queries])
    query += " -is:retweet"
    
    url = "https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "query": query,
        "max_results": min(limit, 100),
        "tweet.fields": "created_at,public_metrics,author_id",
        "expansions": "author_id",
        "user.fields": "username"
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        users = {}
        for user in data.get("includes", {}).get("users", []):
            users[user["id"]] = user["username"]
        
        items = []
        threshold = config.get_threshold("x")
        min_likes = threshold.get("likes", 20)
        min_retweets = threshold.get("retweets", 5)
        cutoff = datetime.now() - timedelta(hours=24)
        
        for tweet in data.get("data", []):
            metrics = tweet.get("public_metrics", {})
            likes = metrics.get("like_count", 0)
            retweets = metrics.get("retweet_count", 0)
            
            if likes < min_likes and retweets < min_retweets:
                continue
            
            created = tweet.get("created_at", "")
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                if dt < cutoff:
                    continue
            except:
                pass
            
            author = users.get(tweet["author_id"], "unknown")
            
            items.append({
                "platform": "X",
                "title": tweet.get("text", "")[:200],
                "text": tweet.get("text", ""),
                "url": f"https://x.com/{author}/status/{tweet['id']}",
                "author": author,
                "published_at": created,
                "engagement": {
                    "likes": likes,
                    "retweets": retweets,
                    "replies": metrics.get("reply_count", 0)
                }
            })
        
        return items
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("⚠️  X API 401: Invalid Bearer Token")
        elif e.response.status_code == 429:
            print("⚠️  X API 429: Rate limit exceeded")
        else:
            print(f"⚠️  X API error: {e}")
        return []
    except Exception as e:
        print(f"⚠️  X native fetch failed: {e}")
        return []


def fetch_x_autocli(
    topics: List[str] = None,
    limit: int = 20
) -> List[Dict]:
    """使用 autocli"""
    if not has_autocli():
        return []
    
    if topics is None:
        topics = ["AI", "ArtificialIntelligence", "MachineLearning", "LLM", "ChatGPT", "Claude"]
    
    # 检查登录
    success, stdout, _ = run_autocli("autocli social x status")
    if not success or "active" not in stdout.lower():
        print("⚠️  X not logged in via autocli. Run: autocli social x login --browser")
        return []
    
    all_items = []
    threshold = config.get_threshold("x")
    cutoff = datetime.now() - timedelta(hours=24)
    
    for topic in topics:
        cmd = f'autocli social x search "#{topic} OR ${topic}" --limit {limit} --json 2>/dev/null'
        success, stdout, stderr = run_autocli(cmd, timeout=30)
        
        if not success or not stdout:
            continue
        
        try:
            items = json.loads(stdout)
            if not isinstance(items, list):
                continue
            
            for item in items:
                created = item.get("created_at") or item.get("publishedAt")
                if created:
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        if dt < cutoff:
                            continue
                    except:
                        pass
                
                metrics = item.get("public_metrics", {})
                likes = metrics.get("like_count", 0) or item.get("likes", 0)
                retweets = metrics.get("retweet_count", 0) or item.get("retweets", 0)
                
                if likes < threshold.get("likes", 20) and retweets < threshold.get("retweets", 5):
                    continue
                
                all_items.append({
                    "platform": "X",
                    "title": item.get("text", "")[:200],
                    "text": item.get("text", ""),
                    "url": f"https://x.com/i/web/status/{item.get('id')}" if item.get('id') else item.get("url"),
                    "author": item.get("author", {}).get("username", "unknown"),
                    "published_at": created,
                    "engagement": {"likes": likes, "retweets": retweets}
                })
        except Exception as e:
            print(f"  ✗ topic '{topic}': {e}")
    
    return all_items


def fetch_x(
    mode: str = "native",
    queries: List[str] = None,
    limit: int = 25
) -> List[Dict]:
    """
    抓取 X 内容
    
    Args:
        mode: "native" (需 Bearer Token) 或 "autocli" (需登录)
        queries: 搜索关键词
        limit: 数量限制
    """
    print(f"📱 Fetching X/Twitter (mode: {mode})...")
    
    if mode == "autocli":
        if not has_autocli():
            print("⚠️  autocli not found, falling back to native mode")
            mode = "native"
        else:
            items = fetch_x_autocli(queries, limit)
            print(f"✅ X: {len(items)} items")
            return items
    
    # native mode
    items = fetch_x_native(queries, limit)
    print(f"✅ X: {len(items)} items")
    return items


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "native"
    items = fetch_x(mode=mode)
    print(f"\nTotal: {len(items)} items")
