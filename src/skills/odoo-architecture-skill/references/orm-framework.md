# Odoo ORM 框架

## 概述

Odoo ORM (Object-Relational Mapping) 是 Odoo 的核心组件，提供：
- Python 类 ↔ 数据库表自动映射
- 丰富的字段类型
- 关系管理
- 查询优化
- 自动审计字段

---

## 模型定义

### 基础模型

```python
from odoo import models, fields, api

class SaleOrder(models.Model):
    _name = 'sale.order'
    _description = 'Sales Order'
    
    # 基础字段
    name = fields.Char(string='Reference', required=True)
    date_order = fields.Datetime(string='Order Date', default=fields.Datetime.now)
    amount_total = fields.Monetary(string='Total', currency_field='currency_id')
```

### 模型属性

| 属性 | 说明 | 示例 |
|------|------|------|
| `_name` | 模型名（必需） | `'sale.order'` |
| `_description` | 模型描述 | `'Sales Order'` |
| `_inherit` | 继承的模型 | `'mail.thread'` |
| `_order` | 默认排序 | `'date_order desc'` |
| `_rec_name` | 显示字段 | `'name'` |
| `_table` | 自定义表名 | `'my_sale_order'` |
| `_auto` | 是否创建表 | `True/False` |

---

## 字段类型

### 基础字段

```python
# 文本
name = fields.Char(string='Name', size=50)
description = fields.Text(string='Description')
content = fields.Html(string='Content')

# 数值
qty = fields.Integer(string='Quantity')
price = fields.Float(string='Price', digits=(10, 2))
amount = fields.Monetary(string='Amount', currency_field='currency_id')

# 日期
date = fields.Date(string='Date')
datetime = fields.Datetime(string='Datetime')

# 布尔
active = fields.Boolean(string='Active', default=True)

# 选择
state = fields.Selection([
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed'),
    ('done', 'Done'),
], string='Status', default='draft')

# 二进制 (文件)
attachment = fields.Binary(string='Attachment')
```

### 字段参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `string` | 显示标签 | 字段名 |
| `required` | 是否必填 | `False` |
| `default` | 默认值 | `None` |
| `readonly` | 只读 | `False` |
| `invisible` | 隐藏 | `False` |
| `help` | 提示信息 | `''` |
| `tracking` | 跟踪变更 | `False` |
| `index` | 添加索引 | `False` |

---

## 关系字段

### Many2one (多对一)

```python
# 外键关系
partner_id = fields.Many2one(
    'res.partner',
    string='Customer',
    required=True,
    ondelete='cascade',  # cascade, restrict, set null
    domain="[('customer', '=', True)]",
    context={'default_customer': True}
)

# SQL: partner_id INTEGER REFERENCES res_partner(id)
```

### One2many (一对多)

```python
# 反向关系 (不创建数据库列)
order_line = fields.One2many(
    'sale.order.line',  # 关联模型
    'order_id',         # 关联字段
    string='Order Lines',
    limit=100
)

# SQL: 在 sale_order_line 表创建 order_id 列
```

### Many2many (多对多)

```python
# 自动创建关联表
tag_ids = fields.Many2many(
    'sale.tag',                    # 关联模型
    string='Tags',
    relation='sale_order_tag_rel', # 关联表名 (可选)
    column1='order_id',            # 本模型列名 (可选)
    column2='tag_id',              # 关联模型列名 (可选)
    domain="[('active', '=', True)]"
)

# SQL: 创建 sale_order_tag_rel(order_id, tag_id)
```

---

## 计算字段

### 基础计算

```python
amount_untaxed = fields.Monetary(
    string='Untaxed Amount',
    compute='_compute_amounts',
    store=True  # 存储到数据库
)

@api.depends('order_line.price_subtotal')
def _compute_amounts(self):
    for order in self:
        order.amount_untaxed = sum(
            line.price_subtotal for line in order.order_line
        )
```

### 带逆计算

```python
amount_total = fields.Monetary(
    compute='_compute_amounts',
    store=True,
    inverse='_inverse_amount_total'
)

def _inverse_amount_total(self):
    # 当用户修改 amount_total 时触发
    for order in self:
        # 调整行项目
        pass
```

### 相关字段

```python
# 直接获取关联字段值
partner_name = fields.Char(
    related='partner_id.name',
    string='Customer Name',
    store=True
)
```

---

## 约束

### Python 约束

```python
from odoo.exceptions import ValidationError

@api.constrains('amount_total')
def _check_amount(self):
    for record in self:
        if record.amount_total < 0:
            raise ValidationError('Amount cannot be negative')

@api.constrains('date_order', 'date_delivery')
def _check_dates(self):
    for record in self:
        if record.date_order > record.date_delivery:
            raise ValidationError('Order date must be before delivery date')
```

### SQL 约束

```python
_sql_constraints = [
    ('name_uniq', 'unique (name)', 'Order reference must be unique!'),
    ('amount_positive', 'CHECK (amount_total >= 0)', 'Amount must be positive!'),
]
```

---

## ORM 方法

### CRUD 操作

```python
# 创建
record = self.env['sale.order'].create({
    'name': 'SO001',
    'partner_id': 1,
})

# 读取
record = self.env['sale.order'].browse(1)
records = self.env['sale.order'].search([('state', '=', 'draft')])

# 更新
record.write({'state': 'confirmed'})
record.state = 'confirmed'  # 简写

# 删除
record.unlink()

# 复制
new_record = record.copy(default={'name': 'SO002'})
```

### 搜索方法

```python
# 基础搜索
records = self.env['sale.order'].search([
    ('state', '=', 'draft'),
    ('amount_total', '>', 1000),
    ('partner_id', 'in', [1, 2, 3]),
], order='date_order desc', limit=10)

# 搜索计数
count = self.env['sale.order'].search_count([('state', '=', 'draft')])

# 域名操作符
# =, !=, >, <, >=, <=, =like, like, ilike, in, not in, child_of
```

### 读取数据

```python
# 读取特定字段
data = records.read(['name', 'partner_id', 'amount_total'])

# 读取所有字段
data = records.read()

# 读取关联字段 (自动 JOIN)
data = records.read(['partner_id', 'partner_id.name', 'partner_id.email'])
```

---

## 高级功能

### 记录集操作

```python
# 并集
all_records = records1 | records2

# 交集
common = records1 & records2

# 差集
diff = records1 - records2

# 过滤
draft_orders = records.filtered(lambda r: r.state == 'draft')

# 排序
sorted_records = records.sorted(key=lambda r: r.amount_total, reverse=True)

# 分组
by_partner = records.grouped(lambda r: r.partner_id)
```

### 事务管理

```python
# 自动回滚
with self.env.cr.savepoint():
    # 如果出错，自动回滚
    record.action_confirm()

# 手动提交
self.env.cr.commit()  # 谨慎使用!
```

### 缓存管理

```python
# 清除缓存
self.env.clear()

# 刷新数据
record.invalidate_recordset()
```

---

## 性能优化

### 避免 N+1 查询

```python
# ❌ 不推荐：N+1 问题
for order in orders:
    print(order.partner_id.name)  # 每次访问都查询

# ✅ 推荐：预读取
orders = self.env['sale.order'].search([])
orders.read(['partner_id'])  # 预加载
for order in orders:
    print(order.partner_id.name)  # 使用缓存
```

### 批量操作

```python
# ❌ 不推荐：循环创建
for vals in vals_list:
    self.env['sale.order'].create(vals)

# ✅ 推荐：批量创建
self.env['sale.order'].create(vals_list)

# ❌ 不推荐：循环写入
for record in records:
    record.state = 'done'

# ✅ 推荐：批量写入
records.write({'state': 'done'})
```

### 使用 read_group

```python
# ❌ 不推荐：Python 聚合
total = sum(order.amount_total for order in orders)

# ✅ 推荐：数据库聚合
result = self.env['sale.order'].read_group(
    domain=[('state', '=', 'sale')],
    fields=['amount_total:sum'],
    groupby=[]
)
total = result[0]['amount_total'] if result else 0
```

---

## 调试技巧

### SQL 日志

```python
# 查看生成的 SQL
self.env.cr.execute("SELECT * FROM sale_order WHERE id = %s", (1,))
print(self.env.cr.mogrify("SELECT * FROM sale_order WHERE id = %s", (1,)))
```

### ORM 调试

```python
# 查看查询
import logging
_logger = logging.getLogger(__name__)

# 启用 ORM 调试
# 启动时添加：--log-level=debug_orm

# 打印查询
for record in records:
    _logger.info('Record: %s', record.name)
```

---

*参考：Odoo 官方 ORM 文档*
