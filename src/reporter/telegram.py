"""
AI_HUB Daily - Telegram Reporter
生成 Telegram 格式的日报
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


def load_today_data(data_dir: Path, date: str) -> List[Dict]:
    """加载今日处理后的数据"""
    json_file = data_dir / f"{date}.json"
    if not json_file.exists():
        return []
    
    import json
    with open(json_file, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_trends(current: List[Dict], previous: List[Dict]) -> Dict:
    """计算趋势变化"""
    trends = {
        "total_change": "N/A",
        "category_changes": []
    }
    
    if previous:
        total_change = len(current) - len(previous)
        trends["total_change"] = f"+{total_change}" if total_change > 0 else str(total_change)
    
    # 分类统计
    today_cats = {}
    for item in current:
        for cat in item.get("categories", []):
            today_cats[cat] = today_cats.get(cat, 0) + 1
    
    yesterday_cats = {}
    for item in previous:
        for cat in item.get("categories", []):
            yesterday_cats[cat] = yesterday_cats.get(cat, 0) + 1
    
    # 变化
    all_cats = set(today_cats.keys()) | set(yesterday_cats.keys())
    changes = []
    for cat in all_cats:
        t = today_cats.get(cat, 0)
        y = yesterday_cats.get(cat, 0)
        if t != y:
            changes.append((cat, t - y, t))
    
    changes.sort(key=lambda x: abs(x[1]), reverse=True)
    trends["category_changes"] = changes[:5]
    
    return trends


def generate_insights(items: List[Dict]) -> List[str]:
    """生成深度洞察"""
    insights = []
    
    # 热门分类
    cat_counts = {}
    for item in items:
        for cat in item.get("categories", []):
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    if cat_counts:
        top_cat = max(cat_counts.items(), key=lambda x: x[1])
        if top_cat[1] > 10:
            insights.append(f"🔥 **{top_cat[0]}** 是今日绝对热点（{top_cat[1]} 条）")
    
    # 活跃平台
    platform_counts = {}
    for item in items:
        p = item["platform"]
        platform_counts[p] = platform_counts.get(p, 0) + 1
    
    if platform_counts:
        top_platform = max(platform_counts.items(), key=lambda x: x[1])
        insights.append(f"📱 **{top_platform[0]}** 是今日最活跃平台（{top_platform[1]} 条）")
    
    # 高质量内容
    high_quality = [i for i in items if i.get("quality_score", 0) > 70]
    if high_quality:
        insights.append(f"⭐ 发现 **{len(high_quality)}** 条高质量内容（>70分）")
    
    # 新趋势
    keywords = ["mcp", "claude code", "reasoning", "multimodal", "local llm", "apple silicon"]
    found = []
    for item in items:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        for kw in keywords:
            if kw in text and kw not in found:
                found.append(kw)
    
    if found:
        insights.append(f"🆕 新趋势: {', '.join(found[:2])}")
    
    return insights


def format_engagement(item: Dict) -> str:
    """格式化 engagement 数据"""
    engagement = item.get("engagement", {})
    platform = item.get("platform", "")
    
    if platform == "Reddit":
        return f"🔼{engagement.get('score', 0)} 💬{engagement.get('comments', 0)}"
    elif platform == "HackerNews":
        return f"🔼{engagement.get('points', 0)} 💬{engagement.get('comments', 0)}"
    elif platform == "GitHub":
        return f"⭐{engagement.get('stars', 0)}"
    elif platform == "X":
        return f"❤️{engagement.get('likes', 0)} 🔄{engagement.get('retweets', 0)}"
    elif platform == "Zhihu":
        return f"👍{engagement.get('votes', 0)}"
    elif platform == "Dev.to":
        return f"❤️{engagement.get('likes', 0)} 💬{engagement.get('comments', 0)}"
    elif platform == "ProductHunt":
        return f"🔺{engagement.get('votes', 0)}"
    
    return ""


def generate_message(items: List[Dict], trends: Dict, date: str) -> str:
    """生成 Telegram 消息"""
    if not items:
        return "📭 今日暂无高质量 AI 内容"
    
    # 统计
    total = len(items)
    by_platform = {}
    by_category = {}
    high_quality = 0
    
    for item in items:
        p = item["platform"]
        by_platform[p] = by_platform.get(p, 0) + 1
        
        for c in item.get("categories", []):
            by_category[c] = by_category.get(c, 0) + 1
        
        if item.get("quality_score", 0) > 50:
            high_quality += 1
    
    # 排序
    sorted_items = sorted(items, key=lambda x: x.get("quality_score", 0), reverse=True)
    top_items = sorted_items[:8]
    
    # 平台 emoji
    platform_emoji = {
        "Reddit": "🔴",
        "HackerNews": "🟠",
        "GitHub": "⚫",
        "X": "⚪",
        "Zhihu": "🔵",
        "Dev.to": "🟢",
        "ProductHunt": "🟡",
    }
    
    # 构建消息
    msg = f"""📊 <b>AI_HUB 日报 V2 - {date}</b>

🎯 <b>今日总览</b>
总条目: <b>{total}</b> | 高质量: <b>{high_quality}</b> | 环比: <b>{trends['total_change']}</b>

📈 <b>平台分布</b>
"""
    
    for p, c in sorted(by_platform.items(), key=lambda x: -x[1]):
        emoji = platform_emoji.get(p, "•")
        msg += f"{emoji} {p}: {c} 条\n"
    
    msg += f"\n🏷️ <b>热门分类</b>\n"
    for cat, count in sorted(by_category.items(), key=lambda x: -x[1])[:5]:
        msg += f"• {cat}: {count} 条\n"
    
    # 趋势变化
    if trends["category_changes"]:
        msg += f"\n📊 <b>趋势变化</b>\n"
        for cat, change, total in trends["category_changes"][:3]:
            emoji = "📈" if change > 0 else "📉"
            msg += f"{emoji} {cat}: {change:+d} (共{total})\n"
    
    # 深度洞察
    insights = generate_insights(items)
    if insights:
        msg += f"\n💡 <b>今日洞察</b>\n"
        for insight in insights[:4]:
            msg += f"{insight}\n"
    
    # 精选内容
    msg += f"\n🔥 <b>精选内容 TOP 5</b>\n"
    
    for idx, item in enumerate(top_items[:5], 1):
        score = item.get("quality_score", 0)
        
        title = item.get("title", "")[:60]
        if len(item.get("title", "")) > 60:
            title += "..."
        
        summary = item.get("summary", "")[:80]
        if len(item.get("summary", "")) > 80:
            summary = summary.rsplit(" ", 1)[0] + "..."
        
        eng_str = format_engagement(item)
        
        msg += f"""
{idx}. <b>[{item['platform']}]</b> <a href="{item['url']}">{title}</a>
   <i>{summary}</i>
   {eng_str} | 质量: <b>{score}</b> | {', '.join(item['categories'][:1])}"""
    
    msg += f"""

📍 <i>完整报告见 AI_HUB/02_Processed/{date}.md</i>
<i>Generated by AI_HUB V2 🤖</i>"""
    
    return msg


def generate_report(
    data_dir: Path,
    output_dir: Path,
    date: str,
    previous_date: Optional[str] = None
) -> str:
    """
    生成完整报告
    
    Args:
        data_dir: 处理后数据目录
        output_dir: 报告输出目录
        date: 日期 (YYYY-MM-DD)
        previous_date: 前一天日期 (用于趋势对比)
    
    Returns:
        Telegram 消息文本
    """
    # 加载数据
    today_items = load_today_data(data_dir, date)
    
    # 加载昨日数据
    previous_items = []
    if previous_date:
        previous_items = load_today_data(data_dir, previous_date)
    
    # 计算趋势
    trends = calculate_trends(today_items, previous_items)
    
    # 生成消息
    message = generate_message(today_items, trends, date)
    
    # 保存
    output_dir.mkdir(parents=True, exist_ok=True)
    
    txt_file = output_dir / f"{date}_telegram.txt"
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(message)
    
    print(f"✅ Report saved: {txt_file}")
    
    return message


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI_HUB Telegram Reporter")
    parser.add_argument("--data-dir", required=True, help="Processed data directory")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Date (YYYY-MM-DD)")
    parser.add_argument("--previous-date", help="Previous date for comparison")
    
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        exit(1)
    
    # 自动计算前一天
    previous_date = args.previous_date
    if not previous_date:
        try:
            date_obj = datetime.strptime(args.date, "%Y-%m-%d")
            previous_date = (date_obj - timedelta(days=1)).strftime("%Y-%m-%d")
        except:
            pass
    
    message = generate_report(data_dir, output_dir, args.date, previous_date)
    
    print("\n" + "=" * 50)
    print("REPORT PREVIEW:")
    print("=" * 50)
    print(message[:1500] + "..." if len(message) > 1500 else message)


if __name__ == "__main__":
    main()


# Legacy main (kept for backward compatibility)
def _legacy_main():
    import sys
    
    date = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    data_dir = Path("/Users/Shared/obsidian_share/mini-claw/AI_HUB/02_Processed")
    output_dir = Path("/Users/Shared/obsidian_share/mini-claw/AI_HUB/04_Daily_Report")
    
    message = generate_report(data_dir, output_dir, date, yesterday)
    print("\n" + "=" * 50)
    print("MESSAGE PREVIEW:")
    print("=" * 50)
    print(message[:1500] + "..." if len(message) > 1500 else message)
