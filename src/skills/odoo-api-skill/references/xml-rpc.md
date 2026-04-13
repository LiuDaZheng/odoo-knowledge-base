# XML-RPC API 详解

## 概述

XML-RPC 是 Odoo 的传统 API 协议，提供广泛的编程语言支持。

---

## 连接设置

### Python

```python
import xmlrpc.client

# 配置
url = 'http://localhost:8069'
db = 'mydb'
username = 'admin'
password = 'admin'

# 创建代理
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 认证
uid = common.authenticate(db, username, password, {})
```

### 其他语言

| 语言 | 库 | 示例 |
|------|-----|------|
| Java | Apache XML-RPC | `XmlRpcClient` |
| PHP | 内置 | `xmlrpc_client` |
| Ruby | xmlrpc | `XMLRPC::Client` |
| C# | CookComputing.XmlRpc | `XmlRpcProxy` |
| JavaScript | xmlrpc | `xmlrpc.Client` |

---

## 认证服务

### authenticate

```python
uid = common.authenticate(db, username, password, {})
```

### check_access_rights

```python
# 检查访问权限
has_access = common.check_access_rights(
    db, uid, password,
    'sale.order',  # 模型
    'read',        # 操作
    False          # 是否检查记录级权限
)
```

### version

```python
# 获取版本信息
version = common.version()
print(version)
# 输出：{'server_version': '17.0', 'server_version_info': [17, 0, 0, '', '']}
```

### list_lang

```python
# 获取语言列表
langs = common.list_lang()
print(langs)
# 输出：[['en_US', 'English (US)'], ['zh_CN', 'Chinese (Simplified)'], ...]
```

### list_countries

```python
# 获取国家列表
countries = common.list_countries()
print(countries)
```

---

## 对象服务

### execute (XML-RPC)

```python
# 基本用法
result = models.execute(
    db, uid, password,
    'sale.order',      # 模型
    'search',          # 方法
    [[('state', '=', 'draft')]]  # 参数
)
```

### execute_kw (推荐)

```python
# 带关键字参数
result = models.execute_kw(
    db, uid, password,
    'sale.order',
    'search',
    [[('state', '=', 'draft')]],  # args
    {'limit': 10, 'order': 'date_order desc'}  # kwargs
)
```

---

## CRUD 操作

### Search

```python
# 基础搜索
ids = models.execute_kw(db, uid, password,
    'sale.order', 'search', [[]])

# 带条件
ids = models.execute_kw(db, uid, password,
    'sale.order', 'search',
    [[('state', '=', 'draft'), ('amount_total', '>', 1000)]]
)

# 带选项
ids = models.execute_kw(db, uid, password,
    'sale.order', 'search',
    [[]],
    {
        'offset': 0,
        'limit': 100,
        'order': 'date_order desc',
    }
)
```

### Search Count

```python
count = models.execute_kw(db, uid, password,
    'sale.order', 'search_count',
    [[('state', '=', 'draft')]]
)
print(f"Draft orders: {count}")
```

### Read

```python
# 读取所有字段
data = models.execute_kw(db, uid, password,
    'sale.order', 'read', [[1, 2, 3]])

# 读取特定字段
data = models.execute_kw(db, uid, password,
    'sale.order', 'read',
    [[1, 2, 3]],
    {'fields': ['name', 'partner_id', 'amount_total']}
)
```

### Search Read (推荐)

```python
# 一步完成搜索和读取
records = models.execute_kw(db, uid, password,
    'sale.order', 'search_read',
    [[('state', '=', 'draft')]],
    {
        'fields': ['name', 'partner_id', 'amount_total'],
        'limit': 10,
        'order': 'date_order desc'
    }
)
```

### Create

```python
# 创建简单记录
partner_id = models.execute_kw(db, uid, password,
    'res.partner', 'create',
    [{
        'name': 'New Customer',
        'email': 'customer@example.com',
        'phone': '123456789',
    }]
)

# 创建带 One2many 的记录
order_id = models.execute_kw(db, uid, password,
    'sale.order', 'create',
    [{
        'partner_id': partner_id,
        'order_line': [
            (0, 0, {
                'product_id': 1,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            }),
        ],
    }]
)
```

### Write

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

### Unlink

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
    [[1], {'partner_id': 5}]
)

# 清除关联
models.execute_kw(db, uid, password,
    'sale.order', 'write',
    [[1], {'partner_id': False}]
)
```

### One2many / Many2many 命令

```python
# 命令格式
# (操作，ID, 值)

commands = [
    (0, 0, {'product_id': 1, 'qty': 1}),  # 创建新记录
    (1, 2, {'qty': 5}),                    # 更新 ID=2 的记录
    (2, 3),                                # 删除 ID=3 的记录
    (3, 4),                                # 解除关联 ID=4
    (4, 5),                                # 关联已有 ID=5
    (5, False),                            # 解除所有关联
    (6, 0, [6, 7, 8]),                    # 替换为 IDs [6,7,8]
]

models.execute_kw(db, uid, password,
    'sale.order', 'write',
    [[1], {'order_line': commands}]
)
```

---

## 调用方法

### 调用对象方法

```python
# 确认订单
result = models.execute_kw(db, uid, password,
    'sale.order',
    'action_confirm',
    [[1]]  # 记录 IDs
)

# 创建发票
invoice_ids = models.execute_kw(db, uid, password,
    'sale.order',
    'action_create_invoice',
    [[1]]
)
```

### 调用模型方法

```python
# 获取字段信息
fields = models.execute_kw(db, uid, password,
    'sale.order',
    'fields_get',
    [],
    {'attributes': ['string', 'type', 'required', 'selection']}
)

# 获取默认值
defaults = models.execute_kw(db, uid, password,
    'sale.order',
    'default_get',
    [],
    {'fields': ['partner_id', 'date_order', 'state']}
)

# 获取字段变化
result = models.execute_kw(db, uid, password,
    'sale.order',
    'onchange',
    [[], {'partner_id': 1}, ['partner_id']],
    {'partner_id': 1}
)
```

---

## 元数据操作

### 获取模型列表

```python
models_list = models.execute_kw(db, uid, password,
    'ir.model', 'search_read',
    [[]],
    {'fields': ['model', 'name'], 'limit': 100}
)
```

### 获取字段信息

```python
fields = models.execute_kw(db, uid, password,
    'sale.order', 'fields_get',
    [],
    {'attributes': ['string', 'type', 'relation', 'selection']}
)

# 输出示例
{
    'name': {'string': 'Order', 'type': 'char'},
    'partner_id': {'string': 'Customer', 'type': 'many2one', 'relation': 'res.partner'},
    'state': {'string': 'Status', 'type': 'selection', 'selection': [...]}
}
```

### 检查权限

```python
permissions = models.execute_kw(db, uid, password,
    'sale.order', 'check_access_rights',
    ['read'],
    {'raise_exception': False}
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
    print(f"XML-RPC Fault: {e.faultString}")
    # 输出：XML-RPC Fault: 'invalid_field'
except xmlrpc.client.ProtocolError as e:
    print(f"Protocol Error: {e.errmsg}")
except Exception as e:
    print(f"Other Error: {e}")
```

---

## 性能优化

### 批量操作

```python
# ✅ 推荐：批量创建
records_data = [{'name': f'Record {i}'} for i in range(100)]
ids = models.execute_kw(db, uid, password,
    'my.model', 'create', [records_data]
)

# ❌ 不推荐：循环创建
ids = []
for i in range(100):
    id = models.execute_kw(db, uid, password,
        'my.model', 'create', [{'name': f'Record {i}'}]
    )
    ids.append(id)
```

### 使用 search_read

```python
# ✅ 推荐：一步完成
records = models.execute_kw(db, uid, password,
    'sale.order', 'search_read',
    [[('state', '=', 'draft')]],
    {'fields': ['name', 'amount_total']}
)

# ❌ 不推荐：两步
ids = models.execute_kw(db, uid, password,
    'sale.order', 'search', [[('state', '=', 'draft')]]
)
records = models.execute_kw(db, uid, password,
    'sale.order', 'read', [ids], {'fields': ['name', 'amount_total']}
)
```

### 限制返回字段

```python
# ✅ 推荐：只获取需要的字段
data = models.execute_kw(db, uid, password,
    'sale.order', 'read',
    [[1]],
    {'fields': ['name', 'amount_total']}
)

# ❌ 不推荐：获取所有字段
data = models.execute_kw(db, uid, password,
    'sale.order', 'read', [[1]]
)
```

---

## 完整示例

```python
import xmlrpc.client
from contextlib import contextmanager

class OdooXMLRPC:
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        self.uid = self.common.authenticate(db, username, password, {})
        if not self.uid:
            raise Exception("认证失败")
    
    @contextmanager
    def error_handler(self, operation):
        try:
            yield
        except xmlrpc.client.Fault as e:
            raise Exception(f"{operation} 失败：{e.faultString}")
    
    def search(self, model, domain, fields=None, limit=100):
        with self.error_handler('搜索'):
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
        with self.error_handler('创建'):
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'create', [values]
            )
    
    def update(self, model, ids, values):
        with self.error_handler('更新'):
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'write', [ids, values]
            )
    
    def delete(self, model, ids):
        with self.error_handler('删除'):
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, 'unlink', [ids]
            )
    
    def execute(self, model, method, *args, **kwargs):
        with self.error_handler(f'执行 {method}'):
            return self.models.execute_kw(
                self.db, self.uid, self.password,
                model, method, args, kwargs
            )

# 使用示例
api = OdooXMLRPC('http://localhost:8069', 'mydb', 'admin', 'admin')

# 搜索客户
customers = api.search('res.partner', [('customer', '=', True)], 
                       ['name', 'email'], limit=10)

# 创建销售订单
order_id = api.create('sale.order', {
    'partner_id': customers[0]['id'] if customers else 1,
    'order_line': [(0, 0, {'product_id': 1, 'product_uom_qty': 1})],
})

# 确认订单
api.execute('sale.order', 'action_confirm', [order_id])

print(f"订单 {order_id} 已确认")
```

---

*参考：Odoo 官方 XML-RPC 文档*
