# Odoo API 最佳实践

## 错误处理

### 重试机制

```python
import time
from functools import wraps
from xmlrpc.client import Fault

def retry_on_error(max_retries=3, delay=1):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Fault as e:
                    if i == max_retries - 1:
                        raise
                    time.sleep(delay * (2 ** i))  # 指数退避
            return None
        return wrapper
    return decorator

class OdooAPI:
    @retry_on_error(max_retries=3)
    def create(self, model, values):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'create', [values]
        )
```

### 错误分类处理

```python
from xmlrpc.client import Fault
import logging

logger = logging.getLogger(__name__)

def execute_with_error_handling(func, model, operation):
    try:
        return func()
    except Fault as e:
        error_msg = str(e.faultString)
        
        if 'Access Denied' in error_msg:
            logger.error(f"权限错误：{model}.{operation}")
            raise PermissionError(f"无权限执行 {operation}")
        
        if 'does not exist' in error_msg:
            logger.error(f"记录不存在：{model}")
            raise KeyError(f"模型 {model} 不存在")
        
        if 'unique constraint' in error_msg.lower():
            logger.error(f"唯一约束冲突：{model}")
            raise ValueError("数据重复")
        
        logger.error(f"未知错误：{error_msg}")
        raise
```

---

## 性能优化

### 批量操作

```python
# ✅ 推荐：批量创建
def create_batch(self, model, records_data, batch_size=100):
    """分批创建记录"""
    results = []
    for i in range(0, len(records_data), batch_size):
        batch = records_data[i:i + batch_size]
        ids = self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'create', [batch]
        )
        results.extend(ids)
    return results

# ❌ 不推荐：单条创建
def create_one_by_one(self, model, records_data):
    results = []
    for data in records_data:
        id = self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'create', [data]
        )
        results.append(id)
    return results
```

### 使用 search_read

```python
# ✅ 推荐：一步完成
records = self.models.execute_kw(
    self.db, self.uid, self.password,
    model, 'search_read', [domain],
    {'fields': fields, 'limit': limit}
)

# ❌ 不推荐：两步
ids = self.models.execute_kw(
    self.db, self.uid, self.password,
    model, 'search', [domain]
)
records = self.models.execute_kw(
    self.db, self.uid, self.password,
    model, 'read', [ids], {'fields': fields}
)
```

### 限制返回字段

```python
# ✅ 推荐：只获取需要的字段
data = self.models.execute_kw(
    self.db, self.uid, self.password,
    model, 'read', [ids],
    {'fields': ['name', 'email', 'phone']}
)

# ❌ 不推荐：获取所有字段
data = self.models.execute_kw(
    self.db, self.uid, self.password,
    model, 'read', [ids]
)
```

### 分页处理

```python
def fetch_all(self, model, domain, fields, limit=100):
    """分页获取所有记录"""
    all_records = []
    offset = 0
    
    while True:
        records = self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search_read', [domain],
            {
                'fields': fields,
                'limit': limit,
                'offset': offset
            }
        )
        
        if not records:
            break
        
        all_records.extend(records)
        offset += limit
    
    return all_records
```

---

## 安全最佳实践

### 使用环境变量

```python
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

ODOO_CONFIG = {
    'url': os.getenv('ODOO_URL', 'http://localhost:8069'),
    'db': os.getenv('ODOO_DB'),
    'username': os.getenv('ODOO_USERNAME'),
    'password': os.getenv('ODOO_PASSWORD'),  # 或 API Key
}

# .env 文件
# ODOO_URL=https://odoo.example.com
# ODOO_DB=production
# ODOO_USERNAME=api_user
# ODOO_PASSWORD=your-api-key-here
```

### 专用集成账户

```python
# ✅ 推荐：创建专用账户
INTEGRATION_USER = {
    'username': 'api_integration',
    'password': 'strong-api-key',
    'groups': ['group_api_user'],  # 限制权限
}

# ❌ 不推荐：使用管理员
ADMIN_USER = {
    'username': 'admin',
    'password': 'admin',
}
```

### 权限最小化

```xml
<!-- 为集成用户创建限制组 -->
<record id="group_api_user" model="res.groups">
    <field name="name">API User</field>
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

### HTTPS 强制

```python
# ✅ 推荐：生产环境使用 HTTPS
url = os.getenv('ODOO_URL', 'https://odoo.example.com')

# 验证 HTTPS
if not url.startswith('https://') and os.getenv('PRODUCTION'):
    raise ValueError("生产环境必须使用 HTTPS")
```

---

## 日志记录

### 结构化日志

```python
import logging
import json

logger = logging.getLogger(__name__)

class OdooAPILogger:
    def __init__(self):
        self.logger = logging.getLogger('odoo_api')
        self.logger.setLevel(logging.INFO)
        
        # JSON 格式处理器
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "level": "%(levelname)s", '
            '"message": "%(message)s"}'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_request(self, model, method, args):
        self.logger.info(json.dumps({
            'action': 'request',
            'model': model,
            'method': method,
            'args_count': len(args) if args else 0
        }))
    
    def log_response(self, model, method, result):
        self.logger.info(json.dumps({
            'action': 'response',
            'model': model,
            'method': method,
            'result_type': type(result).__name__
        }))
    
    def log_error(self, model, method, error):
        self.logger.error(json.dumps({
            'action': 'error',
            'model': model,
            'method': method,
            'error': str(error)
        }))

# 使用
api_logger = OdooAPILogger()

def execute_with_logging(self, model, method, *args, **kwargs):
    api_logger.log_request(model, method, args)
    try:
        result = self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
        api_logger.log_response(model, method, result)
        return result
    except Exception as e:
        api_logger.log_error(model, method, e)
        raise
```

---

## 连接管理

### 连接池

```python
from queue import Queue
from threading import Lock

class OdooConnectionPool:
    def __init__(self, url, db, username, password, pool_size=5):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.pool_size = pool_size
        
        self.pool = Queue(maxsize=pool_size)
        self.lock = Lock()
        
        # 初始化连接池
        for _ in range(pool_size):
            conn = self._create_connection()
            self.pool.put(conn)
    
    def _create_connection(self):
        common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
        models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')
        uid = common.authenticate(self.db, self.username, self.password, {})
        
        return {
            'common': common,
            'models': models,
            'uid': uid,
            'db': self.db,
            'password': self.password
        }
    
    def get_connection(self):
        return self.pool.get()
    
    def return_connection(self, conn):
        self.pool.put(conn)
    
    def execute(self, model, method, *args, **kwargs):
        conn = self.get_connection()
        try:
            return conn['models'].execute_kw(
                conn['db'], conn['uid'], conn['password'],
                model, method, args, kwargs
            )
        finally:
            self.return_connection(conn)

# 使用
pool = OdooConnectionPool(
    'http://localhost:8069',
    'mydb',
    'admin',
    'admin',
    pool_size=5
)

# 多线程安全
result = pool.execute('sale.order', 'search_read', [[]])
```

### 超时设置

```python
import xmlrpc.client
import socket

# 设置超时
socket.setdefaulttimeout(30)

# 或使用自定义传输
class TimeoutTransport(xmlrpc.client.Transport):
    def __init__(self, timeout=30):
        super().__init__()
        self.timeout = timeout
    
    def make_connection(self, host):
        conn = super().make_connection(host)
        conn.timeout = self.timeout
        return conn

transport = TimeoutTransport(timeout=30)
common = xmlrpc.client.ServerProxy(
    'http://localhost:8069/xmlrpc/2/common',
    transport=transport
)
```

---

## 测试

### 单元测试

```python
import unittest
from unittest.mock import Mock, patch

class TestOdooAPI(unittest.TestCase):
    
    @patch('xmlrpc.client.ServerProxy')
    def test_create_order(self, mock_proxy):
        # Mock 认证
        mock_common = Mock()
        mock_common.authenticate.return_value = 2
        
        # Mock 创建
        mock_models = Mock()
        mock_models.execute_kw.return_value = 1
        
        mock_proxy.side_effect = [mock_common, mock_models]
        
        # 测试
        api = OdooAPI('http://localhost:8069', 'mydb', 'admin', 'admin')
        order_id = api.create('sale.order', {'partner_id': 1})
        
        # 断言
        self.assertEqual(order_id, 1)
        mock_models.execute_kw.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

### 集成测试

```python
import os
import unittest

@unittest.skipIf(not os.getenv('TEST_ODOO'), "需要 Odoo 测试环境")
class TestOdooIntegration(unittest.TestCase):
    
    def setUp(self):
        self.api = OdooAPI(
            os.getenv('ODOO_URL'),
            os.getenv('ODOO_DB'),
            os.getenv('ODOO_USERNAME'),
            os.getenv('ODOO_PASSWORD')
        )
    
    def test_create_and_read(self):
        # 创建
        partner_id = self.api.create('res.partner', {
            'name': 'Test Partner',
            'email': 'test@example.com'
        })
        
        # 读取
        partner = self.api.read('res.partner', [partner_id], ['name', 'email'])
        
        # 验证
        self.assertEqual(partner[0]['name'], 'Test Partner')
        
        # 清理
        self.api.delete('res.partner', [partner_id])
```

---

## 监控和告警

### 性能监控

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start
            
            if duration > 5:  # 超过 5 秒告警
                logger.warning(f"慢查询：{func.__name__} ({duration:.2f}s)")
            
            return result
        except Exception as e:
            logger.error(f"错误：{func.__name__}: {e}")
            raise
    return wrapper

class OdooAPI:
    @monitor_performance
    def search_read(self, model, domain, fields):
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search_read', [domain],
            {'fields': fields}
        )
```

---

*参考：Odoo 官方最佳实践*
