# Odoo 三层架构详解

## 架构概览

Odoo 采用经典的**三层架构**（Three-Tier Architecture）设计：

```
┌─────────────────────────────────────────────────────────┐
│                    客户端层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Web 浏览器  │  │  移动应用   │  │  POS 客户端  │     │
│  │  (HTML/JS)  │  │  (OWL)      │  │  (Electron) │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │             │
│         └────────────────┼────────────────┘             │
│                          │ HTTP/HTTPS                   │
│                          │ JSON-RPC / XML-RPC          │
├──────────────────────────┼──────────────────────────────┤
│                    应用服务层                            │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Odoo 服务器 (Python)                │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐   │    │
│  │  │  控制器   │  │   ORM     │  │  业务逻辑  │   │    │
│  │  │ (Routes)  │  │ (Models)  │  │ (Methods) │   │    │
│  │  └───────────┘  └───────────┘  └───────────┘   │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐   │    │
│  │  │  安全层   │  │  工作流   │  │   报表    │   │    │
│  │  │ (ACL/Rules)│ │ (Workflow)│ │ (Reports) │   │    │
│  │  └───────────┘  └───────────┘  └───────────┘   │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│                          │ psycopg2                      │
│                          │ (数据库驱动)                   │
├──────────────────────────┼──────────────────────────────┤
│                    数据层                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │            PostgreSQL 数据库                     │    │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐   │    │
│  │  │  业务表   │  │  关系表   │  │  系统表   │   │    │
│  │  │ (Models)  │  │  (Rel)    │  │ (System)  │   │    │
│  │  └───────────┘  └───────────┘  └───────────┘   │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

---

## 第一层：表现层 (Presentation Tier)

### 职责
- 用户界面渲染
- 用户交互处理
- 客户端验证
- 数据展示

### 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **HTML/CSS** | HTML5, CSS3 | 页面结构和样式 |
| **JavaScript 框架** | OWL | Odoo Web Library (v15+) |
| **模板引擎** | QWeb | XML 模板渲染 |
| **构建工具** | Webpack | 资源打包 |

### OWL 框架

OWL (Odoo Web Library) 是 Odoo 自研的前端组件框架。

**核心概念**:
```javascript
import { Component, useState, onMounted } from "@odoo/owl";

class MyComponent extends Component {
    setup() {
        this.state = useState({ count: 0 });
        onMounted(() => {
            console.log('Component mounted');
        });
    }
    
    increment() {
        this.state.count++;
    }
}

MyComponent.template = xml`
    <div>
        <p>Count: <t t-esc="state.count"/></p>
        <button t-on-click="increment">+</button>
    </div>
`;
```

**关键特性**:
- 组件系统
- 响应式状态管理
- 虚拟 DOM
- 生命周期钩子
- 事件处理

### 视图类型

| 视图类型 | 用途 | XML 标签 |
|----------|------|----------|
| Form | 表单视图 | `<form>` |
| Tree/List | 列表视图 | `<tree>` |
| Kanban | 看板视图 | `<kanban>` |
| Graph | 图表视图 | `<graph>` |
| Pivot | 透视表 | `<pivot>` |
| Calendar | 日历视图 | `<calendar>` |
| Search | 搜索视图 | `<search>` |
| Activity | 活动视图 | `<activity>` |

### 示例：表单视图

```xml
<record id="view_sale_order_form" model="ir.ui.view">
    <field name="name">sale.order.form</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <form string="Sales Order">
            <header>
                <button name="action_confirm" type="object" 
                        string="Confirm" class="oe_highlight"/>
                <field name="state" widget="statusbar"/>
            </header>
            <sheet>
                <div class="oe_title">
                    <h1>
                        <field name="name" readonly="1"/>
                    </h1>
                </div>
                <group>
                    <group>
                        <field name="partner_id"/>
                        <field name="date_order"/>
                    </group>
                    <group>
                        <field name="amount_total"/>
                        <field name="state"/>
                    </group>
                </group>
                <notebook>
                    <page string="Order Lines">
                        <field name="order_line">
                            <tree>
                                <field name="product_id"/>
                                <field name="product_uom_qty"/>
                                <field name="price_unit"/>
                                <field name="price_subtotal"/>
                            </tree>
                        </field>
                    </page>
                </notebook>
            </sheet>
        </form>
    </field>
</record>
```

---

## 第二层：逻辑层 (Logic Tier)

### 职责
- 业务逻辑处理
- 数据验证
- 工作流管理
- 权限控制
- API 暴露

### 核心组件

#### 1. 模型 (Models)

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sales Order'
    
    # 字段定义
    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner')
    amount_total = fields.Monetary()
    
    # 业务方法
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
            order._create_picking()
        return True
```

#### 2. 控制器 (Controllers)

```python
from odoo import http
from odoo.http import request

class SaleController(http.Controller):
    
    @http.route('/sales/orders', type='json', auth='user')
    def list_orders(self, **kwargs):
        orders = request.env['sale.order'].search([])
        return orders.read(['name', 'partner_id', 'amount_total'])
    
    @http.route('/sales/order/<int:order_id>', type='json', auth='user')
    def get_order(self, order_id):
        order = request.env['sale.order'].browse(order_id)
        return order.read()[0]
```

#### 3. 工作流 (Workflows)

Odoo 14+ 使用**活动**（Activities）和**状态机**替代旧工作流引擎。

```python
state = fields.Selection([
    ('draft', 'Draft'),
    ('sent', 'Quotation Sent'),
    ('sale', 'Sales Order'),
    ('done', 'Locked'),
    ('cancel', 'Cancelled'),
], default='draft', tracking=True)

def action_confirm(self):
    self.state = 'sale'
    return True
```

#### 4. 安全层 (Security)

```python
# 访问控制
@api.model
def check_access_rights(self, operation, raise_exception=True):
    # 自定义权限检查
    pass

# 记录规则
# 在 XML 中定义 domain 过滤
```

### ORM 装饰器

| 装饰器 | 用途 | 示例 |
|--------|------|------|
| `@api.model` | 模型方法 | `def create(self, vals):` |
| `@api.depends` | 计算字段 | `@api.depends('qty', 'price')` |
| `@api.onchange` | 字段变更 | `@api.onchange('partner_id')` |
| `@api.constrains` | 约束检查 | `@api.constrains('amount')` |
| `@api.model_create_multi` | 批量创建 | `def create(self, vals_list):` |

---

## 第三层：数据层 (Data Tier)

### 职责
- 数据持久化
- 事务管理
- 查询优化
- 索引管理

### PostgreSQL 特性使用

#### 1. 表结构

```sql
-- 自动创建的表
CREATE TABLE sale_order (
    id SERIAL PRIMARY KEY,
    create_uid INTEGER REFERENCES res_users(id),
    create_date TIMESTAMP,
    write_uid INTEGER REFERENCES res_users(id),
    write_date TIMESTAMP,
    name VARCHAR,
    partner_id INTEGER REFERENCES res_partner(id),
    amount_total NUMERIC,
    state VARCHAR
);

-- 索引
CREATE INDEX sale_order_partner_id_idx ON sale_order(partner_id);
CREATE INDEX sale_order_state_idx ON sale_order(state);
```

#### 2. 事务管理

```python
from odoo import tools

@tools.ormcache('arg1')
def cached_method(self, arg1):
    # 缓存方法结果
    pass

# 事务控制
with self.env.cr.savepoint():
    # 自动回滚
    pass
```

#### 3. 查询优化

```python
# 使用 read_group 进行聚合
result = self.env['sale.order'].read_group(
    domain=[('state', '=', 'sale')],
    fields=['partner_id', 'amount_total:sum'],
    groupby=['partner_id']
)

# 使用 SQL 直接查询
self.env.cr.execute("""
    SELECT partner_id, SUM(amount_total) 
    FROM sale_order 
    WHERE state = 'sale'
    GROUP BY partner_id
""")
```

---

## 层间通信

### 1. 前端 → 后端 (HTTP/JSON-RPC)

```javascript
// OWL 组件调用后端
const result = await this.rpc('/web/dataset/call', {
    model: 'sale.order',
    method: 'action_confirm',
    args: [order_id],
    kwargs: {}
});
```

### 2. 外部系统 → 后端 (XML-RPC/JSON-RPC)

```python
# Python 外部调用
import xmlrpc.client

url = 'http://localhost:8069'
db = 'mydb'
username = 'admin'
password = 'admin'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
order_ids = models.execute_kw(db, uid, password,
    'sale.order', 'search', [[]])
```

### 3. 后端 → 数据库 (ORM)

```python
# ORM 自动转换为 SQL
orders = self.env['sale.order'].search([
    ('state', '=', 'sale'),
    ('amount_total', '>', 1000)
], limit=10)

# 生成的 SQL:
# SELECT id FROM sale_order 
# WHERE state = 'sale' AND amount_total > 1000 
# LIMIT 10
```

---

## 部署架构

### 单机部署

```
┌─────────────────┐
│   Nginx (反向代理) │
└────────┬────────┘
         │
┌────────┴────────┐
│  Odoo 服务器     │
│  (Python/WSGI)  │
└────────┬────────┘
         │
┌────────┴────────┐
│  PostgreSQL     │
└─────────────────┘
```

### 集群部署

```
┌─────────────────┐
│   负载均衡器     │
│   (Nginx/HAProxy)│
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───┴───┐ ┌───┴───┐
│Odoo 1 │ │Odoo 2 │  (无状态，可水平扩展)
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         │
┌────────┴────────┐
│  PostgreSQL     │
│  (主从复制)      │
└─────────────────┘
```

---

## 性能考虑

### 表现层优化
- 资源压缩和缓存
- 懒加载
- 虚拟滚动（大数据列表）
- WebSocket 实时通信

### 逻辑层优化
- 使用 `@api.depends` 而非 `@api.onchange`
- 批量操作（`create_multi`）
- 避免 N+1 查询
- 使用 `read_group` 聚合

### 数据层优化
- 适当索引
- 查询分析（EXPLAIN）
- 分区表（大数据量）
- 定期 VACUUM

---

*参考：Odoo 官方开发者文档*
