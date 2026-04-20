"""
AI_HUB Daily - Configuration Manager
"""

import os
import yaml
from pathlib import Path

# 默认配置
DEFAULT_THRESHOLDS = {
    "reddit": {"score": 10, "comments": 5},
    "hackernews": {"points": 20, "comments": 5},
    "github": {"stars": 50, "is_new": True},
    "x": {"likes": 20, "retweets": 5},
    "zhihu": {"votes": 10, "answers": 3}
}

DEFAULT_CATEGORIES = {
    "AI_Agents": ["agent", "autonomous", "workflow", "orchestration", "crewai", "langgraph", "autogen"],
    "AI_LLM": ["llm", "large language model", "gpt", "claude", "gemini", "transformer", "fine-tune"],
    "AI_Products": ["product", "launch", "release", "tool", "platform", "api"],
    "AI_Research": ["paper", "research", "study", "arxiv", "benchmark", "evaluation"],
    "AI_Ethics": ["ethic", "safety", "alignment", "bias", "privacy", "regulation", "job", "replace"],
    "AI_Business": ["startup", "funding", "revenue", "business", "market", "invest"],
    "AI_Infra": ["infrastructure", "deployment", "scaling", "gpu", "hardware", "mps", "cuda"],
    "AI_Skills": ["tutorial", "guide", "how to", "learn", "course", "beginner", "getting started"],
    "Programming": ["code", "github", "repository", "framework", "library", "sdk"],
}

class Config:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or Path(__file__).parent.parent.parent / "config" / "thresholds.yaml"
        self.thresholds = self._load_thresholds()
        self.categories = self._load_categories()
    
    def _load_thresholds(self) -> dict:
        """加载阈值配置（环境变量优先）"""
        thresholds = DEFAULT_THRESHOLDS.copy()
        
        # 从文件加载
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'thresholds' in data:
                        thresholds.update(data['thresholds'])
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}")
        
        # 环境变量覆盖
        for platform in thresholds:
            for key in thresholds[platform]:
                env_key = f"QUALITY_THRESHOLD_{platform.upper()}_{key.upper()}"
                if env_key in os.environ:
                    try:
                        val = os.environ[env_key]
                        thresholds[platform][key] = int(val) if val.isdigit() else val
                    except:
                        pass
        
        return thresholds
    
    def _load_categories(self) -> dict:
        """加载分类配置"""
        categories = DEFAULT_CATEGORIES.copy()
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'categories' in data:
                        categories.update(data['categories'])
            except Exception as e:
                print(f"Warning: Failed to load categories: {e}")
        
        return categories
    
    def get_threshold(self, platform: str) -> dict:
        """获取平台阈值"""
        return self.thresholds.get(platform.lower(), {})
    
    def get_categories(self) -> dict:
        """获取所有分类"""
        return self.categories

# 全局配置实例
config = Config()
