---
name: odoo-ecommerce-skill
description: Odoo 电商功能 Skill - 提供产品目录管理、购物车管理、订单管理、支付集成 (支付宝/微信/信用卡)、订单履行 (处理/发货/退货) 功能。Use when working with Odoo eCommerce modules for: (1) Product catalog management, (2) Shopping cart operations, (3) Order processing and fulfillment, (4) Payment gateway integration, (5) Returns and refunds.
---

# Odoo 电商功能 Skill

## 快速开始

### 使用 Odoo XML-RPC API

```python
from scripts.odoo_client import create_client

client = create_client()

# 创建电商产品
product_id = client.create('product.template', {
    'name': '产品 A',
    'type': 'product',
    'list_price': 99.99,
    'standard_price': 50.00,
    'website_published': True,
    'website_sequence': 1,
    'description_sale': '产品描述',
})

# 查询订单
domain = [['state', 'in', ['sale', 'done']]]
orders = client.search_read('sale.order', domain, fields=['name', 'partner_id', 'amount_total'], limit=20)

# 创建发货单
picking_id = client.create('stock.picking', {
    'picking_type_id': 1,
    'partner_id': partner_id,
    'location_id': stock_location_id,
    'location_dest_id': customer_location_id,
    'move_ids': [(0, 0, {
        'name': '发货',
        'product_id': product_id,
        'product_uom_qty': qty,
    })],
})
```

## 核心功能

### 1. 产品目录管理

#### 创建电商产品

```python
product_id = client.create('product.template', {
    'name': '产品 A',
    'type': 'product',
    'list_price': 99.99,
    'standard_price': 50.00,
    'website_published': True,
    'website_sequence': 1,
    'description_sale': '产品描述',
})
```

### 2. 购物车管理

```python
# 添加到购物车
cart_id = client.create('sale.order', {
    'partner_id': partner_id,
    'order_line': [
        (0, 0, {
            'product_id': product_id,
            'product_uom_qty': 2,
            'price_unit': 99.99,
        }),
    ],
})
```

### 3. 订单管理

#### 查询订单

```python
domain = [['state', 'in', ['sale', 'done']]]
orders = client.search_read('sale.order', domain, fields=['name', 'partner_id', 'amount_total'])
```

#### 订单确认

```python
client.execute('sale.order', 'action_confirm', [[order_id]])
```

### 4. 支付集成

#### 支付宝集成

```python
# 配置支付宝支付提供商
provider_id = client.create('payment.provider', {
    'name': 'Alipay',
    'provider': 'alipay',
    'state': 'enabled',
})
```

### 5. 订单履行

#### 创建发货单

```python
picking_id = client.create('stock.picking', {
    'picking_type_id': picking_type_id,
    'partner_id': partner_id,
    'location_id': stock_location_id,
    'location_dest_id': customer_location_id,
    'move_ids': [
        (0, 0, {
            'name': '发货',
            'product_id': product_id,
            'product_uom_qty': qty,
        }),
    ],
})
```

#### 处理退货

```python
# 创建退货
return_picking_id = client.create('stock.picking', {
    'picking_type_id': return_picking_type_id,
    'partner_id': partner_id,
    'location_id': customer_location_id,
    'location_dest_id': stock_location_id,
    'move_ids': [(0, 0, {...})],
})
```

## 最佳实践

- 优化产品页面
- 简化结账流程
- 提供多种支付方式
- 及时处理订单

## 支持的 Odoo 版本

- Odoo 16.0 LTS
- Odoo 17.0 LTS
- Odoo 18.0 (最新)
