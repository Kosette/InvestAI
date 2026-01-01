# InvestAI 安全风险与改进建议分析报告

## 📋 概述
本文档对 InvestAI 项目进行了全面的安全审查和代码质量分析，列出了发现的安全风险和改进建议。

---

## 🔴 高优先级 - 安全风险

### 1. SSL 证书验证被禁用
**位置**: `src/notifiers/senders/slack.py:7`

```python
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
```

**风险等级**: 🔴 高危

**问题描述**: 
- 全局禁用了 SSL 证书验证
- 使所有 HTTPS 连接容易受到中间人攻击(MITM)
- 影响整个应用程序的所有网络请求

**建议修复**:
```python
# 移除全局 SSL 禁用
# 如果遇到证书问题，应该：
# 1. 更新系统证书
# 2. 使用 certifi 包
# 3. 针对特定请求设置，而不是全局禁用
```

**影响范围**: 所有网络通信

---

### 2. 敏感信息泄露风险
**位置**: `.env.example`, `conf/invest_ai.yaml`

**风险等级**: 🟡 中危

**问题描述**:
- API Keys 和 Tokens 通过环境变量注入（这是好的做法）
- 但缺少对环境变量未设置情况的完整处理
- `.env` 文件已在 `.gitignore` 中（好的做法）

**当前保护措施** ✅:
- `.env` 已被 `.gitignore` 忽略
- 环境变量缺失时会抛出异常（`config/loader.py:20`）

**建议改进**:
```python
# 在 config/loader.py 中添加更友好的错误提示
def inject_env_vars(value):
    if isinstance(value, str):
        match = ENV_PATTERN.fullmatch(value)
        if match:
            env_key = match.group(1)
            if env_key not in os.environ:
                # 提供更详细的错误信息
                raise RuntimeError(
                    f"缺少必需的环境变量: {env_key}\n"
                    f"请在 .env 文件中设置此变量，或参考 .env.example"
                )
            return os.environ[env_key]
```

---

### 3. HTTP 服务无认证保护
**位置**: `src/mcp_server.py:106`

```python
mcp.run(transport="http", host="0.0.0.0", port=8888)
```

**风险等级**: 🟡 中危

**问题描述**:
- MCP 服务器监听在 `0.0.0.0:8888`，可从任何网络接口访问
- 没有实现任何认证或授权机制
- 敏感操作（如添加关注列表、分析股票）无需验证

**建议改进**:
1. **添加 API Token 认证**:
```python
# 添加简单的 API Token 验证
@mcp.tool()
async def analyze_stock_tool(code: str, api_token: str = None):
    if api_token != os.getenv("MCP_API_TOKEN"):
        raise ValueError("Invalid API token")
    # ... 原有逻辑
```

2. **限制监听地址**（如果仅本地使用）:
```python
# 仅监听本地
mcp.run(transport="http", host="127.0.0.1", port=8888)
```

3. **使用反向代理** (Nginx/Caddy) 添加认证层

---

### 4. Webhook URL 请求超时设置较短
**位置**: `src/notifiers/senders/webhook.py:20`

```python
resp = requests.post(
    endpoint.url,
    json=payload,
    timeout=5,
)
```

**风险等级**: 🟢 低危

**问题描述**:
- 5秒超时可能对某些慢速网络不够
- 但这实际上是一个好的安全实践，防止挂起

**建议**:
- 保持现有超时设置
- 考虑添加重试机制
```python
# 添加重试逻辑
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
```

---

### 5. 文件路径硬编码，缺少路径验证
**位置**: `src/config/config.py:7-11`, `src/tools/watch_list.py`

```python
LOG_PATH = "./logs"
WATCHLIST_PATH = "./conf/watchlist.json"
INDEX_POOL_PATH = "./conf/index_pool.json"
```

**风险等级**: 🟢 低危

**问题描述**:
- 相对路径可能导致在不同工作目录下运行时找不到文件
- 缺少对用户提供的文件路径的验证（虽然当前代码不接受用户输入的路径）

**建议改进**:
```python
from pathlib import Path

# 使用绝对路径
BASE_DIR = Path(__file__).parent.parent
LOG_PATH = BASE_DIR / "logs"
WATCHLIST_PATH = BASE_DIR / "conf" / "watchlist.json"

# 如果需要接受用户输入的路径，添加验证
def validate_file_path(user_path: str, allowed_dir: Path) -> Path:
    """防止路径遍历攻击"""
    path = Path(user_path).resolve()
    if not path.is_relative_to(allowed_dir):
        raise ValueError("Invalid file path")
    return path
```

---

## 🟡 中优先级 - 代码质量改进

### 6. 异常处理不够细化
**位置**: 多处 try-except 块

**问题**:
- 许多地方使用 `except Exception as e`，捕获过于宽泛
- 某些地方异常后返回空值，可能隐藏问题

**示例**: `src/datacenter/market/stock.py:21-29`
```python
try:
    if period == "daily":
        df = ak.stock_zh_a_daily(symbol=symbol, start_date="20200101", adjust=adjust)
    else:
        raise ValueError(f"Unsupported period: {period}")
    return df
except Exception as e:  # 过于宽泛
    logger.opt(exception=e).error(f"Error fetching Kline: {e}")
    return pd.DataFrame()  # 返回空DataFrame可能掩盖问题
```

**建议改进**:
```python
try:
    if period == "daily":
        df = ak.stock_zh_a_daily(symbol=symbol, start_date="20200101", adjust=adjust)
    else:
        raise ValueError(f"Unsupported period: {period}")
    return df
except ValueError as e:
    # 参数错误，重新抛出
    raise
except requests.RequestException as e:
    # 网络错误
    logger.error(f"Network error fetching Kline for {symbol}: {e}")
    return pd.DataFrame()
except Exception as e:
    # 未预期的错误，记录详细信息
    logger.exception(f"Unexpected error fetching Kline for {symbol}: {e}")
    raise
```

---

### 7. 缺少输入验证
**位置**: `src/mcp_server.py` 各个工具函数

**问题**:
- 股票代码（code）参数缺少格式验证
- 可能导致无效请求或注入风险

**示例**: `src/mcp_server.py:20`
```python
@mcp.tool()
async def analyze_stock_tool(code: str):
    fullcode = get_fullcode(code)
    # 缺少对 code 格式的验证
```

**建议改进**:
```python
import re

def validate_stock_code(code: str) -> bool:
    """验证股票代码格式"""
    # A股股票代码通常是6位数字
    pattern = r'^[0-9]{6}$|^(sh|sz|bj)[0-9]{6}$'
    return bool(re.match(pattern, code.lower()))

@mcp.tool()
async def analyze_stock_tool(code: str):
    """分析特定code的股票"""
    if not validate_stock_code(code):
        raise ValueError(f"Invalid stock code format: {code}")
    
    fullcode = get_fullcode(code)
    # ... 原有逻辑
```

---

### 8. 日志可能包含敏感信息
**位置**: `src/log.py`, 多处 logger 使用

**问题**:
- 日志记录可能包含敏感数据
- 日志文件权限未明确设置

**建议改进**:
```python
# 在 log.py 中添加日志脱敏
import re

class SensitiveDataFilter:
    """过滤日志中的敏感信息"""
    
    PATTERNS = {
        'api_key': (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', r'\1***'),
        'token': (r'(token["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', r'\1***'),
        'password': (r'(password["\']?\s*[:=]\s*["\']?)([^"\'\s]+)', r'\1***'),
    }
    
    def __call__(self, record):
        message = record["message"]
        for pattern, replacement in self.PATTERNS.values():
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        record["message"] = message
        return True

# 应用过滤器
logger.add(
    os.path.join(LOG_PATH, 'info.log'),
    filter=SensitiveDataFilter(),
    # ... 其他配置
)

# 设置日志文件权限（Unix系统）
import os
import stat
log_file = os.path.join(LOG_PATH, 'info.log')
if os.path.exists(log_file):
    os.chmod(log_file, stat.S_IRUSR | stat.S_IWUSR)  # 600
```

---

### 9. Docker 容器以 root 运行
**位置**: `docker/Dockerfile.mcp:3`

```dockerfile
USER root
```

**问题**:
- 容器内以 root 用户运行应用
- 如果容器被攻破，攻击者将拥有 root 权限

**建议改进**:
```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./src /app
COPY pyproject.toml uv.lock /app/
COPY docker/run_mcp.sh /app/run_mcp.sh
RUN chmod +x /app/run_mcp.sh

ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN uv sync --frozen --no-install-project

# 更改所有权并切换到非 root 用户
RUN chown -R appuser:appuser /app
USER appuser

CMD ["/app/run_mcp.sh"]
```

---

### 10. 缺少依赖版本锁定验证
**位置**: `pyproject.toml`

**当前状态** ✅:
- 使用 `uv.lock` 锁定依赖版本（好的做法）
- 依赖项指定了最低版本

**建议改进**:
- 定期更新依赖以获取安全补丁
- 添加 dependabot 或 renovate bot 自动检查依赖更新
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

---

## 🟢 低优先级 - 最佳实践建议

### 11. 添加速率限制
**位置**: `src/mcp_server.py`

**建议**:
- 为 API 端点添加速率限制，防止滥用
```python
from collections import defaultdict
from datetime import datetime, timedelta
from functools import wraps

class RateLimiter:
    def __init__(self, max_requests=60, window=60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window)
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = datetime.now()
        cutoff = now - self.window
        
        # 清理过期请求
        self.requests[client_id] = [
            req for req in self.requests[client_id] if req > cutoff
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(now)
        return True

limiter = RateLimiter(max_requests=60, window=60)

@mcp.tool()
async def analyze_stock_tool(code: str, client_id: str = "default"):
    if not limiter.is_allowed(client_id):
        raise ValueError("Rate limit exceeded")
    # ... 原有逻辑
```

---

### 12. 配置文件数据验证增强
**位置**: `src/config/strategy.py`

**建议**:
- 使用 Pydantic 验证器添加更多业务逻辑验证
```python
from pydantic import field_validator

class StrategyConfig(BaseModel):
    # ... 现有字段
    
    @field_validator('market_rsi_min')
    def validate_rsi_range(cls, v, info):
        if not 0 <= v <= 100:
            raise ValueError('RSI must be between 0 and 100')
        return v
    
    @field_validator('market_rsi_max')
    def validate_rsi_max(cls, v, info):
        if 'market_rsi_min' in info.data and v <= info.data['market_rsi_min']:
            raise ValueError('RSI max must be greater than min')
        return v
```

---

### 13. 添加健康检查端点
**位置**: `src/mcp_server.py`

**建议**:
```python
@mcp.tool()
async def health_check():
    """健康检查端点，用于监控和负载均衡"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.1.0"
    }
```

---

### 14. 改进错误消息，避免信息泄露
**位置**: 多处异常处理

**当前问题**:
- 某些错误消息可能泄露内部实现细节

**建议**:
```python
# 区分开发和生产环境的错误消息
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

def format_error(error: Exception) -> str:
    if DEBUG:
        return f"Error: {str(error)}\n{traceback.format_exc()}"
    else:
        return "An internal error occurred. Please contact support."
```

---

### 15. 添加请求/响应日志记录
**位置**: `src/mcp_server.py`

**建议**:
```python
from functools import wraps
import time

def log_api_call(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"API call started: {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"API call completed: {func.__name__} ({elapsed:.2f}s)")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"API call failed: {func.__name__} ({elapsed:.2f}s) - {e}")
            raise
    return wrapper

@mcp.tool()
@log_api_call
async def analyze_stock_tool(code: str):
    # ... 原有逻辑
```

---

### 16. 数据备份机制
**位置**: `conf/` 目录

**建议**:
```python
# 添加配置文件备份
import shutil
from datetime import datetime

def backup_config_file(filepath: str):
    """备份配置文件"""
    backup_dir = Path("./conf/backups")
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = Path(filepath).name
    backup_path = backup_dir / f"{filename}.{timestamp}.bak"
    
    shutil.copy2(filepath, backup_path)
    
    # 保留最近10个备份
    backups = sorted(backup_dir.glob(f"{filename}.*.bak"))
    for old_backup in backups[:-10]:
        old_backup.unlink()

# 在修改配置前调用
def add_to_watchlist(filepath, item):
    backup_config_file(filepath)  # 先备份
    # ... 原有逻辑
```

---

## 📊 安全评分总结

| 类别 | 评分 | 说明 |
|------|------|------|
| **认证与授权** | 🟡 60/100 | MCP服务缺少认证，但环境变量管理较好 |
| **数据保护** | 🟡 70/100 | 环境变量使用正确，但SSL验证被禁用 |
| **输入验证** | 🟡 65/100 | 基本验证存在，但可以更严格 |
| **错误处理** | 🟡 70/100 | 有异常处理，但可以更细化 |
| **日志记录** | 🟢 75/100 | 使用loguru，但需要添加敏感信息过滤 |
| **依赖管理** | 🟢 85/100 | 使用uv锁定依赖，版本控制良好 |
| **容器安全** | 🟡 65/100 | 使用Docker，但以root运行 |
| **代码质量** | 🟢 80/100 | 结构清晰，使用类型提示和Pydantic |

**总体评分**: 🟡 **71/100** (中等偏上)

---

## 🎯 优先修复建议（按优先级排序）

### 立即修复（第一优先级）
1. ✅ **移除 SSL 证书验证禁用** - 安全风险最高
2. ✅ **为 MCP 服务添加认证** - 防止未授权访问

### 短期修复（1-2周内）
3. ✅ **添加输入验证** - 防止无效数据和潜在注入
4. ✅ **改进异常处理** - 更精确的错误处理
5. ✅ **Docker 容器使用非 root 用户** - 提高容器安全性

### 中期改进（1个月内）
6. ✅ **添加日志脱敏** - 防止敏感信息泄露
7. ✅ **添加速率限制** - 防止API滥用
8. ✅ **配置文件备份机制** - 防止数据丢失

### 长期优化
9. ✅ 定期依赖更新流程
10. ✅ 添加自动化安全扫描
11. ✅ 完善监控和告警

---

## 📝 额外建议

### 1. 添加安全相关的文档
创建 `SECURITY.md` 文件，说明：
- 如何报告安全漏洞
- 安全最佳实践
- 部署安全检查清单

### 2. 代码审计建议
- 使用 `bandit` 进行 Python 安全扫描
- 使用 `safety` 检查依赖漏洞
- 使用 `semgrep` 进行静态代码分析

```bash
# 安装安全工具
pip install bandit safety semgrep

# 运行安全扫描
bandit -r src/
safety check
semgrep --config=auto src/
```

### 3. 环境隔离
- 开发、测试、生产环境分离
- 使用不同的 API Keys
- 使用不同的数据库/配置

### 4. 监控和告警
- 添加异常行为监控
- API 调用频率监控
- 错误率告警

---

## ✅ 正面特性（做得好的地方）

1. ✅ **环境变量管理** - 使用 `.env` 和环境变量注入，未将敏感信息硬编码
2. ✅ **依赖锁定** - 使用 `uv.lock` 确保可重现的构建
3. ✅ **类型提示** - 广泛使用 Python 类型提示，提高代码可维护性
4. ✅ **Pydantic 验证** - 使用 Pydantic 进行配置验证
5. ✅ **Docker 化** - 应用已容器化，便于部署
6. ✅ **结构清晰** - 代码组织良好，模块化设计
7. ✅ **日志记录** - 使用 loguru 进行结构化日志记录
8. ✅ **请求超时** - Webhook 请求设置了超时，防止挂起

---

## 📚 参考资源

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**生成时间**: 2026-01-01  
**审查范围**: 全部源代码、配置文件、Docker配置  
**分析工具**: 手动代码审查 + 静态分析
