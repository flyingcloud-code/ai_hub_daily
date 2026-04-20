# AI_HUB Daily

🤖 AI 内容聚合与日报生成系统

## 功能

- 多平台内容抓取 (Reddit, X/Twitter, HackerNews, GitHub, Zhihu)
- 智能质量过滤与评分 (0-100)
- 自动分类与去重
- 趋势对比与洞察生成
- Telegram 日报推送

## 项目状态

| 模块 | 状态 | 说明 |
|------|------|------|
| Reddit fetcher | ✅ 可用 | 原生 API + autocli 双模式 |
| X/Twitter fetcher | ⚠️ 部分 | 需 X_BEARER_TOKEN 或 autocli |
| HackerNews fetcher | ✅ 可用 | 官方 API |
| GitHub fetcher | ⚠️ 部分 | 需 GitHub Token (高频率) |
| Zhihu fetcher | 🚧 未实现 | 需要登录态 |
| Processor | ✅ 完整 | 评分、分类、去重 |
| Reporter | ✅ 完整 | Telegram 格式 |

## 安装

### 基础依赖

```bash
pip install -r requirements.txt
```

### 可选: autocli (推荐)

autocli 提供更稳定的社交内容抓取，支持已登录账号的个性化内容。

```bash
# 安装
npm install -g @flyingcloud/autocli
# 或
pip install autocli

# 文档: https://github.com/flyingcloud-code/autocli
```

### 可选: API Tokens

```bash
# X/Twitter (免费层 100 req/15min)
export X_BEARER_TOKEN="your_token"

# GitHub (提高速率限制)
export GITHUB_TOKEN="your_token"

# LLM 摘要 (可选)
export OPENAI_API_KEY="your_key"
```

## 使用模式

### 模式 A: 原生 API (无需 autocli)

```bash
# 使用 Reddit/HN 公开 API
python main.py fetch --mode native
```

**限制**:
- Reddit: 无搜索，只能抓取特定 subreddit hot
- X: 需要 Bearer Token
- GitHub: 速率限制严格 (60 req/hour)

### 模式 B: autocli (推荐)

```bash
# 先登录各平台
autocli social reddit login
autocli social x login --browser

# 然后运行
python main.py fetch --mode autocli
```

**优势**:
- 支持搜索功能
- 访问个性化内容
- 更高稳定性

### 完整工作流

```bash
# 方式 1: 脚本
bash scripts/workflow.sh

# 方式 2: Python CLI
python main.py all --mode native      # 原生 API
python main.py all --mode autocli     # autocli

# 方式 3: 分步
python main.py fetch --mode native
python main.py process
python main.py report
```

### 定时任务

```cron
0 8 * * * cd /path/to/ai_hub_daily && bash scripts/workflow.sh
```

## 配置

### 质量阈值 (config/thresholds.yaml)

```yaml
reddit:
  score: 10
  comments: 5

hackernews:
  points: 20
  comments: 5

x:
  likes: 20
  retweets: 5
```

### 环境变量覆盖

```bash
export QUALITY_THRESHOLD_REDDIT_SCORE=20
export QUALITY_THRESHOLD_REDDIT_COMMENTS=10
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
⚪ X: 12 条
🟠 HN: 15 条

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
| AI_LLM | llm, gpt, claude, transformer, fine-tune, reasoning |
| AI_Products | product, launch, tool, platform, api |
| AI_Research | paper, research, arxiv, benchmark |
| AI_Ethics | ethic, safety, bias, privacy, regulation, job |
| AI_Business | startup, funding, revenue, market, investment |
| AI_Infra | deployment, gpu, hardware, scaling, apple silicon |
| AI_Skills | tutorial, guide, how to, learn, beginner |
| Programming | code, github, framework, library, open source |

## 依赖说明

### 必需
- Python 3.9+
- requests
- pyyaml

### 可选但推荐
- [autocli](https://github.com/flyingcloud-code/autocli) - 社交内容抓取
- OpenAI API Key - LLM 摘要生成

### 平台特定
- X_BEARER_TOKEN - X/Twitter API 访问
- GITHUB_TOKEN - GitHub API 速率提升

## 已知限制

1. **Reddit**: 原生模式只能抓 subreddit hot，搜索需要 OAuth
2. **X**: 免费 API 层限制 100 req/15min
3. **GitHub**: 无 Token 时 60 req/hour
4. **Zhihu**: 未实现（需要登录态）

## 许可证

MIT
