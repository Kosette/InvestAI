# 安全改进说明

本文档说明了已实施的安全改进措施。

## 1. SSL/TLS 处理

### 变更内容
- ✅ 移除了 `src/notifiers/senders/slack.py` 中的全局 SSL 证书验证禁用代码
- ✅ 恢复标准的 SSL 证书验证流程

### 部署说明
- HTTP 服务由应用提供
- HTTPS 证书验证由前端 Nginx 代理处理
- 应用与外部服务的通信使用标准 SSL 验证

---

## 2. MCP 服务认证

### 变更内容
- ✅ 添加基于 Token 的简单认证机制
- ✅ 通过环境变量 `MCP_API_TOKEN` 配置认证令牌
- ✅ 所有 MCP 工具添加 `@require_auth` 装饰器

### 配置方法

在 `.env` 文件中添加：

```env
MCP_API_TOKEN=your-secret-token-here
```

### 使用说明

**向后兼容**：
- 如果未设置 `MCP_API_TOKEN`，系统会记录警告但不拦截请求
- 建议生产环境设置强密码作为 token

**HTTP 请求头认证**：

MCP 服务从 HTTP 请求头中提取 token，支持两种格式：

```http
# 方式一：Authorization Bearer Token
Authorization: Bearer your-secret-token-here

# 方式二：X-API-Key
X-API-Key: your-secret-token-here
```

**API 调用示例**：

使用 curl：
```bash
curl -X POST http://localhost:8888/mcp \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"analyze_stock_tool","params":{"code":"000001"},"id":1}'
```

使用 Python：
```python
import requests

headers = {
    "Authorization": "Bearer your-secret-token-here",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8888/mcp",
    json={"jsonrpc":"2.0","method":"get_watchlist_tool","params":{},"id":1},
    headers=headers
)
```

**Cherry Studio 配置**：

在 Cherry Studio 的 MCP 配置中添加请求头：
```
Authorization=Bearer your-secret-token-here
```

或使用：
```
X-API-Key=your-secret-token-here
```

**Nginx 集成**：

详细的 Nginx 配置和集成说明请查看 `NGINX_INTEGRATION.md` 文档。

---

## 3. 输入验证

### 变更内容
- ✅ 添加 `validate_stock_code()` 函数验证股票代码格式
- ✅ 所有接受股票代码的工具添加输入验证
- ✅ 详细的错误提示信息

### 支持的股票代码格式

```python
# 有效格式
"000001"      # 6位数字
"600519"      # 6位数字  
"300750"      # 6位数字
"sh000001"    # 带前缀
"sz600519"    # 带前缀
"SH000001"    # 大写前缀（自动转换）

# 无效格式
"12345"       # 少于6位
"1234567"     # 多于6位
"abc123"      # 包含字母
""            # 空字符串
```

### 错误处理示例

```python
# 输入无效代码时的错误响应
"无效的股票代码格式: abc123。请提供6位数字代码或带sh/sz前缀的代码"
```

---

## 4. 异常处理优化

### 变更内容
- ✅ 细化异常捕获类型，避免过于宽泛的 `except Exception`
- ✅ 使用 `logger.exception()` 记录完整堆栈信息
- ✅ 区分参数错误和运行时错误

### 改进文件
- `src/datacenter/market/stock.py` - 股票数据获取
- `src/agents/llm.py` - LLM 调用
- `src/mcp_server.py` - 所有 MCP 工具

### 示例

**改进前**：
```python
except Exception as e:
    logger.error(f"Error: {e}")
    return None
```

**改进后**：
```python
except ValueError as e:
    logger.error(f"参数错误: {e}")
    raise  # 重新抛出参数错误
except Exception as e:
    logger.exception(f"获取数据失败: {e}")  # 记录完整堆栈
    return pd.DataFrame()
```

---

## 5. 日志脱敏

### 变更内容
- ✅ 实现 `SensitiveDataFilter` 类自动过滤日志中的敏感信息
- ✅ 添加日志文件轮转和保留策略
- ✅ 统一的日志编码（UTF-8）

### 过滤规则

自动过滤以下敏感信息：
- API Keys (`api_key=xxx` → `api_key=***`)
- Tokens (`token: xxx` → `token: ***`)
- Passwords (`password="xxx"` → `password="***"`)
- Bearer Tokens (`Bearer xxx` → `Bearer ***`)
- 特定格式密钥 (`sk-xxx`, `xoxb-xxx` → `sk-***`, `xoxb-***`)

### 日志配置

```python
# 日志轮转：单文件最大 10MB
# 保留期：30 天
# 编码：UTF-8
```

### 示例

**原始日志**：
```
INFO: Connecting with token=xoxb-1234567890-abcdefghij
```

**过滤后**：
```
INFO: Connecting with token=***
```

---

## 6. Docker 容器安全

### 变更内容
- ✅ 创建并使用非 root 用户 `appuser` 运行应用
- ✅ 为 MCP 容器添加健康检查
- ✅ 映射 logs 目录到主机

### Dockerfile 改进

**MCP 容器**：
```dockerfile
# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置文件权限
RUN mkdir -p /app/logs /app/conf && \
    chown -R appuser:appuser /app

# 切换用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8888/ || exit 1
```

**Monitor 容器**：
```dockerfile
# 创建非 root 用户
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 设置文件权限  
RUN mkdir -p /app/logs /app/conf && \
    chown -R appuser:appuser /app

# 切换用户
USER appuser
```

### docker-compose.yml 改进

```yaml
services:
  invest-mcp:
    # ... 其他配置
    volumes:
      - ../conf:/app/conf
      - ../logs:/app/logs  # 日志映射到主机
    
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8888/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

### 健康检查说明

- **检查频率**：每 30 秒
- **超时时间**：10 秒
- **启动宽限期**：5 秒（容器启动时不检查）
- **失败重试**：3 次失败后标记为 unhealthy

---

## 7. 新增功能

### 批量分析工具

新增 `analyze_watchlist_tool()` 可以批量分析关注列表中的所有股票：

```python
# 用法示例
result = await analyze_watchlist_tool(token="your-token")
# 返回所有股票的分析结果
```

### 健康检查端点

新增 `health_check()` 端点用于容器健康检查：

```python
# 用法示例
result = await health_check()
# 返回: "OK"
```

---

## 部署检查清单

在部署到生产环境前，请确认：

- [ ] 已设置 `MCP_API_TOKEN` 环境变量
- [ ] 所有敏感信息已从代码中移除，使用环境变量
- [ ] 日志目录权限正确（appuser 可写）
- [ ] Docker 容器以非 root 用户运行
- [ ] 健康检查配置正确
- [ ] Nginx 配置了正确的 SSL 证书
- [ ] 定期检查并更新依赖版本

---

## 测试验证

### 验证输入验证

```bash
cd src
python -c "
from utils.stock import validate_stock_code
print(validate_stock_code('000001'))  # True
print(validate_stock_code('abc123'))  # False
"
```

### 验证日志脱敏

```bash
cd src
python -c "
from log import SensitiveDataFilter
import re
filter = SensitiveDataFilter()

class Record:
    def __init__(self, msg):
        self.message = msg

record = Record('api_key=sk-123456789012345678901234567890')
filter(record)
print(record.message)  # 应显示: api_key=***
"
```

### 验证容器健康检查

```bash
# 启动容器后
docker ps
# 查看 STATUS 列是否显示 (healthy)

# 手动测试健康检查
curl http://localhost:8888/
```

---

## 故障排查

### MCP 认证失败

**问题**：调用工具时提示"认证失败"

**解决**：
1. 检查 `.env` 文件中是否设置了 `MCP_API_TOKEN`
2. 确认传递的 token 参数值与环境变量一致
3. 检查日志文件 `logs/error.log`

### 容器健康检查失败

**问题**：`docker ps` 显示容器状态为 `(unhealthy)`

**解决**：
1. 检查容器日志：`docker logs invest-mcp`
2. 确认端口 8888 正常监听：`docker exec invest-mcp netstat -tulpn`
3. 手动测试健康检查：`docker exec invest-mcp curl http://localhost:8888/`

### 日志文件权限错误

**问题**：容器启动后无法写入日志

**解决**：
1. 确认主机上 `logs` 目录权限：`ls -la logs/`
2. 如需要，调整权限：`chmod 777 logs/`（开发环境）
3. 生产环境建议使用具体的用户ID映射

---

## 安全建议

1. **定期更新密钥**：定期更换 `MCP_API_TOKEN`
2. **监控日志**：定期检查 `logs/error.log` 发现异常
3. **限制访问**：使用防火墙限制 8888 端口仅允许授权IP访问
4. **备份配置**：定期备份 `conf/` 目录
5. **更新依赖**：定期运行 `uv lock --upgrade` 更新依赖

---

**生成时间**：2026-01-01  
**版本**：1.0
