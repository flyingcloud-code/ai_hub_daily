"""
AI_HUB Daily - Product Hunt Fetcher
使用 Product Hunt RSS 抓取 AI 产品
"""

import re
import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timedelta
from typing import List, Dict

from ..utils.config import config

PH_RSS = "https://www.producthunt.com/feed"


def parse_ph_date(date_str: str) -> str:
    """解析 RSS 日期格式"""
    try:
        # RFC 2822 格式
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except:
        return ""


def is_within_7d(date_str: str) -> bool:
    """检查是否在 7 天内"""
    if not date_str:
        return True
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(date_str)
        return datetime.now(dt.tzinfo) - dt < timedelta(days=7)
    except:
        return True


def fetch_producthunt(topic: str = "artificial-intelligence", limit: int = 15) -> List[Dict]:
    """
    抓取 Product Hunt AI 产品
    
    Args:
        topic: PH topic slug
        limit: 最大数量
    
    Returns:
        过滤后的内容列表
    """
    print("📱 Fetching Product Hunt...")
    
    all_items = []
    
    # 尝试多个 feed URL
    feed_urls = [
        f"{PH_RSS}?category=artificial-intelligence",
        f"{PH_RSS}",
    ]
    
    for url in feed_urls:
        try:
            resp = requests.get(url, headers={"User-Agent": "AI_HUB_Daily/2.0"}, timeout=15)
            if resp.status_code != 200:
                continue
            
            root = ET.fromstring(resp.text)
            
            # RSS 2.0 结构
            ns = {
                "dc": "http://purl.org/dc/elements/1.1/",
                "content": "http://purl.org/rss/1.0/modules/content/",
            }
            
            items = root.findall(".//item")
            count = 0
            
            for item in items:
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                desc = item.findtext("description", "")[:300]
                pub_date = item.findtext("pubDate", "")
                author = item.findtext("dc:creator", "", ns) or "unknown"
                
                # 过滤 AI 相关
                text_lower = f"{title} {desc}".lower()
                ai_keywords = ["ai", "artificial intelligence", "machine learning", "llm", 
                              "gpt", "claude", "agent", "automation", "neural", "model",
                              "chatbot", "copilot", "assistant", "generative"]
                
                if not any(kw in text_lower for kw in ai_keywords):
                    continue
                
                if not is_within_7d(pub_date):
                    continue
                
                # 从 description 提取 votes
                votes = 0
                vote_match = re.search(r'(\d+)\s*upvotes?', desc, re.IGNORECASE)
                if vote_match:
                    votes = int(vote_match.group(1))
                
                all_items.append({
                    "platform": "ProductHunt",
                    "title": title,
                    "text": re.sub(r'<[^>]+>', '', desc),
                    "url": link,
                    "author": author,
                    "published_at": parse_ph_date(pub_date),
                    "engagement": {
                        "votes": votes,
                        "comments": 0,
                    },
                    "raw": {"title": title, "link": link, "desc": desc},
                })
                count += 1
                
                if len(all_items) >= limit:
                    break
            
            print(f"  ✓ ProductHunt RSS: {count} items")
            break  # 第一个成功的 URL 就够
        
        except Exception as e:
            print(f"  ✗ ProductHunt {url}: {e}")
            continue
    
    print(f"✅ ProductHunt: {len(all_items)} items after filtering")
    return all_items


if __name__ == "__main__":
    items = fetch_producthunt()
    print(f"\nTotal: {len(items)} items")
    for item in items[:5]:
        print(f"  - {item['title'][:60]}")
