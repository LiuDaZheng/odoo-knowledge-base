# Odoo API 认证

## 认证方法

### 1. 用户名 + 密码

```python
import xmlrpc.client

url = 'http://localhost:8069'
db = 'mydb'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
```

**适用场景**:
- 开发测试
- 内部集成
- 临时脚本

**安全建议**:
- 仅用于 HTTPS
- 使用专用集成账户
- 定期更换密码

---

### 2. API Key (推荐)

Odoo 14+ 支持 API Key 认证。

#### 生成 API Key

1. 登录 Odoo
2. 进入 **设置 → 用户 → 选择用户**
3. 点击 **操作 → 更改密码**
4. 生成 API Key

#### 使用 API Key

```python
# API Key 作为密码使用
password = 'api-key-here'
uid = common.authenticate(db, username, password, {})
```

**优势**:
- 可独立撤销
- 不影响主密码
- 可设置过期时间

---

### 3. OAuth 2.0

企业版支持 OAuth 2.0 集成。

#### 配置 OAuth Provider

```xml
<record id="oauth_provider" model="auth.oauth.provider">
    <field name="name">My OAuth</field>
    <field name="client_id">your-client-id</field>
    <field name="validation_endpoint">https://oauth-server/validate</field>
</record>
```

#### OAuth 流程

```
1. 用户点击"使用 OAuth 登录"
   ↓
2. 重定向到 OAuth 提供商
   ↓
3. 用户授权
   ↓
4. 返回授权码
   ↓
5. 换取访问令牌
   ↓
6. 使用令牌访问 API
```

---

## 认证端点

### XML-RPC

```
# Odoo 17/18
http://<host>:<port>/xmlrpc/2/common

# Odoo 16 及更早
http://<host>:<port>/xmlrpc/common
```

### JSON-RPC

```
http://<host>:<port>/jsonrpc
```

---

## 认证示例

### Python XML-RPC

```python
import xmlrpc.client

def authenticate(url, db, username, password):
    """认证并返回用户 ID"""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    
    try:
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"认证成功，用户 ID: {uid}")
            return uid
        else:
            print("认证失败：用户名或密码错误")
            return None
    except Exception as e:
        print(f"认证错误：{e}")
        return None

# 使用
uid = authenticate('http://localhost:8069', 'mydb', 'admin', 'admin')
```

### Python JSON-RPC

```python
import requests
import json

def authenticate_json(url, db, username, password):
    """JSON-RPC 认证"""
    payload = {
        'jsonrpc': '2.0',
        'method': 'call',
        'params': {
            'service': 'common',
            'method': 'authenticate',
            'args': [db, username, password, {}]
        },
        'id': 1
    }
    
    response = requests.post(
        f'{url}/jsonrpc',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    result = response.json()
    if 'result' in result:
        return result['result']
    else:
        raise Exception(result.get('error', {}).get('message'))

# 使用
uid = authenticate_json('http://localhost:8069', 'mydb', 'admin', 'admin')
```

### Node.js

```javascript
const axios = require('axios');

async function authenticate(url, db, username, password) {
    const response = await axios.post(`${url}/jsonrpc`, {
        jsonrpc: '2.0',
        method: 'call',
        params: {
            service: 'common',
            method: 'authenticate',
            args: [db, username, password, {}]
        },
        id: 1
    });
    
    if (response.data.result) {
        console.log('认证成功，用户 ID:', response.data.result);
        return response.data.result;
    } else {
        throw new Error('认证失败');
    }
}

// 使用
authenticate('http://localhost:8069', 'mydb', 'admin', 'admin')
    .then(uid => console.log('UID:', uid))
    .catch(err => console.error('错误:', err));
```

### PHP

```php
<?php
function authenticate($url, $db, $username, $password) {
    $client = new xmlrpc_client("/xmlrpc/2/common", $url, 8069);
    
    $msg = new xmlrpcmsg("authenticate");
    $msg->addParam(new xmlrpcval($db, "string"));
    $msg->addParam(new xmlrpcval($username, "string"));
    $msg->addParam(new xmlrpcval($password, "string"));
    $msg->addParam(new xmlrpcval(array(), "struct"));
    
    $resp = $client->send($msg);
    
    if ($resp->faultCode()) {
        echo "认证失败：" . $resp->faultString();
        return null;
    }
    
    $uid = $resp->value()->scalarval();
    echo "认证成功，用户 ID: $uid";
    return $uid;
}

// 使用
$uid = authenticate('localhost', 'mydb', 'admin', 'admin');
?>
```

---

## 会话管理

### 保持会话

```python
class OdooSession:
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # 认证
        self.authenticate()
    
    def authenticate(self):
        """认证"""
        self.uid = self.common.authenticate(
            self.db, self.username, self.password, {}
        )
        if not self.uid:
            raise Exception("认证失败")
    
    def is_authenticated(self):
        """检查是否已认证"""
        return self.uid is not None
    
    def execute(self, model, method, *args, **kwargs):
        """执行方法"""
        if not self.is_authenticated():
            self.authenticate()
        
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )

# 使用
session = OdooSession('http://localhost:8069', 'mydb', 'admin', 'admin')
orders = session.execute('sale.order', 'search', [[]])
```

### 重新认证

```python
def execute_with_retry(func, max_retries=3):
    """执行并处理认证过期"""
    for i in range(max_retries):
        try:
            return func()
        except xmlrpc.client.Fault as e:
            if 'Access Denied' in str(e):
                # 重新认证
                session.authenticate()
                if i == max_retries - 1:
                    raise
            else:
                raise
```

---

## 安全最佳实践

### 1. 使用 HTTPS

```python
# ✅ 推荐
url = 'https://odoo.example.com'

# ❌ 不推荐 (生产环境)
url = 'http://odoo.example.com'
```

### 2. 使用专用账户

```python
# ✅ 推荐：创建专用集成账户
username = 'api_integration'
password = 'strong-api-key'

# ❌ 不推荐：使用管理员账户
username = 'admin'
password = 'admin'
```

### 3. 环境变量存储凭证

```python
import os

url = os.getenv('ODOO_URL')
db = os.getenv('ODOO_DB')
username = os.getenv('ODOO_USERNAME')
password = os.getenv('ODOO_PASSWORD')

# .env 文件
# ODOO_URL=https://odoo.example.com
# ODOO_DB=mydb
# ODOO_USERNAME=api_user
# ODOO_PASSWORD=secret-key
```

### 4. 限制权限

```xml
<!-- 为集成用户创建限制组 -->
<record id="group_api_user" model="res.groups">
    <field name="name">API User</field>
    <field name="category_id" ref="base.module_category_hidden"/>
</record>

<!-- 限制访问的模型 -->
<record id="access_sale_order_api" model="ir.model.access">
    <field name="name">sale.order api access</field>
    <field name="model_id" ref="model_sale_order"/>
    <field name="group_id" ref="group_api_user"/>
    <field name="perm_read" eval="1"/>
    <field name="perm_write" eval="1"/>
    <field name="perm_create" eval="1"/>
    <field name="perm_unlink" eval="0"/>  <!-- 禁止删除 -->
</record>
```

### 5. 日志记录

```python
import logging

_logger = logging.getLogger(__name__)

def authenticate_and_log(url, db, username, password):
    _logger.info(f"尝试认证：{username}@{db}")
    
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if uid:
        _logger.info(f"认证成功：{uid}")
    else:
        _logger.warning(f"认证失败：{username}")
    
    return uid
```

---

## 故障排除

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 认证失败 | 密码错误 | 检查密码，重置 API Key |
| 连接超时 | 网络问题 | 检查防火墙，确认端口 |
| 数据库不存在 | DB 名错误 | 检查数据库名 |
| 权限不足 | 用户权限 | 检查用户组和 ACL |

### 调试技巧

```python
# 启用 XML-RPC 日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 测试连接
import socket
socket.create_connection(('odoo.example.com', 8069), timeout=5)

# 检查数据库列表
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
dbs = common.list()
print("可用数据库:", dbs)
```

---

*参考：Odoo 官方安全文档*
