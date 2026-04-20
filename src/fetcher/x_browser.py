"""
AI_HUB Daily - X/Twitter Browser Fetcher
使用 OpenClaw browser + 已登录态抓取 X 搜索结果
"""

import json
import time
from typing import List, Dict, Optional


def parse_x_snapshot(snapshot_text: str, search_url: str = "") -> List[Dict]:
    """
    从 browser snapshot 文本解析 X 推文
    
    Args:
        snapshot_text: accessibility snapshot 文本
        search_url: 搜索 URL
    
    Returns:
        推文列表
    """
    items = []
    
    # snapshot 是结构化的，我们需要找到 article 元素
    # 这里用简单文本匹配提取
    lines = snapshot_text.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # 找 article 开头（包含用户名）
        if 'article' in line.lower() and ('@' in line or 'Verified' in line):
            tweet = _parse_article(lines, i)
            if tweet:
                items.append(tweet)
                i += tweet.get('_line_span', 30)
                continue
        i += 1
    
    return items


def _parse_article(lines: List[str], start: int) -> Optional[Dict]:
    """从 snapshot lines 解析单条推文"""
    # 收集 article 块（到下一个 article 或 30 行）
    block = '\n'.join(lines[start:start + 30])
    
    # 提取用户名
    import re
    author_match = re.search(r'@(\w+)', block)
    author = author_match.group(1) if author_match else "unknown"
    
    # 提取日期
    date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}', block)
    date_str = date_match.group(0) if date_match else ""
    
    # 提取文本内容（在用户名/日期之后，replies/likes 之前）
    text_parts = []
    capturing = False
    for line in lines[start:start + 25]:
        s = line.strip()
        if capturing:
            if any(kw in s for kw in ['Replies', 'reposts', 'Likes', 'views', 'Bookmark', 'Share']):
                break
            if s and not s.startswith(('statictext', 'link', 'button', 'image', 'video')):
                text_parts.append(s)
        if '@' in s and not capturing:
            capturing = True
            continue
    
    text = ' '.join(text_parts).strip()
    if len(text) < 10:
        return None
    
    # 提取 engagement
    likes = 0
    reposts = 0
    replies = 0
    views = 0
    
    likes_match = re.search(r'(\d[\d,]*)\s*Likes', block)
    if likes_match:
        likes = int(likes_match.group(1).replace(',', ''))
    
    reposts_match = re.search(r'(\d[\d,]*)\s*reposts', block)
    if reposts_match:
        reposts = int(reposts_match.group(1).replace(',', ''))
    
    replies_match = re.search(r'(\d[\d,]*)\s*Replies', block)
    if replies_match:
        replies = int(replies_match.group(1).replace(',', ''))
    
    views_match = re.search(r'(\d[\d,.]*K?)\s*views', block)
    if views_match:
        v = views_match.group(1).replace(',', '')
        if 'K' in v:
            views = int(float(v.replace('K', '')) * 1000)
        else:
            views = int(v)
    
    return {
        "platform": "X",
        "title": text[:200],
        "text": text,
        "url": f"https://x.com/{author}",
        "author": author,
        "published_at": date_str,
        "engagement": {
            "likes": likes,
            "retweets": reposts,
            "replies": replies,
            "views": views,
        },
        "raw": {"author": author, "text": text[:100]},
    }


def fetch_x_browser(search_queries: List[str] = None, min_likes: int = 20, min_retweets: int = 5) -> List[Dict]:
    """
    使用 browser 抓取 X 搜索结果
    
    注意：需要通过 OpenClaw browser 工具调用，此函数提供解析逻辑
    """
    if search_queries is None:
        search_queries = [
            "AI agent",
            "LLM GPT Claude",
            "AI automation",
            "machine learning",
        ]
    
    # 这个函数的调用方式比较特殊：
    # 虾宝在 main 层用 browser 工具打开搜索页，拿到 snapshot，
    # 然后调用 parse_x_snapshot 解析
    #
    # 不在这里直接调 browser，因为 browser 是 OpenClaw 工具层能力
    
    print("📱 X Browser fetcher requires caller to use OpenClaw browser tool")
    print("   Use: browser(open, url=x.com/search?q=...) -> snapshot -> parse_x_snapshot()")
    return []


if __name__ == "__main__":
    # 测试：读取一个 snapshot 文件
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            text = f.read()
        items = parse_x_snapshot(text)
        print(f"Parsed {len(items)} tweets")
        for item in items[:5]:
            e = item['engagement']
            print(f"  @{item['author']}: {item['text'][:60]}... ({e['likes']}❤️ {e['retweets']}🔄)")
