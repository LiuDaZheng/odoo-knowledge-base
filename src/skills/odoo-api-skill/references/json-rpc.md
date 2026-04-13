# JSON-RPC API 详解

## 概述

JSON-RPC 是 Odoo 的现代 API 协议，推荐使用于 Web 和移动端应用。

---

## 端点

```
统一端点：http://<host>:<port>/jsonrpc
Content-Type: application/json
```

---

## 请求格式

```json
{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "<service_name>",
        "method": "<method_name>",
        "args": [<arg1>, <arg2>, ...],
        "kwargs": {"key": "value"}
    },
    "id": <request_id>
}
```

---

## 响应格式

### 成功

```json
{
    "jsonrpc": "2.0",
    "id": <request_id>,
    "result": <return_value>
}
```

### 错误

```json
{
    "jsonrpc": "2.0",
    "id": <request_id>,
    "error": {
        "code": <error_code>,
        "message": "<error_message>",
        "data": "<debug_info>"
    }
}
```

---

## 认证

### 请求

```json
POST /jsonrpc
Content-Type: application/json

{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "authenticate",
        "args": ["mydb", "admin", "admin", {}]
    },
    "id": 1
}
```

### 响应

```json
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": 2
}
```

---

## Python 示例

### 基础客户端

```python
import requests
import json

class OdooJSONRPC:
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.uid = None
        self.session = requests.Session()
        
        self._authenticate()
    
    def _authenticate(self):
        """认证"""
        payload = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'service': 'common',
                'method': 'authenticate',
                'args': [self.db, self.username, self.password, {}]
            },
            'id': 1
        }
        
        response = self.session.post(
            f'{self.url}/jsonrpc',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        result = response.json()
        if 'result' in result:
            self.uid = result['result']
        else:
            raise Exception(result.get('error', {}).get('message'))
    
    def call(self, service, method, args=None, kwargs=None):
        """通用调用方法"""
        payload = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'service': service,
                'method': method,
                'args': args or [],
                'kwargs': kwargs or {}
            },
            'id': 2
        }
        
        response = self.session.post(
            f'{self.url}/jsonrpc',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        result = response.json()
        if 'result' in result:
            return result['result']
        else:
            raise Exception(result.get('error', {}).get('message'))
    
    def search(self, model, domain, fields=None, limit=100):
        """搜索记录"""
        ids = self.call('object', 'execute_kw', [
            self.db, self.uid, self.password,
            model, 'search', [domain]
        ], {'limit': limit})
        
        if fields:
            return self.call('object', 'execute_kw', [
                self.db, self.uid, self.password,
                model, 'read', [ids]
            ], {'fields': fields})
        return ids
    
    def search_read(self, model, domain, fields=None, limit=100):
        """搜索并读取"""
        return self.call('object', 'execute_kw', [
            self.db, self.uid, self.password,
            model, 'search_read', [domain]
        ], {
            'fields': fields or [],
            'limit': limit
        })
    
    def create(self, model, values):
        """创建记录"""
        return self.call('object', 'execute_kw', [
            self.db, self.uid, self.password,
            model, 'create', [values]
        ])
    
    def update(self, model, ids, values):
        """更新记录"""
        return self.call('object', 'execute_kw', [
            self.db, self.uid, self.password,
            model, 'write', [ids, values]
        ])
    
    def delete(self, model, ids):
        """删除记录"""
        return self.call('object', 'execute_kw', [
            self.db, self.uid, self.password,
            model, 'unlink', [ids]
        ])
    
    def execute(self, model, method, args=None, kwargs=None):
        """执行方法"""
        return self.call('object', 'execute_kw', [
            self.db, self.uid, self.password,
            model, method, args or []
        ], kwargs or {})

# 使用示例
api = OdooJSONRPC('http://localhost:8069', 'mydb', 'admin', 'admin')

# 搜索客户
customers = api.search_read('res.partner', 
    [('customer', '=', True)], 
    fields=['name', 'email'], 
    limit=10
)

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

## JavaScript 示例

### Node.js

```javascript
const axios = require('axios');

class OdooJSONRPC {
    constructor(url, db, username, password) {
        this.url = url;
        this.db = db;
        this.username = username;
        this.password = password;
        this.uid = null;
        this.axios = axios.create({
            baseURL: url,
            headers: {'Content-Type': 'application/json'}
        });
        
        this.authenticate();
    }
    
    async authenticate() {
        const response = await this.axios.post('/jsonrpc', {
            jsonrpc: '2.0',
            method: 'call',
            params: {
                service: 'common',
                method: 'authenticate',
                args: [this.db, this.username, this.password, {}]
            },
            id: 1
        });
        
        this.uid = response.data.result;
        return this.uid;
    }
    
    async call(service, method, args = [], kwargs = {}) {
        const response = await this.axios.post('/jsonrpc', {
            jsonrpc: '2.0',
            method: 'call',
            params: {
                service: service,
                method: method,
                args: args,
                kwargs: kwargs
            },
            id: 2
        });
        
        if (response.data.result) {
            return response.data.result;
        } else {
            throw new Error(response.data.error?.message || 'Unknown error');
        }
    }
    
    async searchRead(model, domain, fields = [], limit = 100) {
        return await this.call('object', 'execute_kw', [
            this.db, this.uid, this.password,
            model, 'search_read', [domain]
        ], { fields, limit });
    }
    
    async create(model, values) {
        return await this.call('object', 'execute_kw', [
            this.db, this.uid, this.password,
            model, 'create', [values]
        ]);
    }
    
    async update(model, ids, values) {
        return await this.call('object', 'execute_kw', [
            this.db, this.uid, this.password,
            model, 'write', [ids, values]
        ]);
    }
    
    async execute(model, method, args = [], kwargs = {}) {
        return await this.call('object', 'execute_kw', [
            this.db, this.uid, this.password,
            model, method, args
        ], kwargs);
    }
}

// 使用示例
(async () => {
    const api = new OdooJSONRPC('http://localhost:8069', 'mydb', 'admin', 'admin');
    
    // 搜索订单
    const orders = await api.searchRead('sale.order', 
        [('state', '=', 'draft')], 
        ['name', 'amount_total']
    );
    
    console.log('Draft orders:', orders);
    
    // 创建订单
    const orderId = await api.create('sale.order', {
        partner_id: 1,
        order_line: [(0, 0, { product_id: 1, product_uom_qty: 1 })]
    });
    
    console.log('Created order:', orderId);
})();
```

### 浏览器

```javascript
class OdooBrowserClient {
    constructor(url, db, username, password) {
        this.url = url;
        this.db = db;
        this.username = username;
        this.password = password;
        this.uid = null;
    }
    
    async call(service, method, args = [], kwargs = {}) {
        const response = await fetch(`${this.url}/jsonrpc`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                jsonrpc: '2.0',
                method: 'call',
                params: { service, method, args, kwargs },
                id: Date.now()
            })
        });
        
        const data = await response.json();
        if (data.result) {
            return data.result;
        } else {
            throw new Error(data.error?.message);
        }
    }
    
    async authenticate() {
        this.uid = await this.call('common', 'authenticate', [
            this.db, this.username, this.password, {}
        ]);
        return this.uid;
    }
    
    async searchRead(model, domain, fields = []) {
        return await this.call('object', 'execute_kw', [
            this.db, this.uid, this.password,
            model, 'search_read', [domain]
        ], { fields });
    }
}

// 使用示例
const api = new OdooBrowserClient('http://localhost:8069', 'mydb', 'admin', 'admin');
api.authenticate().then(() => {
    return api.searchRead('sale.order', [['state', '=', 'draft']], ['name']);
}).then(orders => {
    console.log('Orders:', orders);
});
```

---

## cURL 示例

### 认证

```bash
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
```

### 搜索记录

```bash
curl -X POST http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "object",
      "method": "execute_kw",
      "args": ["mydb", 2, "admin", "sale.order", "search_read", [[["state", "=", "draft"]]]],
      "kwargs": {"fields": ["name", "amount_total"], "limit": 10}
    },
    "id": 2
  }'
```

### 创建记录

```bash
curl -X POST http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "object",
      "method": "execute_kw",
      "args": ["mydb", 2, "admin", "sale.order", "create", [{"partner_id": 1, "order_line": [[0, 0, {"product_id": 1, "product_uom_qty": 1}]]}]]
    },
    "id": 3
  }'
```

---

## PHP 示例

```php
<?php
class OdooJSONRPC {
    private $url;
    private $db;
    private $uid;
    
    public function __construct($url, $db, $username, $password) {
        $this->url = $url;
        $this->db = $db;
        $this->authenticate($username, $password);
    }
    
    private function authenticate($username, $password) {
        $payload = [
            'jsonrpc' => '2.0',
            'method' => 'call',
            'params' => [
                'service' => 'common',
                'method' => 'authenticate',
                'args' => [$this->db, $username, $password, []]
            ],
            'id' => 1
        ];
        
        $response = $this->send($payload);
        $this->uid = $response['result'];
        
        if (!$this->uid) {
            throw new Exception('认证失败');
        }
    }
    
    private function send($payload) {
        $ch = curl_init($this->url . '/jsonrpc');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
    
    public function call($service, $method, $args = [], $kwargs = []) {
        $payload = [
            'jsonrpc' => '2.0',
            'method' => 'call',
            'params' => [
                'service' => $service,
                'method' => $method,
                'args' => $args,
                'kwargs' => $kwargs
            ],
            'id' => 2
        ];
        
        $response = $this->send($payload);
        
        if (isset($response['result'])) {
            return $response['result'];
        } else {
            throw new Exception($response['error']['message'] ?? 'Unknown error');
        }
    }
    
    public function searchRead($model, $domain, $fields = [], $limit = 100) {
        return $this->call('object', 'execute_kw', [
            $this->db, $this->uid, 'admin',
            $model, 'search_read', [$domain]
        ], ['fields' => $fields, 'limit' => $limit]);
    }
}

// 使用示例
$api = new OdooJSONRPC('http://localhost:8069', 'mydb', 'admin', 'admin');
$orders = $api->searchRead('sale.order', [['state', '=', 'draft']], ['name', 'amount_total']);
print_r($orders);
?>
```

---

## 错误处理

```python
import requests
import json

class OdooError(Exception):
    """Odoo API 错误"""
    pass

class OdooJSONRPC:
    def call(self, service, method, args=None, kwargs=None):
        payload = {
            'jsonrpc': '2.0',
            'method': 'call',
            'params': {
                'service': service,
                'method': method,
                'args': args or [],
                'kwargs': kwargs or {}
            },
            'id': 2
        }
        
        try:
            response = requests.post(
                f'{self.url}/jsonrpc',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if 'error' in result:
                error = result['error']
                raise OdooError(f"{error.get('message')}: {error.get('data', '')}")
            
            return result.get('result')
            
        except requests.exceptions.Timeout:
            raise OdooError('请求超时')
        except requests.exceptions.ConnectionError:
            raise OdooError('连接失败')
        except json.JSONDecodeError:
            raise OdooError('响应格式错误')

# 使用
try:
    api = OdooJSONRPC('http://localhost:8069', 'mydb', 'admin', 'admin')
    orders = api.search_read('sale.order', [[]])
except OdooError as e:
    print(f"错误：{e}")
```

---

*参考：Odoo 官方 JSON-RPC 文档*
