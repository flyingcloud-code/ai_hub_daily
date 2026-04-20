"""
AI_HUB Daily - Reddit Fetcher
使用 autocli 搜索 Reddit 公开内容
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


def parse_metrics(metrics: List[str]) -> tuple:
    """解析 Reddit metrics"""
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


def is_within_24h(published_at: str) -> bool:
    """检查是否在 24 小时内"""
    if not published_at:
        return True  # 没有时间默认保留
    
    try:
        # 处理 ISO 格式
        dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        return datetime.now(dt.tzinfo) - dt < timedelta(hours=24)
    except:
        return True


def fetch_reddit(queries: List[str] = None, limit: int = 15) -> List[Dict]:
    """
    抓取 Reddit 内容
    
    Args:
        queries: 搜索关键词列表
        limit: 每个关键词抓取数量
    
    Returns:
        过滤后的内容列表
    """
    if queries is None:
        queries = [
            "AI agent",
            "artificial intelligence",
            "machine learning",
            "LLM ChatGPT Claude",
            "AI automation"
        ]
    
    print("📱 Fetching Reddit...")
    
    all_items = []
    threshold = config.get_threshold("reddit")
    
    for query in queries:
        cmd = f'autocli social reddit search "{query}" --limit {limit} --json 2>/dev/null'
        success, stdout, stderr = run_autocli(cmd, timeout=30)
        
        if not success or not stdout:
            continue
        
        try:
            data = json.loads(stdout)
            if isinstance(data, dict) and "data" in data:
                items = data["data"].get("items", [])
                all_items.extend(items)
                print(f"  ✓ '{query}': {len(items)} items")
        except Exception as e:
            print(f"  ✗ '{query}': parse error - {e}")
    
    # 过滤与去重
    seen = set()
    filtered = []
    
    for item in all_items:
        item_id = item.get("id")
        if not item_id or item_id in seen:
            continue
        seen.add(item_id)
        
        # 解析 metrics
        metrics = item.get("metrics", [])
        score, comments, subreddit = parse_metrics(metrics)
        
        # 时间过滤
        published = item.get("publishedAt", "")
        if not is_within_24h(published):
            continue
        
        # 质量阈值过滤
        if score >= threshold.get("score", 10) or comments >= threshold.get("comments", 5):
            filtered.append({
                "platform": "Reddit",
                "title": item.get("title", ""),
                "text": item.get("text", "")[:1000],
                "url": item.get("url", ""),
                "author": item.get("username", "unknown"),
                "published_at": published,
                "engagement": {
                    "score": score,
                    "comments": comments,
                    "metrics": metrics
                },
                "subreddit": subreddit,
                "raw": item
            })
    
    print(f"✅ Reddit: {len(filtered)} items after filtering")
    return filtered


if __name__ == "__main__":
    items = fetch_reddit()
    print(f"\nTotal: {len(items)} items")
    for item in items[:3]:
        print(f"- {item['title'][:60]}... (score: {item['engagement']['score']})")
