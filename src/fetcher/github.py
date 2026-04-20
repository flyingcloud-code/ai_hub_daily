"""
AI_HUB Daily - GitHub Fetcher
支持两种模式:
1. Native: GitHub API (公开，有速率限制)
2. Autocli: 通过 autocli 命令
"""

import json
import os
import subprocess
import requests
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
    except FileNotFoundError:
        return False, "", "autocli not found"


def has_autocli() -> bool:
    """检查 autocli 是否安装"""
    success, _, _ = run_autocli("autocli --version")
    return success


def get_github_token() -> str:
    """从环境变量获取 GitHub Token"""
    return os.environ.get("GITHUB_TOKEN", "")


def fetch_trending_native(limit: int = 30) -> List[Dict]:
    """使用 GitHub API 抓取 trending"""
    token = get_github_token()
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    # GitHub API 没有直接的 trending endpoint
    # 使用搜索最近创建的 repos
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    url = "https://api.github.com/search/repositories"
    params = {
        "q": f"AI OR LLM OR agent OR chatgpt created:>{cutoff}",
        "sort": "stars",
        "order": "desc",
        "per_page": limit
    }
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        items = []
        for repo in data.get("items", []):
            items.append({
                "platform": "GitHub",
                "title": repo.get("full_name", ""),
                "text": repo.get("description", ""),
                "url": repo.get("html_url", ""),
                "author": repo.get("owner", {}).get("login", ""),
                "published_at": repo.get("created_at", ""),
                "engagement": {
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0)
                },
                "language": repo.get("language", ""),
                "topics": repo.get("topics", [])
            })
        
        return items
    except Exception as e:
        print(f"  ✗ GitHub trending failed: {e}")
        return []


def fetch_trending_autocli(limit: int = 30) -> List[Dict]:
    """使用 autocli"""
    if not has_autocli():
        return []
    
    # autocli web github-trending
    cmd = f"autocli web github-trending --limit {limit} --json 2>/dev/null"
    success, stdout, stderr = run_autocli(cmd, timeout=30)
    
    if not success or not stdout:
        return []
    
    try:
        data = json.loads(stdout)
        items = data if isinstance(data, list) else []
        
        # 转换为统一格式
        formatted = []
        for item in items:
            formatted.append({
                "platform": "GitHub",
                "title": item.get("full_name") or item.get("name", ""),
                "text": item.get("description", ""),
                "url": item.get("html_url", ""),
                "author": item.get("owner", {}).get("login", "") if isinstance(item.get("owner"), dict) else "",
                "published_at": item.get("created_at", ""),
                "engagement": {
                    "stars": item.get("stargazers_count", 0) or item.get("stars", 0),
                    "forks": item.get("forks_count", 0)
                },
                "language": item.get("language", "")
            })
        
        return formatted
    except Exception as e:
        print(f"  ✗ autocli trending failed: {e}")
        return []


def fetch_github(
    mode: str = "native",
    limit: int = 30,
    min_stars: int = None
) -> List[Dict]:
    """
    抓取 GitHub 内容
    
    Args:
        mode: "native" 或 "autocli"
        limit: 数量限制
        min_stars: 最小星标数
    """
    threshold = config.get_threshold("github")
    min_stars = min_stars or threshold.get("stars", 50)
    
    print(f"📱 Fetching GitHub (mode: {mode})...")
    
    if mode == "autocli" and has_autocli():
        items = fetch_trending_autocli(limit)
    else:
        if mode == "autocli" and not has_autocli():
            print("⚠️  autocli not found, using native mode")
        items = fetch_trending_native(limit)
    
    # 过滤
    filtered = []
    for item in items:
        if item["engagement"]["stars"] >= min_stars:
            filtered.append(item)
    
    print(f"✅ GitHub: {len(filtered)} items after filtering (from {len(items)} raw)")
    return filtered


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "native"
    items = fetch_github(mode=mode)
    print(f"\nTotal: {len(items)} items")
    for item in items[:3]:
        print(f"- {item['title']}: {item['engagement']['stars']} stars")
