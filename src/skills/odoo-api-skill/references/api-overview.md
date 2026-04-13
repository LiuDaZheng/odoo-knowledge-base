# Odoo API 概览

## 支持的协议

### XML-RPC

**特点**:
- 传统协议，广泛支持
- 所有编程语言都有 XML-RPC 库
- 适合后端集成

**端点**:
```
认证：http://<host>:<port>/xmlrpc/2/common
对象：http://<host>:<port>/xmlrpc/2/object
```

### JSON-RPC

**特点**:
- 现代协议，推荐用于 Web
- 轻量级，易于调试
- 适合前端和移动端

**端点**:
```
统一端点：http://<host>:<port>/jsonrpc
```

---

## API 架构

```
┌─────────────────┐
│   外部客户端     │
│  (Python/JS/等) │
└────────┬────────┘
         │ XML-RPC / JSON-RPC
         │
┌────────┴────────┐
│   Odoo 服务器    │
│  ┌─────────────┐│
│  │  认证服务   ││ → 验证用户
│  │  (common)   ││
│  └─────────────┘│
│  ┌─────────────┐│
│  │  对象服务   ││ → CRUD 操作
│  │  (object)   ││
│  └─────────────┘│
│  ┌─────────────┐│
│  │   ORM 层     ││
│  └─────────────┘│
└────────┬────────┘
         │
┌────────┴────────┐
│   PostgreSQL    │
└─────────────────┘
```

---

## 认证流程

```
1. 客户端发送认证请求
   ↓
2. Odoo 验证用户名/密码
   ↓
3. 返回用户 ID (uid)
   ↓
4. 使用 uid 进行后续操作
```

### 认证示例

```python
import xmlrpc.client

url = 'http://localhost:8069'
db = 'mydb'
username = 'admin'
password = 'admin'

# 创建认证代理
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')

# 认证
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"认证成功，用户 ID: {uid}")
else:
    print("认证失败")
```

---

## 可用服务

### Common 服务

| 方法 | 说明 | 示例 |
|------|------|------|
| `authenticate` | 用户认证 | `authenticate(db, user, pass, {})` |
| `check_access_rights` | 检查访问权限 | `check_access_rights(model, operation)` |
| `version` | 获取版本信息 | `version()` |
| `list_lang` | 获取语言列表 | `list_lang()` |
| `list_countries` | 获取国家列表 | `list_countries()` |

### Object 服务

| 方法 | 说明 | 示例 |
|------|------|------|
| `execute` | 执行模型方法 (XML-RPC) | `execute(db, uid, pass, model, method, *args)` |
| `execute_kw` | 执行模型方法 (带 kwargs) | `execute_kw(db, uid, pass, model, method, args, kwargs)` |
| `execute_kw` (JSON-RPC) | JSON-RPC 统一调用 | `call(service, method, args)` |

---

## 域名语法

Odoo 使用**域名**（Domain）进行过滤：

```python
# 基本语法
[('字段名', '操作符', '值')]

# 多个条件 (AND)
[('state', '=', 'draft'), ('amount_total', '>', 1000)]

# OR 条件
['|', ('state', '=', 'draft'), ('state', '=', 'sent')]

# NOT 条件
['!', ('state', '=', 'cancel')]

# 复杂组合
['&', ('state', 'in', ['draft', 'sent']), 
   '|', ('amount_total', '>', 1000), ('partner_id', '=', 1)]
```

### 操作符

| 操作符 | 说明 | 示例 |
|--------|------|------|
| `=` | 等于 | `('state', '=', 'draft')` |
| `!=` | 不等于 | `('state', '!=', 'cancel')` |
| `>` | 大于 | `('amount', '>', 1000)` |
| `>=` | 大于等于 | `('amount', '>=', 1000)` |
| `<` | 小于 | `('amount', '<', 1000)` |
| `<=` | 小于等于 | `('amount', '<=', 1000)` |
| `in` | 在列表中 | `('state', 'in', ['draft', 'sent'])` |
| `not in` | 不在列表中 | `('state', 'not in', ['cancel'])` |
| `like` | 包含 (SQL LIKE) | `('name', 'like', 'SO%')` |
| `ilike` | 包含 (不区分大小写) | `('name', 'ilike', 'so')` |
| `=like` | 精确 LIKE | `('name', '=like', 'SO_')` |
| `=ilike` | 精确 iLIKE | `('name', '=ilike', 'so_')` |
| `child_of` | 子记录 | `('parent_id', 'child_of', [1])` |

---

## 数据格式

### 日期时间

```python
# 日期
'2024-01-15'

# 日期时间 (UTC)
'2024-01-15 10:30:00'

# Python 转换
from datetime import datetime
date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
```

### 货币

```python
# 货币值 (浮点数)
amount = 1000.50

# 读取时自动包含货币字段
data = models.execute_kw(db, uid, password,
    'sale.order', 'read',
    [[1]],
    {'fields': ['amount_total', 'currency_id']}
)
```

### 关系字段

```python
# Many2one (存储 ID)
{'partner_id': 5}

# One2many/Many2many (使用命令)
{'order_line': [(0, 0, {'product_id': 1, 'qty': 1})]}
```

---

## 响应格式

### XML-RPC 响应

```python
# 成功
{
    'result': <返回值>
}

# 错误
xmlrpc.client.Fault: <错误信息>
```

### JSON-RPC 响应

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": <返回值>
}

// 错误
{
    "jsonrpc": "2.0",
    "id": 1,
    "error": {
        "code": -32600,
        "message": "错误信息"
    }
}
```

---

## 限制和配额

### 请求限制

- 默认无请求次数限制
- 可通过 Nginx/Apache 配置限流
- 大数据量建议使用分页

### 数据大小

- 单次请求建议 < 1000 条记录
- 大批量数据使用分批处理
- 文件上传使用 `upload_file` 方法

---

## 安全考虑

### 认证安全

- ✅ 使用 HTTPS
- ✅ 使用 API Key 而非密码
- ✅ 定期轮换凭证
- ❌ 不要在代码中硬编码密码

### 权限控制

- 使用最小权限原则
- 为集成创建专用用户
- 限制访问的模型和字段

### 数据验证

- 验证所有输入
- 使用域名过滤
- 记录审计日志

---

*参考：Odoo 官方 API 文档*
