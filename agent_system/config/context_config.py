"""
上下文管理配置模块 (已废弃)

⚠️ 此文件已废弃，所有配置已合并到 config/settings.py
为了向后兼容，此文件会从 settings 导入并重新导出配置
"""

from config.settings import get_settings

# 向后兼容：导出 settings 实例作为 context_config
# 所有原来使用 context_config.xxx 的代码现在实际使用 settings.xxx
context_config = get_settings()

__all__ = ['context_config']
