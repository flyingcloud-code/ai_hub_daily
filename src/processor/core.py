"""
AI_HUB Daily - Content Processor
质量评分、分类、去重
"""

import hashlib
from typing import List, Dict, Tuple
from ..utils.config import config


def calculate_quality_score(item: Dict) -> float:
    """
    计算内容质量分数 0-100
    
    算法:
    - Reddit: score/10 + comments*2
    - HN: points + comments*3
    - GitHub: stars/50
    - X: likes/10 + retweets*2
    - Zhihu: votes/5
    """
    platform = item.get("platform", "")
    engagement = item.get("engagement", {})
    score = 0.0
    
    if platform == "Reddit":
        s = engagement.get("score", 0)
        c = engagement.get("comments", 0)
        score = (s / 10) + (c * 2)
    elif platform == "HackerNews":
        p = engagement.get("points", 0)
        c = engagement.get("comments", 0)
        score = p + (c * 3)
    elif platform == "GitHub":
        s = engagement.get("stars", 0)
        score = s / 50
    elif platform == "X":
        l = engagement.get("likes", 0)
        r = engagement.get("retweets", 0)
        score = (l / 10) + (r * 2)
    elif platform == "Zhihu":
        v = engagement.get("votes", 0)
        score = v / 5
    
    return min(100.0, round(score, 1))


def classify_content(item: Dict) -> List[str]:
    """
    智能分类 - 基于关键词匹配
    返回多个可能分类
    """
    text = f"{item.get('title', '')} {item.get('text', '')}".lower()
    categories = config.get_categories()
    
    matched = []
    for cat, keywords in categories.items():
        if cat == "AI_General":
            continue
        if any(kw.lower() in text for kw in keywords):
            matched.append(cat)
    
    # 兜底
    if not matched:
        matched = ["AI_General"]
    
    return matched


def generate_content_hash(item: Dict) -> str:
    """生成内容指纹用于去重"""
    content = f"{item.get('title', '')}{item.get('url', '')}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def deduplicate(items: List[Dict]) -> Tuple[List[Dict], int]:
    """
    去重
    
    Returns:
        (去重后的列表, 去重数量)
    """
    seen = set()
    unique = []
    
    for item in items:
        content_hash = generate_content_hash(item)
        if content_hash not in seen:
            seen.add(content_hash)
            unique.append(item)
    
    return unique, len(items) - len(unique)


def process_items(items: List[Dict]) -> List[Dict]:
    """
    处理内容列表
    
    流程:
    1. 去重
    2. 质量评分
    3. 智能分类
    4. 生成摘要
    """
    # 去重
    unique_items, dup_count = deduplicate(items)
    print(f"📊 Deduplicated: {dup_count} removed, {len(unique_items)} remaining")
    
    # 处理每个条目
    processed = []
    for item in unique_items:
        # 质量评分
        item["quality_score"] = calculate_quality_score(item)
        
        # 分类
        item["categories"] = classify_content(item)
        
        # 内容指纹
        item["id"] = generate_content_hash(item)
        
        # 简单摘要（可扩展为 LLM 摘要）
        text = item.get("text", "")
        if len(text) > 300:
            item["summary"] = text[:300].rsplit(" ", 1)[0] + "..."
        else:
            item["summary"] = text
        
        processed.append(item)
    
    # 按质量排序
    processed.sort(key=lambda x: x["quality_score"], reverse=True)
    
    return processed


def detect_trends(current: List[Dict], previous: List[Dict] = None) -> Dict:
    """
    趋势分析
    
    Returns:
        {
            "total_change": "+5" or "N/A",
            "hot_categories": [(cat, count), ...],
            "new_patterns": ["keyword1", ...]
        }
    """
    trends = {
        "total_change": "N/A",
        "hot_categories": [],
        "new_patterns": []
    }
    
    if previous:
        total_change = len(current) - len(previous)
        trends["total_change"] = f"+{total_change}" if total_change > 0 else str(total_change)
    
    # 分类统计
    cat_counts = {}
    for item in current:
        for cat in item.get("categories", []):
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    trends["hot_categories"] = sorted(
        cat_counts.items(), key=lambda x: x[1], reverse=True
    )[:5]
    
    # 新趋势检测
    keywords = ["mcp", "claude code", "reasoning", "multimodal", "local llm", "apple silicon"]
    found = set()
    for item in current:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        for kw in keywords:
            if kw in text:
                found.add(kw)
    trends["new_patterns"] = list(found)[:3]
    
    return trends


if __name__ == "__main__":
    # 测试
    test_items = [
        {
            "platform": "Reddit",
            "title": "How to build AI agents",
            "text": "Tutorial on building agents with LangGraph",
            "url": "https://reddit.com/r/AI_Agents/xxx",
            "engagement": {"score": 100, "comments": 50}
        }
    ]
    
    result = process_items(test_items)
    print(f"\nProcessed: {result[0]}")
