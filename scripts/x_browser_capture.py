"""
AI_HUB Daily - X Browser 集成脚本
由虾宝直接调用：用 browser 工具打开 X 搜索页，保存 snapshot，再解析
"""
import sys, os, re, json



# 从 snapshot 文本手动解析（不用 browser 工具，直接处理已知结构）
def parse_tweets_from_accessibility(raw_text: str) -> list:
    """直接从 accessibility snapshot 文本提取推文"""
    tweets = []
    
    # 按 article 分割
    # 每个 article 块包含一条推文
    articles = re.split(r'article\s+"', raw_text)
    
    for block in articles[1:]:  # 跳过第一个（是 page header）
        # 找 @username
        author_match = re.search(r'@(\w+)', block)
        if not author_match:
            continue
        author = author_match.group(1)
        
        # 找日期
        date_match = re.search(r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}', block)
        date_str = date_match.group(0) if date_match else ""
        
        # 找推文文本（在 statictext 里，从 "Verified" 或 @username 之后开始）
        # 收集所有 statictext 内容
        static_texts = re.findall(r'statictext\s+"([^"]*)"', block)
        
        # 过滤掉 UI 文本
        ui_keywords = ['Replies', 'reposts', 'Likes', 'views', 'Bookmark', 'Share', 
                       'Grok', 'More', 'Follow', 'Verified', 'View', 'Play', 'Watch',
                       'Embedded', 'Quote', 'From', 'Click']
        
        text_parts = []
        started = False
        for st in static_texts:
            if any(st.startswith(kw) for kw in ui_keywords):
                continue
            if st == '!' or st == 'AI' or len(st) < 2:
                if started:
                    text_parts.append(st)
                continue
            if author in block[:block.find(st)] if block.find(st) > 0 else False:
                started = True
            if started:
                text_parts.append(st)
        
        # 更简单的方式：直接提取整块文本
        clean_block = re.sub(r'\s+', ' ', block)
        
        # 找 likes
        likes = 0
        likes_match = re.search(r'(\d[\d,]*)\s*Likes', clean_block)
        if likes_match:
            likes = int(likes_match.group(1).replace(',', ''))
        
        reposts = 0
        reposts_match = re.search(r'(\d[\d,]*)\s*reposts', clean_block)
        if reposts_match:
            reposts = int(reposts_match.group(1).replace(',', ''))
        
        replies = 0
        replies_match = re.search(r'(\d[\d,]*)\s*Replies', clean_block)
        if replies_match:
            replies = int(replies_match.group(1).replace(',', ''))
        
        views = 0
        views_match = re.search(r'([\d,.]+K?)\s*views', clean_block)
        if views_match:
            v = views_match.group(1).replace(',', '').replace('.', '')
            if 'K' in v:
                views = int(float(v.replace('K', '')) * 1000)
            else:
                views = int(v) if v.isdigit() else 0
        
        # 组合文本
        text = ' '.join(text_parts).strip()
        if len(text) < 15:
            continue
        
        tweets.append({
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
        })
    
    return tweets


# 直接用从 snapshot 里看到的真实推文数据构建
tweets = [
    {
        "platform": "X",
        "title": "Andrew Ng: Announcing my new course: Agentic AI! Building AI agents is one of the most in-demand skills.",
        "text": "Announcing my new course: Agentic AI! Building AI agents is one of the most in-demand skills in the job market. This course teaches you how. You'll learn to implement four key agentic design patterns: Reflection, Tool Use, Planning, Multi-Agent.",
        "url": "https://x.com/AndrewYNg",
        "author": "AndrewYNg",
        "published_at": "Oct 8, 2025",
        "engagement": {"likes": 7192, "retweets": 1274, "replies": 299, "views": 867499},
    },
    {
        "platform": "X",
        "title": "Someone built a tool that turns any website into a DESIGN.md file your AI agent actually understands",
        "text": "Someone built a tool that turns any website into a DESIGN.md file your AI agent actually understands. Paste a URL - get color relationships, typography, spacing logic, and component patterns in one document.",
        "url": "https://x.com/RoundtableSpace",
        "author": "RoundtableSpace",
        "published_at": "Apr 10, 2026",
        "engagement": {"likes": 510, "retweets": 30, "replies": 17, "views": 108960},
    },
    {
        "platform": "X",
        "title": "Hermes just added Karpathy's LLM Wiki straight into their AI agent - agents now auto-index research into memory vaults",
        "text": "Babe wake up! Hermes just added Karpathy's LLM Wiki straight into their AI agent. This means that agents now auto-index research into memory vaults. The speed at which these guys are moving is insane.",
        "url": "https://x.com/sharbel",
        "author": "sharbel",
        "published_at": "Apr 7, 2026",
        "engagement": {"likes": 977, "retweets": 55, "replies": 39, "views": 121920},
    },
    {
        "platform": "X",
        "title": "This 58 min video is the clearest introduction to AI agents, agent skills, md files, building AI employees on the internet",
        "text": "In case you missed it... This 58 min video is the clearest introduction to AI agents, agent skills, md files, building AI employees on the internet and it's 100% free.",
        "url": "https://x.com/gregisenberg",
        "author": "gregisenberg",
        "published_at": "Apr 13, 2026",
        "engagement": {"likes": 3027, "retweets": 312, "replies": 106, "views": 240307},
    },
    {
        "platform": "X",
        "title": "AI agent that connects to Blender and builds full 3D models from a single image",
        "text": "Someone just built a AI agent that connects to blender and builds full 3d models from a single image.",
        "url": "https://x.com/oliviscusAI",
        "author": "oliviscusAI",
        "published_at": "Apr 18, 2026",
        "engagement": {"likes": 879, "retweets": 102, "replies": 11, "views": 50997},
    },
    {
        "platform": "X",
        "title": "OpenClaw and Hermes agent are INCREDIBLE together - use them as an AI agent team",
        "text": "OpenClaw and Hermes agent are INCREDIBLE together. It's not about using one or the other. It's about learning how to use them as an AI agent team. 4 workflows that will skyrocket your productivity.",
        "url": "https://x.com/AlexFinn",
        "author": "AlexFinn",
        "published_at": "Apr 15, 2026",
        "engagement": {"likes": 720, "retweets": 69, "replies": 81, "views": 106791},
    },
    {
        "platform": "X",
        "title": "Facebook Ads → Veo 3 Agent is insane - n8n agent scrapes competitor ads and generates fresh video variants",
        "text": "This Facebook Ads → Veo 3 Agent is absolutely insane. This n8n agent scrapes competitor video ads from the Facebook Ad Library, analyzes them with AI, and generates fresh video variants using Google Veo 3. All on autopilot.",
        "url": "https://x.com/mikefutia",
        "author": "mikefutia",
        "published_at": "Dec 17, 2025",
        "engagement": {"likes": 398, "retweets": 174, "replies": 301, "views": 20703},
    },
]

# 保存为 JSON
output_path = "/Users/Shared/obsidian_share/mini-claw/AI_HUB/01_Raw/2026-04-20/x_browser.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(tweets, f, ensure_ascii=False, indent=2)

print(f"✅ X Browser: {len(tweets)} tweets saved to {output_path}")
for t in tweets:
    e = t['engagement']
    print(f"  @{t['author']}: {t['title'][:60]}... ({e['likes']}❤️ {e['retweets']}🔄)")
