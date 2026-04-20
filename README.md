# AI_HUB Daily

🤖 AI 内容聚合与日报生成系统

## 功能

- 多平台内容抓取 (Reddit, X/Twitter, HackerNews, GitHub, Zhihu)
- 智能质量过滤与评分 (0-100)
- 自动分类与去重
- 趋势对比与洞察生成
- Telegram 日报推送

## 项目结构

```
ai_hub_daily/
├── src/
│   ├── fetcher/          # 内容抓取模块
│   │   ├── __init__.py
│   │   ├── reddit.py     # Reddit 搜索
│   │   ├── x.py          # X/Twitter
│   │   ├── hackernews.py # HackerNews
│   │   ├── github.py     # GitHub Trending
│   │   └── zhihu.py      # 知乎
│   ├── processor/        # 内容处理模块
│   │   ├── __init__.py
│   │   ├── classifier.py # 智能分类
│   │   ├── scorer.py     # 质量评分
│   │   └── dedup.py      # 去重
│   ├── reporter/         # 报告生成模块
│   │   ├── __init__.py
│   │   └── telegram.py   # Telegram 格式
│   └── utils/
│       ├── __init__.py
│       └── config.py     # 配置管理
├── scripts/
│   └── workflow.sh       # 主工作流
├── config/
│   └── thresholds.yaml   # 质量阈值配置
├── requirements.txt
├── README.md
└── LICENSE
```

## 安装

```bash
pip install -r requirements.txt
```

## 依赖工具

- [autocli](https://github.com/yourusername/autocli) - 多平台 CLI 工具
- Python 3.9+

## 配置

### 环境变量

```bash
# 可选: 启用 LLM 摘要
export OPENAI_API_KEY="your-key"

# 可选: 自定义质量阈值
export QUALITY_THRESHOLD_REDDIT_SCORE=10
export QUALITY_THRESHOLD_REDDIT_COMMENTS=5
```

### 质量阈值

| 平台 | 默认阈值 |
|------|----------|
| Reddit | score ≥ 10 或 comments ≥ 5 |
| HackerNews | points ≥ 20 或 comments ≥ 5 |
| GitHub | stars ≥ 50 |
| X/Twitter | likes ≥ 20 或 retweets ≥ 5 |
| Zhihu | votes ≥ 10 或 answers ≥ 3 |

## 使用

### 手动运行

```bash
# 完整工作流
bash scripts/workflow.sh

# 单独模块
python -m src.fetcher.reddit
python -m src.processor.classifier
python -m src.reporter.telegram
```

### 定时任务

```cron
0 8 * * * cd /path/to/ai_hub_daily && bash scripts/workflow.sh
```

## 输出格式

### 处理后的数据

```json
{
  "id": "a1b2c3d4e5f6",
  "platform": "Reddit",
  "title": "How I make $300-500/day with an AI agent",
  "url": "https://reddit.com/...",
  "author": "username",
  "published_at": "2026-04-20T10:00:00Z",
  "engagement": {
    "score": 0,
    "comments": 354
  },
  "quality_score": 100,
  "categories": ["AI_Agents", "AI_Business"],
  "summary": "Mac Mini 跑 AI Agent 自动找客户建站..."
}
```

### Telegram 报告

```
📊 AI_HUB 日报 V2 - 2026-04-20

🎯 今日总览
总条目: 73 | 高质量: 27 | 环比: +15

📈 平台分布
🔴 Reddit: 73 条

🏷️ 热门分类
• AI_Skills: 23 条
• AI_Agents: 17 条

💡 今日洞察
🔥 AI_Skills 是今日绝对热点
⭐ 发现 25 条高质量内容
🆕 新趋势: reasoning, local llm

🔥 精选内容 TOP 5
1. [Reddit] How I make $300-500/day with an AI agent...
   🔼0 💬354 | 质量: 100 | AI_Agents
```

## 分类体系

| 分类 | 关键词 |
|------|--------|
| AI_Agents | agent, autonomous, workflow, langgraph, crewai |
| AI_LLM | llm, gpt, claude, transformer, fine-tune |
| AI_Products | product, launch, tool, platform, api |
| AI_Research | paper, research, arxiv, benchmark |
| AI_Ethics | ethic, safety, bias, privacy, regulation |
| AI_Business | startup, funding, revenue, market |
| AI_Infra | deployment, gpu, hardware, scaling |
| AI_Skills | tutorial, guide, how to, learn |
| Programming | code, github, framework, library |

## 许可证

MIT
