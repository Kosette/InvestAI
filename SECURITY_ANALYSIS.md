# InvestAI 安全分析与改进建议

**分析日期**: 2026-01-01  
**版本**: v0.1.0

## 📋 概述

本文档对 InvestAI 项目进行了全面的安全审查，识别了潜在的安全风险和可以改进的地方。所有建议都遵循"最小改动"原则，不过度设计。

---

## 🔴 高优先级安全风险

### 1. SSL 证书验证被禁用 ⚠️

**位置**: `src/notifiers/senders/slack.py:7`

```python
ssl._create_default_https_context = ssl._create_unverified_context
```

**风险等级**: 🔴 高危

**问题描述**: 
- 全局禁用 SSL 证书验证，使应用容易受到中间人攻击 (MITM)
- 攻击者可以拦截和篡改与 Slack API 的通信
- 影响范围：整个 Python 进程的所有 HTTPS 连接

**建议修复**:
```python
# 删除这行代码
# ssl._create_default_https_context = ssl._create_unverified_context

# 如果遇到 SSL 证书问题，应该：
# 1. 更新系统的 CA 证书包
# 2. 或在 slack_sdk 初始化时指定 ssl_context
from slack_sdk import WebClient
client = WebClient(token=channel_config.token)  # 使用默认的 SSL 验证
```

**影响**: 移除这行代码可能导致在某些环境下 SSL 证书验证失败，但这是正确的安全行为。

---

### 2. MCP 服务器暴露在公网 ⚠️

**位置**: `src/mcp_server.py:106`

```python
mcp.run(transport="http", host="0.0.0.0", port=8888)
```

**风险等级**: 🔴 高危

**问题描述**:
- 服务绑定到 `0.0.0.0`，意味着可以从任何网络接口访问
- 没有身份验证机制
- 任何人都可以调用 MCP 工具，包括：
  - 分析股票
  - 修改关注列表
  - 编辑策略配置

**建议修复**:
```python
# 选项 1: 仅绑定到本地 (推荐用于桌面应用)
mcp.run(transport="http", host="127.0.0.1", port=8888)

# 选项 2: 如果需要远程访问，添加认证中间件
# 或使用反向代理 (nginx/caddy) 提供 HTTPS + 基本认证
```

**Docker 配置建议**:
```yaml
# docker/docker-compose.yml
ports:
  - "127.0.0.1:8888:8888"  # 仅绑定到本地
  # 而不是 - "8888:8888"
```

---

### 3. 环境变量缺少验证 ⚠️

**位置**: `src/config/loader.py:11-30`

**风险等级**: 🟡 中危

**问题描述**:
- 环境变量替换时会抛出异常，但没有提供清晰的错误处理
- 如果环境变量未设置，应用会在运行时崩溃
- 敏感配置（API Key）可能意外使用空值或默认值

**建议改进**:
```python
def inject_env_vars(value):
    """
    将 ${VAR_NAME} 替换为环境变量
    """
    if isinstance(value, str):
        match = ENV_PATTERN.fullmatch(value)
        if match:
            env_key = match.group(1)
            if env_key not in os.environ:
                # 改进：提供更清晰的错误信息
                raise RuntimeError(
                    f"Missing required environment variable: {env_key}\n"
                    f"Please set {env_key} in your .env file or environment."
                )
            env_value = os.environ[env_key]
            # 新增：验证敏感环境变量不为空
            if env_key in ["OPENAI_API_KEY", "SLACK_TOKEN"] and not env_value.strip():
                raise ValueError(f"Environment variable {env_key} cannot be empty")
            return env_value
        return value
    # ... rest of the code
```

---

### 4. 日志可能包含敏感信息 ⚠️

**位置**: `src/notifiers/senders/slack.py:14`

**风险等级**: 🟡 中危

**问题描述**:
```python
# logger.debug(f"SlackSender send message: {channel_config.token}, ...")
```

虽然已被注释，但显示了可能记录敏感信息的风险模式。

**建议**:
- 确保日志中不记录 token、API key、密码
- 如果需要调试，只记录 token 的前几位字符

```python
# 安全的日志记录方式
def mask_sensitive(value: str, show_chars: int = 4) -> str:
    """脱敏显示敏感信息"""
    if len(value) <= show_chars:
        return "***"
    return f"{value[:show_chars]}...{value[-show_chars:]}"

logger.debug(f"SlackSender send to channel: {channel_config.default_channel}, "
             f"token: {mask_sensitive(channel_config.token)}")
```

---

## 🟡 中优先级安全建议

### 5. 文件写入缺少原子性保护

**位置**: `src/tools/watch_list.py:9-13`

**风险等级**: 🟡 中危

**问题描述**:
```python
def add_to_watchlist(filepath, item):
    watchlist = load_watchlist(filepath)
    watchlist[item['name']] = item['code']
    with open(filepath, "w") as f:
        json.dump(watchlist, f, ensure_ascii=False, indent=4)
```

如果在写入过程中发生错误（磁盘满、权限问题、进程被杀），会导致文件损坏。

**建议改进**:
```python
import tempfile
import shutil

def add_to_watchlist(filepath, item):
    watchlist = load_watchlist(filepath)
    watchlist[item['name']] = item['code']
    
    # 原子写入：先写临时文件，再重命名
    temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath), text=True)
    try:
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(watchlist, f, ensure_ascii=False, indent=4)
        shutil.move(temp_path, filepath)  # 原子操作
    except:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
```

---

### 6. HTTP 请求缺少超时和重试机制

**位置**: `src/notifiers/senders/webhook.py:17-21`

**风险等级**: 🟡 中危

**问题描述**:
```python
resp = requests.post(
    endpoint.url,
    json=payload,
    timeout=5,
)
```

- 超时设置为 5 秒是好的，但没有重试机制
- 网络临时故障会导致通知丢失

**建议改进**:
```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_session_with_retry():
    """创建带重试机制的 session"""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # 最多重试 3 次
        backoff_factor=1,  # 指数退避
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# 使用方式
session = get_session_with_retry()
resp = session.post(endpoint.url, json=payload, timeout=5)
```

---

### 7. 缺少输入验证

**位置**: `src/mcp_server.py:20-42`

**风险等级**: 🟡 中危

**问题描述**:
- MCP 工具函数没有验证输入参数
- `code` 参数可能被注入恶意数据

**建议改进**:
```python
import re

def validate_stock_code(code: str) -> bool:
    """验证股票代码格式"""
    # A股股票代码：6位数字，或带sh/sz前缀
    pattern = r'^(sh|sz)?[0-9]{6}$'
    return bool(re.match(pattern, code, re.IGNORECASE))

@mcp.tool()
async def analyze_stock_tool(code: str):
    """分析特定code的股票"""
    # 输入验证
    if not code or not isinstance(code, str):
        return "错误：股票代码不能为空"
    
    code = code.strip()
    if not validate_stock_code(code):
        return f"错误：无效的股票代码格式: {code}"
    
    # ... 原有逻辑
```

---

### 8. 异常处理不完整

**位置**: 多处

**风险等级**: 🟢 低危

**问题描述**:
许多地方使用了裸的 `except Exception`，这可能隐藏严重错误。

**示例**: `src/agents/llm.py:8-18`
```python
try:
    response = completion(...)
    return response.choices[0].message.content
except Exception as e:
    logger.opt(exception=e).exception(e)
    return None  # 返回 None 可能导致下游代码崩溃
```

**建议改进**:
```python
from typing import Optional

def get_response_by_llm(message, model_name: str = LLM_CONFIG.base_model) -> Optional[str]:
    try:
        response = completion(
            model=LLM_CONFIG.provider + "/" + model_name,
            messages=[{"content": message, "role": "user"}],
            api_base=LLM_CONFIG.base_url,
            api_key=LLM_CONFIG.api_key,
        )
        return response.choices[0].message.content
    except KeyError as e:
        logger.error(f"LLM response format error: {e}")
        raise  # 重新抛出，让调用者处理
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error calling LLM: {e}")
        raise
    except Exception as e:
        logger.exception(f"Unexpected error calling LLM: {e}")
        raise
```

---

## 🟢 配置和最佳实践建议

### 9. 添加日志目录到 .gitignore

**当前状态**: `logs/` 目录不在 `.gitignore` 中

**建议**:
```bash
# 在 .gitignore 中添加
logs/
*.log
```

---

### 10. Docker 镜像安全加固

**位置**: `docker/Dockerfile.mcp` 和 `docker/Dockerfile.monitor`

**当前问题**:
- 使用 root 用户运行应用
- 没有健康检查

**建议改进**:
```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# 创建非 root 用户
RUN groupadd -r investai && useradd -r -g investai investai

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    libstdc++6 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./src /app
COPY pyproject.toml uv.lock /app/
COPY docker/run_mcp.sh /app/run_mcp.sh
RUN chmod +x /app/run_mcp.sh

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN uv sync --frozen --no-install-project

# 创建必要的目录并设置权限
RUN mkdir -p /app/logs /app/conf && \
    chown -R investai:investai /app

# 切换到非 root 用户
USER investai

# 添加健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8888/health', timeout=2)" || exit 1

CMD ["/app/run_mcp.sh"]
```

同时需要在 `src/mcp_server.py` 添加健康检查端点：
```python
@mcp.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

### 11. 环境变量文档改进

**位置**: `.env.example`

**建议**:
```bash
# .env.example - 添加更详细的说明

# ==================== LLM 配置 ====================
# OpenAI API Key (必需)
# 获取方式：https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-xxxx

# ==================== 通知配置 ====================
# Slack Bot Token (可选，仅在启用 Slack 通知时需要)
# 格式：xoxb-开头
# 获取方式：https://api.slack.com/apps
SLACK_TOKEN=xoxb-xxx

# Email 配置 (可选，仅在启用邮件通知时需要)
EMAIL_USERNAME=xxx@example.com
EMAIL_PASSWORD=your_email_password

# ==================== 安全建议 ====================
# 1. 不要提交 .env 文件到 Git
# 2. 生产环境使用强密码
# 3. 定期轮换 API Key
# 4. 使用环境变量管理工具 (如 AWS Secrets Manager)
```

---

### 12. 添加依赖项安全扫描

**建议**: 在 GitHub Actions 中添加依赖项扫描

创建 `.github/workflows/security.yml`:
```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    # 每周一早上 8 点运行
    - cron: '0 8 * * 1'

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          pip install safety pip-audit
      
      - name: Run safety check
        run: safety check --json
        continue-on-error: true
      
      - name: Run pip-audit
        run: pip-audit
        continue-on-error: true
```

---

### 13. 配置文件权限

**建议**: 在部署文档中添加文件权限设置指南

```bash
# 生产环境部署前，设置适当的文件权限
chmod 600 .env              # 仅所有者可读写
chmod 600 conf/*.json       # 配置文件
chmod 644 conf/*.yaml       # YAML 配置
```

---

### 14. 错误信息泄露防护

**位置**: 全局

**当前问题**: 错误信息可能泄露系统内部信息

**建议**: 区分开发环境和生产环境的错误处理

```python
# config/config.py 添加
class AppConfig(BaseModel):
    debug_mode: bool = False  # 生产环境设为 False

# 在异常处理中使用
if not APP_CONFIG.debug_mode:
    # 生产环境：返回通用错误信息
    return {"error": "An error occurred. Please contact support."}
else:
    # 开发环境：返回详细错误
    return {"error": str(e), "traceback": traceback.format_exc()}
```

---

### 15. 添加速率限制

**位置**: MCP 服务器

**建议**: 为 MCP API 添加速率限制，防止滥用

```python
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/analyze")
@limiter.limit("10/minute")  # 每分钟最多 10 次请求
async def analyze(request: Request, code: str):
    # ... your code
```

---

## 📊 安全检查清单

### 立即修复（高优先级）
- [ ] 移除 SSL 证书验证禁用代码 (`src/notifiers/senders/slack.py`)
- [ ] 修改 MCP 服务器绑定地址为 `127.0.0.1` 或添加认证
- [ ] 添加环境变量验证和清晰的错误提示
- [ ] 确保日志不记录敏感信息（token、密码、API key）

### 推荐修复（中优先级）
- [ ] 实现原子文件写入（watchlist.json）
- [ ] 为 HTTP 请求添加重试机制
- [ ] 添加股票代码输入验证
- [ ] 改进异常处理，避免隐藏错误
- [ ] Docker 容器使用非 root 用户运行

### 最佳实践（低优先级）
- [ ] 添加 `logs/` 到 `.gitignore`
- [ ] 完善 `.env.example` 文档
- [ ] 添加 GitHub Actions 安全扫描
- [ ] 设置适当的配置文件权限
- [ ] 实现生产环境的错误信息脱敏
- [ ] 为 MCP API 添加速率限制

---

## 🔐 安全开发建议

1. **最小权限原则**: 
   - 应用只请求必需的权限
   - Docker 容器使用非 root 用户
   - API 访问限制在最小范围

2. **纵深防御**:
   - 使用 HTTPS
   - 添加认证和授权
   - 输入验证和输出编码
   - 日志审计

3. **定期更新**:
   - 定期更新依赖项
   - 关注安全公告
   - 使用自动化工具扫描漏洞

4. **安全配置**:
   - 敏感信息使用环境变量
   - 配置文件不提交到版本控制
   - 使用强密码和密钥

5. **监控和审计**:
   - 记录安全相关事件
   - 监控异常访问模式
   - 定期安全审计

---

## 📝 总结

InvestAI 项目整体代码质量良好，但存在一些需要注意的安全问题：

**主要风险**:
1. SSL 证书验证被全局禁用（高危）
2. MCP 服务器暴露在公网且无认证（高危）
3. 缺少输入验证和错误处理

**改进建议**:
- 优先修复高危风险项
- 逐步完善中优先级项目
- 采用安全开发最佳实践

**预计工作量**:
- 高优先级修复：2-4 小时
- 中优先级改进：4-8 小时
- 最佳实践完善：8-16 小时

所有建议都遵循"最小改动"原则，不会引入复杂的架构变更。

---

**生成时间**: 2026-01-01  
**审查者**: GitHub Copilot Security Analysis
