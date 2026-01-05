# Nginx 集成配置指南

本文档说明如何配置 Nginx 作为反向代理，与 InvestAI MCP 服务集成，实现HTTPS和认证。

## 架构说明

```
客户端 --> Nginx (HTTPS + 认证) --> InvestAI MCP 服务 (HTTP)
```

- **Nginx**: 处理 HTTPS、SSL 证书、请求转发
- **InvestAI**: 提供 HTTP 服务，验证来自 Nginx 的请求头中的 token

## 认证流程

### 1. HTTP 请求头格式

MCP 服务支持两种认证方式：

**方式一：Authorization Bearer Token**
```http
Authorization: Bearer your-secret-token-here
```

**方式二：X-API-Key**
```http
X-API-Key: your-secret-token-here
```

### 2. Token 提取逻辑

服务端 (`src/mcp_server.py`) 会按以下顺序查找 token：

```python
# 1. 首先尝试从 Authorization header 获取 Bearer token
Authorization: Bearer <token>

# 2. 如果没有找到，尝试从 X-API-Key header 获取
X-API-Key: <token>
```

Token 与环境变量 `MCP_API_TOKEN` 进行比对验证。

## Nginx 配置示例

### 基础配置（HTTPS反向代理）

```nginx
upstream investai_mcp {
    server 127.0.0.1:8888;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL 证书配置
    ssl_certificate /etc/nginx/ssl/yourdomain.crt;
    ssl_certificate_key /etc/nginx/ssl/yourdomain.key;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 日志配置
    access_log /var/log/nginx/investai_access.log;
    error_log /var/log/nginx/investai_error.log;

    # MCP 服务代理
    location /mcp {
        proxy_pass http://investai_mcp;
        
        # 传递原始请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 传递认证头到后端服务
        proxy_pass_header Authorization;
        proxy_pass_header X-API-Key;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 健康检查端点（无需认证）
    location /health {
        proxy_pass http://investai_mcp;
        access_log off;
    }
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

### 高级配置：Nginx 层面的 API Key 验证（可选）

如果想在 Nginx 层面进行初步验证：

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL 配置（同上）...

    # API Key 验证（可选）
    location /mcp {
        # 检查请求头中是否包含有效的 API Key
        set $api_key_valid 0;
        
        # 从 Authorization 或 X-API-Key 获取 token
        if ($http_authorization ~* "^Bearer\s+(.+)$") {
            set $token $1;
        }
        if ($http_x_api_key != "") {
            set $token $http_x_api_key;
        }
        
        # 验证 token（简单示例，生产环境建议使用 Lua 或 auth_request）
        # 注意：这里只做示例，实际验证由后端 MCP 服务完成
        
        proxy_pass http://investai_mcp;
        
        # 传递请求头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 传递认证头
        proxy_pass_header Authorization;
        proxy_pass_header X-API-Key;
    }
}
```

### 使用 auth_request 模块进行高级认证（推荐生产环境）

```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL 配置（同上）...

    # 认证子请求端点（内部使用）
    location = /auth {
        internal;
        proxy_pass http://investai_mcp/validate_token;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Original-URI $request_uri;
        proxy_pass_header Authorization;
        proxy_pass_header X-API-Key;
    }

    location /mcp {
        # 使用子请求进行认证
        auth_request /auth;
        
        # 认证失败时的错误处理
        error_page 401 = @error401;
        
        proxy_pass http://investai_mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 传递认证头
        proxy_pass_header Authorization;
        proxy_pass_header X-API-Key;
    }
    
    location @error401 {
        return 401 '{"error": "Unauthorized", "message": "Invalid or missing API token"}';
        add_header Content-Type application/json;
    }
}
```

## 环境变量配置

在 `.env` 文件中设置 MCP API Token：

```env
# MCP 服务认证 Token
MCP_API_TOKEN=your-very-secret-token-at-least-32-characters-long
```

**安全建议**：
- Token 至少 32 字符
- 使用随机生成的强密码
- 定期更换 Token
- 不要在代码或日志中硬编码

生成安全 Token 的方法：

```bash
# 方法1：使用 openssl
openssl rand -base64 32

# 方法2：使用 Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# 方法3：使用 uuidgen
uuidgen | tr -d '-'
```

## 客户端调用示例

### 使用 curl

**方式一：Bearer Token**
```bash
curl -X POST https://api.yourdomain.com/mcp \
  -H "Authorization: Bearer your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "analyze_stock_tool",
    "params": {
      "code": "000001"
    },
    "id": 1
  }'
```

**方式二：X-API-Key**
```bash
curl -X POST https://api.yourdomain.com/mcp \
  -H "X-API-Key: your-secret-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_watchlist_tool",
    "params": {},
    "id": 1
  }'
```

### 使用 Python requests

```python
import requests

# 配置
API_URL = "https://api.yourdomain.com/mcp"
API_TOKEN = "your-secret-token-here"

# 方式一：Bearer Token
headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# 方式二：X-API-Key
# headers = {
#     "X-API-Key": API_TOKEN,
#     "Content-Type": "application/json"
# }

# 调用示例
payload = {
    "jsonrpc": "2.0",
    "method": "analyze_stock_tool",
    "params": {
        "code": "600519"
    },
    "id": 1
}

response = requests.post(API_URL, json=payload, headers=headers)
print(response.json())
```

### 使用 JavaScript (fetch)

```javascript
const API_URL = 'https://api.yourdomain.com/mcp';
const API_TOKEN = 'your-secret-token-here';

// 方式一：Bearer Token
const response = await fetch(API_URL, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    jsonrpc: '2.0',
    method: 'get_watchlist_tool',
    params: {},
    id: 1
  })
});

const result = await response.json();
console.log(result);
```

## Cherry Studio MCP 配置

在 Cherry Studio 中配置 InvestAI MCP 服务：

1. 打开 **设置 → MCP → 添加**
2. 填写信息：
   - **名称**: InvestAI
   - **类型**: 可流式传输的 HTTP
   - **URL**: `https://api.yourdomain.com/mcp`
   - **请求头**:
     ```
     Content-Type=application/json
     Accept=application/json, text/event-stream
     Authorization=Bearer your-secret-token-here
     ```
     
   或者使用 X-API-Key：
     ```
     Content-Type=application/json
     Accept=application/json, text/event-stream
     X-API-Key=your-secret-token-here
     ```

## 测试验证

### 1. 测试 MCP 服务健康状态

```bash
# 不需要认证的健康检查
curl https://api.yourdomain.com/health
# 预期返回: OK
```

### 2. 测试认证成功

```bash
# 使用正确的 token
curl -X POST https://api.yourdomain.com/mcp \
  -H "Authorization: Bearer correct-token" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"health_check","params":{},"id":1}'

# 预期返回: {"jsonrpc":"2.0","result":"OK","id":1}
```

### 3. 测试认证失败

```bash
# 使用错误的 token
curl -X POST https://api.yourdomain.com/mcp \
  -H "Authorization: Bearer wrong-token" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"get_watchlist_tool","params":{},"id":1}'

# 预期返回: 错误信息
```

### 4. 测试不带 token（向后兼容模式）

```bash
# 如果 MCP_API_TOKEN 未设置，应该可以正常访问（仅记录警告）
curl -X POST https://api.yourdomain.com/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"health_check","params":{},"id":1}'
```

## 故障排查

### 问题1：401 Unauthorized

**可能原因**：
- Token 不正确
- 请求头格式错误
- MCP_API_TOKEN 环境变量未设置或值不匹配

**解决方法**：
```bash
# 检查环境变量
docker exec invest-mcp env | grep MCP_API_TOKEN

# 检查日志
docker logs invest-mcp | grep -i "auth"

# 测试不同的 header 格式
curl -v -H "Authorization: Bearer your-token" ...
curl -v -H "X-API-Key: your-token" ...
```

### 问题2：Nginx 未传递认证头

**检查 Nginx 配置**：
```nginx
# 确保有这两行
proxy_pass_header Authorization;
proxy_pass_header X-API-Key;
```

**重新加载 Nginx**：
```bash
sudo nginx -t
sudo nginx -s reload
```

### 问题3：CORS 错误（跨域请求）

**Nginx 添加 CORS 支持**：
```nginx
location /mcp {
    # CORS 配置
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Authorization, X-API-Key, Content-Type' always;
    
    # 处理 OPTIONS 预检请求
    if ($request_method = 'OPTIONS') {
        return 204;
    }
    
    # 代理配置...
    proxy_pass http://investai_mcp;
}
```

## 安全最佳实践

### 1. 使用强密码

```bash
# 生成 32 字节随机 token
openssl rand -base64 32
```

### 2. 限制访问来源

```nginx
# 仅允许特定 IP 访问
location /mcp {
    allow 192.168.1.0/24;
    allow 10.0.0.0/8;
    deny all;
    
    proxy_pass http://investai_mcp;
}
```

### 3. 速率限制

```nginx
# 定义速率限制区域
limit_req_zone $binary_remote_addr zone=mcp_limit:10m rate=10r/s;

server {
    location /mcp {
        # 应用速率限制：每秒最多10个请求，允许突发20个
        limit_req zone=mcp_limit burst=20 nodelay;
        
        proxy_pass http://investai_mcp;
    }
}
```

### 4. 启用访问日志

```nginx
# 自定义日志格式，记录认证信息
log_format mcp_log '$remote_addr - $remote_user [$time_local] '
                   '"$request" $status $body_bytes_sent '
                   '"$http_authorization" "$http_x_api_key"';

server {
    access_log /var/log/nginx/mcp_access.log mcp_log;
}
```

### 5. 定期更换 Token

建议每 90 天更换一次 API Token：

```bash
# 1. 生成新 token
NEW_TOKEN=$(openssl rand -base64 32)

# 2. 更新 .env 文件
echo "MCP_API_TOKEN=$NEW_TOKEN" >> .env

# 3. 重启容器
docker-compose restart invest-mcp

# 4. 更新客户端配置
```

## 监控和告警

### Nginx 状态监控

```nginx
# 启用状态页面（仅内网访问）
location /nginx_status {
    stub_status on;
    access_log off;
    allow 127.0.0.1;
    deny all;
}
```

### 告警配置示例（使用 Prometheus）

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'nginx'
    static_configs:
      - targets: ['localhost:9113']  # nginx-exporter

# 告警规则
groups:
  - name: mcp_alerts
    rules:
      - alert: HighAuthFailureRate
        expr: rate(nginx_http_requests_total{status="401"}[5m]) > 10
        annotations:
          summary: "MCP 认证失败率过高"
```

---

**更新时间**: 2026-01-05  
**适用版本**: InvestAI v0.1.0+
