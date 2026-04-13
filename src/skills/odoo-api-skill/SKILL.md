---
name: odoo-api-skill
description: Odoo API 完整参考，包括 XML-RPC、JSON-RPC 集成方法、认证、CRUD 操作、批量处理、最佳实践。使用本 Skill 当需要与 Odoo 进行外部集成、数据同步、自定义客户端开发或第三方系统对接时。
---

# Odoo API 集成 Skill

## 快速导航

| 主题 | 参考文档 |
|------|----------|
| [API 概览](references/api-overview.md) | 支持的协议和端点 |
| [认证](references/authentication.md) | 认证方法和安全 |
| [XML-RPC](references/xml-rpc.md) | XML-RPC 详细用法 |
| [JSON-RPC](references/json-rpc.md) | JSON-RPC 详细用法 |
| [集成示例](references/integration-examples.md) | Python/JS/PHP/cURL示例 |
| [最佳实践](references/best-practices.md) | 错误处理、性能、安全 |

---

## API 概览

Odoo 提供两种外部 API 协议：

| 协议 | 端点 | 用途 |
|------|------|------|
| **XML-RPC** | `/xmlrpc/2/common`, `/xmlrpc/2/object` | 传统协议，广泛支持 |
| **JSON-RPC** | `/jsonrpc` | 现代协议，推荐用于 Web |

### 服务端点

```
# Odoo 17/18
认证端点：http://<host>:<port>/xmlrpc/2/common
对象端点：http://<host>:<port>/xmlrpc/2/object
JSON 端点：http://<host>:<port>/jsonrpc

# Odoo 16 及更早
认证端点：http://<host>:<port>/xmlrpc/common
对象端点：http://<host>:<port>/xmlrpc/object
```

---

## 快速开始

### 1. 基础连接

```python
import xmlrpc.client

# 连接配置
url = 'http://localhost:8069'
db = 'mydb'
username = 'admin'
password = 'admin'

# 认证
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if uid:
    print(f"认证成功，用户 ID: {uid}")
else:
    print("认证失败")
```

### 2. 读取数据

```python
# 创建对象代理
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 搜索记录
order_ids = models.execute_kw(db, uid, password,
    'sale.order',
    'search',
    [[('state', '=', 'draft')]]
)

# 读取记录
orders = models.execute_kw(db, uid, password,
    'sale.order',
    'read',
    [order_ids],
    {'fields': ['name', 'partner_id', 'amount_total']}
)
```

### 3. 创建数据

```python
# 创建销售订单
order_id = models.execute_kw(db, uid, password,
    'sale.order',
    'create',
    [{
        'partner_id': 1,
        'order_line': [(0, 0, {
            'product_id': 1,
            'product_uom_qty': 1,
            'price_unit': 100.0,
        })],
    }]
)
```

---

## 核心操作

### 搜索 (Search)

```python
# 基础搜索
ids = models.execute_kw(db, uid, password,
    'sale.order', 'search', [[]])

# 带条件搜索
ids = models.execute_kw(db, uid, password,
    'sale.order', 'search',
    [[('state', '=', 'draft'), ('amount_total', '>', 1000)]]
)

# 带排序和限制
ids = models.execute_kw(db, uid, password,
    'sale.order', 'search',
    [[]],
    {'order': 'date_order desc', 'limit': 10}
)
```

### 读取 (Read)

```python
# 读取所有字段
data = models.execute_kw(db, uid, password,
    'sale.order', 'read', [[1]])

# 读取特定字段
data = models.execute_kw(db, uid, password,
    'sale.order', 'read',
    [[1]],
    {'fields': ['name', 'partner_id', 'amount_total']}
)

# 读取关联字段
data = models.execute_kw(db, uid, password,
    'sale.order', 'read',
    [[1]],
    {'fields': ['name', 'partner_id', 'partner_id.name']}
)
```

### 创建 (Create)

```python
# 创建单条记录
record_id = models.execute_kw(db, uid, password,
    'res.partner', 'create',
    [{
        'name': 'New Customer',
        'email': 'customer@example.com',
        'phone': '123456789',
    }]
)

# One2many 记录创建
order_id = models.execute_kw(db, uid, password,
    'sale.order', 'create',
    [{
        'partner_id': 1,
        'order_line': [
            (0, 0, {'product_id': 1, 'qty': 1}),  # 创建
            (0, 0, {'product_id': 2, 'qty': 2}),  # 创建
        ],
    }]
)
```

### 更新 (Write)

```python
# 更新单条记录
models.execute_kw(db, uid, password,
    'sale.order', 'write',
    [[1], {'state': 'confirmed'}]
)

# 批量更新
models.execute_kw(db, uid, password,
    'sale.order', 'write',
    [[1, 2, 3], {'state': 'done'}]
)
```

### 删除 (Unlink)

```python
# 删除记录
models.execute_kw(db, uid, password,
    'sale.order', 'unlink',
    [[1, 2, 3]]
)
```

---

## 关系字段操作

### Many2one

```python
# 设置关联
models.execute_kw(db, uid, password,
    'sale.order', 'write',
    [[1], {'partner_id': 5}]  # 关联到 ID 为 5 的客户
)

# 清除关联
models.execute_kw(db, uid, password,
    'sale.order', 'write',
    [[1], {'partner_id': False}]
)
```

### One2many

```python
# One2many 操作命令
commands = [
    (0, 0, {'product_id': 1, 'qty': 1}),  # 创建新记录
    (1, 2, {'qty': 5}),                    # 更新 ID 为 2 的记录
    (2, 3),                                # 删除 ID 为 3 的记录
    (3, 4),                                # 解除关联 ID 为 4 的记录
    (4, 5),                                # 关联已有 ID 为 5 的记录
    (5, False),                            # 解除所有关联
    (6, 0, [6, 7, 8]),                    # 替换为指定 IDs
]

models.execute_kw(db, uid, password,
    'sale.order', 'write',
    [[1], {'order_line': commands}]
)
```

### Many2many

```python
# Many2many 操作命令 (与 One2many 相同)
models.execute_kw(db, uid, password,
    'sale.order', 'write',
    [[1], {'tag_ids': [(6, 0, [1, 2, 3])]}]  # 设置标签
)
```

---

## 调用方法

### 调用对象方法

```python
# 确认销售订单
result = models.execute_kw(db, uid, password,
    'sale.order',
    'action_confirm',
    [[1]]  # 记录 IDs
)

# 带参数的方法
result = models.execute_kw(db, uid, password,
    'sale.order',
    'action_view_invoice',
    [[1]],
    {}  # kwargs
)
```

### 调用模型方法

```python
# 获取字段信息
fields = models.execute_kw(db, uid, password,
    'sale.order',
    'fields_get',
    [],
    {'attributes': ['string', 'type', 'required']}
)

# 获取默认值
defaults = models.execute_kw(db, uid, password,
    'sale.order',
    'default_get',
    [],
    {'fields': ['partner_id', 'date_order']}
)
```

---

## 错误处理

```python
import xmlrpc.client

try:
    result = models.execute_kw(db, uid, password,
        'sale.order', 'create',
        [{'invalid_field': 'value'}]
    )
except xmlrpc.client.Fault as e:
    print(f"XML-RPC 错误：{e.faultString}")
except Exception as e:
    print(f"其他错误：{e}")
```

---

## 集成示例

### Python 完整示例

```python
import xmlrpc.client
import json

class OdooAPI:
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        
        # 认证
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.uid = common.authenticate(db, username, password, {})
        
        if not self.uid:
            raise Exception("认证失败")
        
        # 对象代理
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    def search(self, model, domain, fields=None, limit=100):
        ids = self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search', [domain],
            {'limit': limit}
        )
        if fields:
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'read', [ids],
                {'fields': fields}
            )
        return ids
    
    def create(self, model, values):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'create', [values]
        )
    
    def update(self, model, ids, values):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'write', [ids, values]
        )
    
    def delete(self, model, ids):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'unlink', [ids]
        )

# 使用示例
api = OdooAPI('http://localhost:8069', 'mydb', 'admin', 'admin')

# 搜索客户
customers = api.search('res.partner', [('customer', '=', True)], 
                       ['name', 'email'], limit=10)

# 创建销售订单
order_id = api.create('sale.order', {
    'partner_id': 1,
    'order_line': [(0, 0, {'product_id': 1, 'qty': 1})],
})
```

### JavaScript (Node.js) 示例

```javascript
const axios = require('axios');

class OdooJSONRPC {
    constructor(url, db, username, password) {
        this.url = url;
        this.db = db;
        this.username = username;
        this.password = password;
        this.uid = null;
    }
    
    async authenticate() {
        const response = await axios.post(`${this.url}/jsonrpc`, {
            jsonrpc: '2.0',
            method: 'call',
            params: {
                service: 'common',
                method: 'authenticate',
                args: [this.db, this.username, this.password, {}]
            }
        });
        
        this.uid = response.data.result;
        return this.uid;
    }
    
    async call(service, method, args = [], kwargs = {}) {
        const response = await axios.post(`${this.url}/jsonrpc`, {
            jsonrpc: '2.0',
            method: 'call',
            params: {
                service: service,
                method: method,
                args: args,
                kwargs: kwargs
            }
        });
        
        return response.data.result;
    }
    
    async search(model, domain, options = {}) {
        return await this.call('object', 'execute_kw', [
            this.db, this.uid, this.password,
            model, 'search', [domain],
            options
        ]);
    }
    
    async read(model, ids, fields = []) {
        return await this.call('object', 'execute_kw', [
            this.db, this.uid, this.password,
            model, 'read', [ids],
            { fields: fields }
        ]);
    }
}

// 使用示例
(async () => {
    const api = new OdooJSONRPC('http://localhost:8069', 'mydb', 'admin', 'admin');
    await api.authenticate();
    
    const orders = await api.search('sale.order', 
        [('state', '=', 'draft')], 
        { limit: 10 }
    );
    
    console.log('Draft orders:', orders);
})();
```

### cURL 示例

```bash
# 认证
curl -X POST http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "common",
      "method": "authenticate",
      "args": ["mydb", "admin", "admin", {}]
    },
    "id": 1
  }'

# 搜索记录
curl -X POST http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "object",
      "method": "execute_kw",
      "args": ["mydb", 2, "admin", "sale.order", "search", [[["state", "=", "draft"]]]]
    },
    "id": 2
  }'
```

---

## 最佳实践

### 1. 连接管理

- ✅ 复用连接（不要每次请求都创建新连接）
- ✅ 实现连接池
- ✅ 处理认证过期

### 2. 批量操作

```python
# ✅ 推荐：批量创建
records = []
for i in range(100):
    records.append({'name': f'Record {i}'})
models.execute_kw(db, uid, password, 'my.model', 'create', records)

# ❌ 不推荐：循环创建
for i in range(100):
    models.execute_kw(db, uid, password, 'my.model', 'create', 
                      [{'name': f'Record {i}'}])
```

### 3. 错误处理

```python
from xmlrpc.client import Fault
import time

def retry_on_error(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Fault as e:
            if i == max_retries - 1:
                raise
            time.sleep(2 ** i)  # 指数退避
```

### 4. 性能优化

- 使用 `search_read` 代替 `search` + `read`
- 限制返回字段
- 使用分页（limit/offset）
- 避免 N+1 查询

---

## 相关 Skill

- [odoo-introduction-skill](../odoo-introduction-skill/SKILL.md) - Odoo 简介
- [odoo-architecture-skill](../odoo-architecture-skill/SKILL.md) - 技术架构

---

## 使用示例

### 场景 1: 数据同步

```
用户：需要将 CRM 系统客户同步到 Odoo

Agent:
1. 加载 odoo-api-skill
2. 查看"集成示例 → Python"
3. 实现同步脚本
4. 处理错误和重试
```

### 场景 2: 创建自定义客户端

```
用户：需要开发一个移动端 App 连接 Odoo

Agent:
1. 加载 odoo-api-skill
2. 查看"JSON-RPC 用法"
3. 查看"JavaScript 示例"
4. 实现认证和数据访问
```

### 场景 3: 批量导入数据

```
用户：需要导入 10000 条产品记录

Agent:
1. 加载 odoo-api-skill
2. 查看"最佳实践 → 批量操作"
3. 使用批量创建
4. 实现分批次处理
```

---

*Skill 版本：v1.0*
*支持 Odoo 版本：17.0 - 18.0*
*最后更新：2026-04-12*
