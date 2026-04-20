"""
AI_HUB Daily - Reddit Fetcher
支持两种模式:
1. Native: Reddit JSON API (无需认证)
2. Autocli: 通过 autocli 命令 (需安装)
"""

import json
import requests
import subprocess
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from urllib.parse import urljoin

from ..utils.config import config


BASE_URL = "https://www.reddit.com"
HEADERS = {
    "User-Agent": "AI_HUB_Daily/2.0 (Research Project)"
}


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


def parse_reddit_metrics(metrics: List[str]) -> tuple:
    """解析 Reddit metrics 字符串"""
    score = 0
    comments = 0
    subreddit = ""
    
    for m in metrics:
        m_lower = m.lower()
        if "score" in m_lower:
            try:
                score_str = m_lower.replace("score", "").replace("k", "000").strip()
                score = int(float(score_str))
            except:
                pass
        elif "comments" in m_lower:
            try:
                comments_str = m_lower.replace("comments", "").replace("k", "000").strip()
                comments = int(float(comments_str))
            except:
                pass
        elif m.startswith("r/"):
            subreddit = m
    
    return score, comments, subreddit


def fetch_subreddit_native(subreddit: str, sort: str = "hot", limit: int = 25) -> List[Dict]:
    """使用 Reddit JSON API 抓取"""
    url = f"{BASE_URL}/r/{subreddit}/{sort}.json?limit={limit}"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        items = []
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            
            if post.get("stickied") or post.get("is_promoted"):
                continue
            
            items.append({
                "platform": "Reddit",
                "title": post.get("title", ""),
                "text": post.get("selftext", "")[:2000],
                "url": urljoin(BASE_URL, post.get("permalink", "")),
                "external_url": post.get("url", ""),
                "author": post.get("author", "unknown"),
                "published_at": datetime.fromtimestamp(
                    post.get("created_utc", 0)
                ).isoformat(),
                "engagement": {
                    "score": post.get("score", 0),
                    "comments": post.get("num_comments", 0),
                    "upvote_ratio": post.get("upvote_ratio", 0)
                },
                "subreddit": post.get("subreddit", ""),
                "is_self": post.get("is_self", False)
            })
        
        return items
    
    except Exception as e:
        print(f"  ✗ r/{subreddit} native failed: {e}")
        return []


def fetch_subreddit_autocli(subreddit: str, limit: int = 25) -> List[Dict]:
    """使用 autocli 抓取"""
    # Note: autocli reddit 没有直接的 subreddit feed 命令
    # 使用 search 模拟
    cmd = f'autocli social reddit search "subreddit:{subreddit}" --limit {limit} --json 2>/dev/null'
    success, stdout, stderr = run_autocli(cmd, timeout=30)
    
    if not success or not stdout:
        return []
    
    try:
        data = json.loads(stdout)
        if isinstance(data, dict) and "data" in data:
            raw_items = data["data"].get("items", [])
            
            items = []
            for item in raw_items:
                metrics = item.get("metrics", [])
                score, comments, sub = parse_reddit_metrics(metrics)
                
                items.append({
                    "platform": "Reddit",
                    "title": item.get("title", ""),
                    "text": item.get("text", "")[:2000],
                    "url": item.get("url", ""),
                    "author": item.get("username", "unknown"),
                    "published_at": item.get("publishedAt", ""),
                    "engagement": {
                        "score": score,
                        "comments": comments,
                        "metrics": metrics
                    },
                    "subreddit": sub,
                    "raw": item
                })
            
            return items
    except Exception as e:
        print(f"  ✗ r/{subreddit} autocli failed: {e}")
    
    return []


def search_reddit_autocli(queries: List[str], limit: int = 15) -> List[Dict]:
    """使用 autocli search"""
    all_items = []
    
    for query in queries:
        cmd = f'autocli social reddit search "{query}" --limit {limit} --json 2>/dev/null'
        success, stdout, stderr = run_autocli(cmd, timeout=30)
        
        if not success or not stdout:
            continue
        
        try:
            data = json.loads(stdout)
            if isinstance(data, dict) and "data" in data:
                raw_items = data["data"].get("items", [])
                
                for item in raw_items:
                    metrics = item.get("metrics", [])
                    score, comments, sub = parse_reddit_metrics(metrics)
                    
                    all_items.append({
                        "platform": "Reddit",
                        "title": item.get("title", ""),
                        "text": item.get("text", "")[:2000],
                        "url": item.get("url", ""),
                        "author": item.get("username", "unknown"),
                        "published_at": item.get("publishedAt", ""),
                        "engagement": {
                            "score": score,
                            "comments": comments,
                            "metrics": metrics
                        },
                        "subreddit": sub,
                        "raw": item
                    })
        except Exception as e:
            print(f"  ✗ search '{query}' failed: {e}")
    
    return all_items


def fetch_reddit(
    mode: str = "native",
    subreddits: List[str] = None,
    search_queries: List[str] = None,
    min_score: int = None,
    min_comments: int = None
) -> List[Dict]:
    """
    抓取 Reddit 内容
    
    Args:
        mode: "native" 或 "autocli"
        subreddits: 要抓取的 subreddit 列表 (native 模式)
        search_queries: 搜索关键词 (autocli 模式)
        min_score: 最小分数阈值
        min_comments: 最小评论数阈值
    
    Returns:
        过滤后的内容列表
    """
    threshold = config.get_threshold("reddit")
    min_score = min_score or threshold.get("score", 10)
    min_comments = min_comments or threshold.get("comments", 5)
    
    print(f"📱 Fetching Reddit (mode: {mode})...")
    
    # 检查 autocli 可用性
    if mode == "autocli" and not has_autocli():
        print("⚠️  autocli not found, falling back to native mode")
        mode = "native"
    
    # 抓取
    all_items = []
    
    if mode == "autocli" and has_autocli():
        # autocli 模式: 使用 search
        if search_queries is None:
            search_queries = [
                "AI agent",
                "artificial intelligence",
                "machine learning",
                "LLM ChatGPT Claude",
                "AI automation"
            ]
        all_items = search_reddit_autocli(search_queries, limit=15)
    else:
        # native 模式: 抓取 subreddit hot
        if subreddits is None:
            subreddits = [
                "MachineLearning",
                "artificial",
                "ChatGPT",
                "ClaudeAI",
                "LocalLLaMA",
                "AI_Agents",
                "singularity",
                "OpenAI"
            ]
        
        for sub in subreddits:
            items = fetch_subreddit_native(sub, sort="hot", limit=25)
            all_items.extend(items)
            print(f"  ✓ r/{sub}: {len(items)} items")
            time.sleep(0.5)  # 礼貌间隔
    
    # 过滤
    cutoff = datetime.now() - timedelta(hours=24)
    filtered = []
    seen = set()
    
    for item in all_items:
        # 去重
        key = item.get("url", "") or f"{item['title'][:50]}_{item['author']}"
        if key in seen:
            continue
        seen.add(key)
        
        # 时间过滤
        try:
            pub_time = datetime.fromisoformat(item["published_at"].replace("Z", "+00:00"))
            if pub_time < cutoff:
                continue
        except:
            pass
        
        # 质量过滤
        eng = item["engagement"]
        score = eng.get("score", 0)
        comments = eng.get("comments", 0)
        
        if score >= min_score or comments >= min_comments:
            filtered.append(item)
    
    print(f"✅ Reddit: {len(filtered)} items after filtering (from {len(all_items)} raw)")
    return filtered


if __name__ == "__main__":
    import sys
    
    mode = sys.argv[1] if len(sys.argv) > 1 else "native"
    items = fetch_reddit(mode=mode)
    print(f"\nTotal: {len(items)} items")
    for item in items[:3]:
        sub = item.get('subreddit', 'unknown')
        score = item['engagement']['score']
        print(f"- r/{sub}: {item['title'][:60]}... (score: {score})")
