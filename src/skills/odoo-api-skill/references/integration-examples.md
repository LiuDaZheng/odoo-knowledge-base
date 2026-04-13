# Odoo API 集成示例

## Python 完整示例

### CRM 同步脚本

```python
#!/usr/bin/env python3
"""
CRM 客户同步脚本
将外部 CRM 系统的客户同步到 Odoo
"""

import xmlrpc.client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CRMSync:
    def __init__(self, odoo_url, odoo_db, odoo_user, odoo_password):
        """初始化 Odoo 连接"""
        self.url = odoo_url
        self.db = odoo_db
        self.username = odoo_user
        self.password = odoo_password
        
        # 认证
        self.common = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{odoo_url}/xmlrpc/2/object')
        self.uid = self.common.authenticate(odoo_db, odoo_user, odoo_password, {})
        
        if not self.uid:
            raise Exception("Odoo 认证失败")
        
        logger.info(f"已连接到 Odoo: {odoo_url}/{odoo_db}")
    
    def sync_customer(self, customer_data):
        """同步单个客户"""
        try:
            # 检查客户是否已存在
            existing = self.models.execute_kw(
                self.db, self.uid, self.password,
                'res.partner', 'search',
                [[('email', '=', customer_data['email'])]]
            )
            
            if existing:
                # 更新现有客户
                self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'res.partner', 'write',
                    [existing[0], customer_data]
                )
                logger.info(f"更新客户：{customer_data['name']}")
                return existing[0]
            else:
                # 创建新客户
                partner_id = self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'res.partner', 'create',
                    [customer_data]
                )
                logger.info(f"创建客户：{customer_data['name']} (ID: {partner_id})")
                return partner_id
                
        except Exception as e:
            logger.error(f"同步客户失败：{e}")
            raise
    
    def sync_customers_batch(self, customers):
        """批量同步客户"""
        results = []
        for customer in customers:
            try:
                partner_id = self.sync_customer(customer)
                results.append({'email': customer['email'], 'status': 'success', 'id': partner_id})
            except Exception as e:
                results.append({'email': customer['email'], 'status': 'error', 'error': str(e)})
        return results
    
    def create_sale_order(self, partner_id, order_lines):
        """创建销售订单"""
        order_data = {
            'partner_id': partner_id,
            'order_line': [
                (0, 0, line) for line in order_lines
            ],
        }
        
        order_id = self.models.execute_kw(
            self.db, self.uid, self.password,
            'sale.order', 'create',
            [order_data]
        )
        
        logger.info(f"创建销售订单：{order_id}")
        return order_id
    
    def confirm_order(self, order_id):
        """确认订单"""
        self.models.execute_kw(
            self.db, self.uid, self.password,
            'sale.order', 'action_confirm',
            [[order_id]]
        )
        logger.info(f"确认订单：{order_id}")

# 使用示例
if __name__ == '__main__':
    # 初始化
    sync = CRMSync(
        odoo_url='http://localhost:8069',
        odoo_db='mydb',
        odoo_user='admin',
        odoo_password='admin'
    )
    
    # 同步客户
    customers = [
        {'name': 'Customer 1', 'email': 'c1@example.com', 'phone': '123456'},
        {'name': 'Customer 2', 'email': 'c2@example.com', 'phone': '789012'},
    ]
    
    results = sync.sync_customers_batch(customers)
    print(f"同步结果：{results}")
    
    # 创建订单
    if results[0]['status'] == 'success':
        order_id = sync.create_sale_order(results[0]['id'], [
            {'product_id': 1, 'product_uom_qty': 1, 'price_unit': 100.0}
        ])
        sync.confirm_order(order_id)
```

---

## JavaScript/Node.js 示例

### 电商订单同步

```javascript
/**
 * 电商订单同步到 Odoo
 */

const axios = require('axios');

class EcommerceSync {
    constructor(odooUrl, odooDb, odooUser, odooPassword) {
        this.url = odooUrl;
        this.db = odooDb;
        this.username = odooUser;
        this.password = odooPassword;
        this.uid = null;
        
        this.axios = axios.create({
            baseURL: odooUrl,
            headers: {'Content-Type': 'application/json'},
            timeout: 30000
        });
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
        if (!this.uid) {
            throw new Error('Odoo 认证失败');
        }
        
        console.log('已连接到 Odoo');
    }
    
    async call(service, method, args = [], kwargs = {}) {
        const response = await this.axios.post('/jsonrpc', {
            jsonrpc: '2.0',
            method: 'call',
            params: {
                service,
                method,
                args,
                kwargs
            },
            id: Date.now()
        });
        
        if (response.data.error) {
            throw new Error(response.data.error.message);
        }
        
        return response.data.result;
    }
    
    async syncOrder(ecommerceOrder) {
        try {
            // 1. 查找或创建客户
            let partner = await this.call('object', 'execute_kw', [
                this.db, this.uid, this.password,
                'res.partner', 'search_read',
                [[('email', '=', ecommerceOrder.customer.email)]]
            ], { limit: 1 });
            
            if (partner.length === 0) {
                const partnerId = await this.call('object', 'execute_kw', [
                    this.db, this.uid, this.password,
                    'res.partner', 'create',
                    [{
                        name: ecommerceOrder.customer.name,
                        email: ecommerceOrder.customer.email,
                        phone: ecommerceOrder.customer.phone,
                    }]
                ]);
                partner = [{ id: partnerId }];
            }
            
            // 2. 创建销售订单
            const orderLines = ecommerceOrder.items.map(item => [
                0, 0, {
                    product_id: item.product_id,
                    product_uom_qty: item.quantity,
                    price_unit: item.price,
                }
            ]);
            
            const orderId = await this.call('object', 'execute_kw', [
                this.db, this.uid, this.password,
                'sale.order', 'create',
                [{
                    partner_id: partner[0].id,
                    origin: ecommerceOrder.order_number,
                    order_line: orderLines,
                }]
            ]);
            
            // 3. 确认订单
            await this.call('object', 'execute_kw', [
                this.db, this.uid, this.password,
                'sale.order', 'action_confirm',
                [[orderId]]
            ]);
            
            console.log(`订单同步成功：${ecommerceOrder.order_number} -> ${orderId}`);
            return { status: 'success', odoo_order_id: orderId };
            
        } catch (error) {
            console.error(`订单同步失败：${ecommerceOrder.order_number}`, error);
            return { status: 'error', error: error.message };
        }
    }
}

// 使用示例
(async () => {
    const sync = new EcommerceSync(
        'http://localhost:8069',
        'mydb',
        'admin',
        'admin'
    );
    
    await sync.authenticate();
    
    const ecommerceOrder = {
        order_number: 'ECO-001',
        customer: {
            name: 'John Doe',
            email: 'john@example.com',
            phone: '123456789'
        },
        items: [
            { product_id: 1, quantity: 2, price: 50.0 },
            { product_id: 2, quantity: 1, price: 100.0 }
        ]
    };
    
    const result = await sync.syncOrder(ecommerceOrder);
    console.log('同步结果:', result);
})();
```

---

## PHP 示例

### WordPress WooCommerce 集成

```php
<?php
/**
 * WooCommerce 订单同步到 Odoo
 */

class WooCommerceOdooSync {
    private $odoo_url;
    private $odoo_db;
    private $odoo_uid;
    
    public function __construct($odoo_url, $odoo_db, $odoo_user, $odoo_password) {
        $this->odoo_url = $odoo_url;
        $this->odoo_db = $odoo_db;
        $this->authenticate($odoo_user, $odoo_password);
    }
    
    private function authenticate($username, $password) {
        $payload = [
            'jsonrpc' => '2.0',
            'method' => 'call',
            'params' => [
                'service' => 'common',
                'method' => 'authenticate',
                'args' => [$this->odoo_db, $username, $password, []]
            ],
            'id' => 1
        ];
        
        $response = $this->send($payload);
        $this->odoo_uid = $response['result'];
        
        if (!$this->odoo_uid) {
            throw new Exception('Odoo 认证失败');
        }
    }
    
    private function send($payload) {
        $ch = curl_init($this->odoo_url . '/jsonrpc');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($payload));
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode !== 200) {
            throw new Exception('HTTP 错误：' . $httpCode);
        }
        
        return json_decode($response, true);
    }
    
    private function call($service, $method, $args = [], $kwargs = []) {
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
        
        if (isset($response['error'])) {
            throw new Exception($response['error']['message']);
        }
        
        return $response['result'];
    }
    
    public function syncWooCommerceOrder($wc_order) {
        try {
            // 1. 查找客户
            $partners = $this->call('object', 'execute_kw', [
                $this->odoo_db, $this->odoo_uid, 'admin',
                'res.partner', 'search_read',
                [[('email', '=', $wc_order['customer_email'])]]
            ], ['limit' => 1]);
            
            if (empty($partners)) {
                // 创建客户
                $partner_id = $this->call('object', 'execute_kw', [
                    $this->odoo_db, $this->odoo_uid, 'admin',
                    'res.partner', 'create',
                    [[
                        'name' => $wc_order['customer_name'],
                        'email' => $wc_order['customer_email'],
                        'phone' => $wc_order['customer_phone'],
                    ]]
                ]);
                $partners = [['id' => $partner_id]];
            }
            
            // 2. 创建订单
            $order_lines = [];
            foreach ($wc_order['items'] as $item) {
                $order_lines[] = [0, 0, [
                    'product_id' => $item['product_id'],
                    'product_uom_qty' => $item['quantity'],
                    'price_unit' => $item['price'],
                ]];
            }
            
            $order_id = $this->call('object', 'execute_kw', [
                $this->odoo_db, $this->odoo_uid, 'admin',
                'sale.order', 'create',
                [[
                    'partner_id' => $partners[0]['id'],
                    'origin' => $wc_order['order_number'],
                    'order_line' => $order_lines,
                ]]
            ]);
            
            // 3. 确认订单
            $this->call('object', 'execute_kw', [
                $this->odoo_db, $this->odoo_uid, 'admin',
                'sale.order', 'action_confirm',
                [[$order_id]]
            ]);
            
            return ['status' => 'success', 'odoo_order_id' => $order_id];
            
        } catch (Exception $e) {
            return ['status' => 'error', 'error' => $e->getMessage()];
        }
    }
}

// 使用示例
$sync = new WooCommerceOdooSync(
    'http://localhost:8069',
    'mydb',
    'admin',
    'admin'
);

$wc_order = [
    'order_number' => 'WC-001',
    'customer_name' => 'John Doe',
    'customer_email' => 'john@example.com',
    'customer_phone' => '123456789',
    'items' => [
        ['product_id' => 1, 'quantity' => 2, 'price' => 50.0],
        ['product_id' => 2, 'quantity' => 1, 'price' => 100.0]
    ]
];

$result = $sync->syncWooCommerceOrder($wc_order);
print_r($result);
?>
```

---

## cURL 命令行示例

### 批量导入产品

```bash
#!/bin/bash

# 配置
URL="http://localhost:8069"
DB="mydb"
USER="admin"
PASS="admin"

# 认证
AUTH_RESPONSE=$(curl -s -X POST "$URL/jsonrpc" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"call\",
    \"params\": {
      \"service\": \"common\",
      \"method\": \"authenticate\",
      \"args\": [\"$DB\", \"$USER\", \"$PASS\", {}]
    },
    \"id\": 1
  }")

UID=$(echo $AUTH_RESPONSE | jq -r '.result')
echo "认证成功，UID: $UID"

# 创建产品
curl -X POST "$URL/jsonrpc" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"call\",
    \"params\": {
      \"service\": \"object\",
      \"method\": \"execute_kw\",
      \"args\": [\"$DB\", $UID, \"$PASS\", \"product.product\", \"create\", [{
        \"name\": \"Test Product 1\",
        \"type\": \"product\",
        \"list_price\": 99.99,
        \"standard_price\": 50.00,
        \"default_code\": \"TP-001\"
      }]]
    },
    \"id\": 2
  }" | jq .

# 搜索产品
curl -X POST "$URL/jsonrpc" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"call\",
    \"params\": {
      \"service\": \"object\",
      \"method\": \"execute_kw\",
      \"args\": [\"$DB\", $UID, \"$PASS\", \"product.product\", \"search_read\", [[[]]]],
      \"kwargs\": {\"fields\": [\"name\", \"list_price\"], \"limit\": 10}
    },
    \"id\": 3
  }" | jq .
```

---

## Java 示例

### Maven 依赖

```xml
<dependencies>
    <dependency>
        <groupId>com.redhat.xmlrpc</groupId>
        <artifactId>xmlrpc-client</artifactId>
        <version>3.1.3</version>
    </dependency>
</dependencies>
```

### Java 客户端

```java
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;

import java.net.URL;
import java.util.HashMap;
import java.util.Map;

public class OdooClient {
    private XmlRpcClient commonClient;
    private XmlRpcClient objectClient;
    private String db;
    private int uid;
    
    public OdooClient(String url, String db, String username, String password) throws Exception {
        this.db = db;
        
        // 配置客户端
        XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
        config.setServerURL(new URL(url + "/xmlrpc/2/common"));
        
        commonClient = new XmlRpcClient();
        commonClient.setConfig(config);
        
        config.setServerURL(new URL(url + "/xmlrpc/2/object"));
        objectClient = new XmlRpcClient();
        objectClient.setConfig(config);
        
        // 认证
        authenticate(username, password);
    }
    
    private void authenticate(String username, String password) throws Exception {
        Object[] params = new Object[]{db, username, password, new HashMap<>()};
        uid = (Integer) commonClient.execute("authenticate", params);
        
        if (uid == 0) {
            throw new Exception("认证失败");
        }
        
        System.out.println("认证成功，UID: " + uid);
    }
    
    public Object[] search(String model, Object[] domain) throws Exception {
        Object[] params = new Object[]{
            db, uid, "admin", model, "search", domain
        };
        return (Object[]) objectClient.execute("execute", params);
    }
    
    public Map<String, Object>[] searchRead(String model, Object[] domain, String[] fields) throws Exception {
        Object[] params = new Object[]{
            db, uid, "admin", model, "search_read", domain
        };
        Map<String, Object> kwargs = new HashMap<>();
        kwargs.put("fields", fields);
        
        Object[] allParams = new Object[]{params, kwargs};
        return (Map<String, Object>[]) objectClient.execute("execute_kw", allParams);
    }
    
    public Integer create(String model, Map<String, Object> values) throws Exception {
        Object[] params = new Object[]{
            db, uid, "admin", model, "create", new Object[]{values}
        };
        return (Integer) objectClient.execute("execute", params);
    }
    
    public static void main(String[] args) {
        try {
            OdooClient client = new OdooClient(
                "http://localhost:8069",
                "mydb",
                "admin",
                "admin"
            );
            
            // 搜索客户
            Object[] domain = new Object[]{
                new Object[]{"customer", "=", true}
            };
            Object[] customerIds = client.search("res.partner", domain);
            
            System.out.println("客户数量：" + customerIds.length);
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

---

*参考：Odoo 官方集成指南*
