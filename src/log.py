import os
import re

import loguru

from config import LOG_PATH

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

logger = loguru.logger


class SensitiveDataFilter:
    """过滤日志中的敏感信息"""

    PATTERNS = [
        # API Keys
        (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})', r"\1***"),
        # Tokens
        (r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})', r"\1***"),
        # Passwords
        (r'(password["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', r"\1***"),
        # Bearer tokens
        (r"(Bearer\s+)([a-zA-Z0-9_\-\.]+)", r"\1***"),
        # 通用密钥格式 sk-xxx, xoxb-xxx
        (r"(sk-|xoxb-|xoxp-)([a-zA-Z0-9\-]+)", r"\1***"),
    ]

    def __init__(self, level: str = None):
        """
        初始化过滤器

        参数:
            level: 要过滤的日志级别，如果为None则不过滤级别
        """
        self.level = level

    def __call__(self, record):
        """应用敏感数据过滤"""
        # 如果指定了级别，先检查级别
        if self.level and record["level"].name != self.level:
            return False

        # 过滤敏感信息
        message = record["message"]
        for pattern, replacement in self.PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        record["message"] = message
        return True


# 创建过滤器实例（避免每次日志都创建新实例）
info_filter = SensitiveDataFilter(level="INFO")
error_filter = SensitiveDataFilter(level="ERROR")

# 应用过滤器到日志
logger.add(
    os.path.join(LOG_PATH, "info.log"),
    filter=info_filter,
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
)

logger.add(
    os.path.join(LOG_PATH, "error.log"),
    filter=error_filter,
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8",
)
