import loguru
from config import LOG_PATH
import os
import re

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

logger = loguru.logger


class SensitiveDataFilter:
    """过滤日志中的敏感信息"""
    
    PATTERNS = [
        # API Keys
        (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})', r'\1***'),
        # Tokens
        (r'(token["\']?\s*[:=]\s*["\']?)([a-zA-Z0-9_\-]{20,})', r'\1***'),
        # Passwords
        (r'(password["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', r'\1***'),
        # Bearer tokens
        (r'(Bearer\s+)([a-zA-Z0-9_\-\.]+)', r'\1***'),
        # 通用密钥格式 sk-xxx, xoxb-xxx
        (r'(sk-|xoxb-|xoxp-)([a-zA-Z0-9\-]+)', r'\1***'),
    ]
    
    def __call__(self, record):
        """应用敏感数据过滤"""
        message = record["message"]
        for pattern, replacement in self.PATTERNS:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        record["message"] = message
        return True


# 应用过滤器到日志
logger.add(
    os.path.join(LOG_PATH, 'info.log'),
    filter=lambda record: record["level"].name == "INFO" and SensitiveDataFilter()(record),
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8"
)

logger.add(
    os.path.join(LOG_PATH, 'error.log'),
    filter=lambda record: record["level"].name == "ERROR" and SensitiveDataFilter()(record),
    rotation="10 MB",
    retention="30 days",
    encoding="utf-8"
)

