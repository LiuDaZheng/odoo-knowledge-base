---
name: odoo-inventory
description: Odoo 库存管理 Skill - 查询库存、创建调拨、管理仓库操作
version: 0.1.0
metadata:
  openclaw:
    version: "1.0"
  author: OpenClaw Agent
  created: 2026-04-12
  tags:
    - odoo
    - inventory
    - erp
    - stock
    - warehouse
triggers:
  - odoo 库存
  - odoo 查询库存
  - odoo 创建调拨
  - odoo 入库
  - odoo 出库
  - odoo 库存调整
  - 查询 odoo 产品
  - odoo 仓库管理
  - stock query
  - odoo inventory
  - create transfer
  - odoo stock
---

# Odoo 库存管理 Skill

## 功能概述

本 Skill 提供与 Odoo ERP 库存管理模块的集成，支持以下核心功能：

1. **库存查询** - 查询产品库存数量、库位分布
2. **调拨管理** - 创建入库、出库、内部调拨单
3. **库存调整** - 执行盘点、处理报废
4. **产品管理** - 查询产品信息、产品类别

## 配置要求

使用前需要在 Feishu 中配置以下环境变量：

```yaml
ODOO_BASE_URL: https://your-company.odoo.com
ODOO_API_KEY: your_api_key_here
ODOO_DATABASE: your_database_name
```

## 使用示例

### 查询产品库存

```
查询 odoo 产品 笔记本电脑 的库存
odoo 查询库存 产品 ID 10
```

### 创建入库单

```
odoo 入库 供应商 A 产品 ID 10 数量 100
创建 odoo 入库单 产品 笔记本电脑 数量 50
```

### 创建出库单

```
odoo 出库 客户 B 产品 ID 10 数量 20
创建 odoo 出库单 订单号 SO001 产品 鼠标 数量 10
```

### 库存调整

```
odoo 库存调整 产品 ID 10 实际数量 95 原因 盘点差异
```

## 核心操作

### 库存查询

- `get_stock_quantity(product_id, location_id=None)` - 查询产品库存
- `get_available_stock(product_id)` - 查询可用库存 (扣除预留)
- `get_stock_moves(product_id, date_from, date_to)` - 查询库存移动历史
- `get_picking_by_origin(origin)` - 根据来源单号查询调拨单

### 调拨管理

- `create_incoming_picking(partner_id, product_lines)` - 创建入库单
- `create_outgoing_picking(partner_id, product_lines, origin)` - 创建出库单
- `create_internal_transfer(from_location, to_location, product_lines)` - 内部调拨
- `validate_picking(picking_id)` - 验证调拨单
- `cancel_picking(picking_id)` - 取消调拨单

### 库存调整

- `create_inventory_adjustment(product_id, counted_quantity, location_id)` - 创建调整单
- `apply_inventory_adjustment(inventory_id)` - 应用调整
- `create_scrap(product_id, quantity, reason)` - 创建报废单

## API 参考

### 数据模型

| 模型 | 说明 | 主要字段 |
|-----|------|---------|
| `stock.quant` | 库存数量 | `product_id`, `location_id`, `quantity`, `reserved_quantity` |
| `stock.picking` | 调拨单 | `picking_type_id`, `origin`, `state`, `move_lines` |
| `stock.move` | 库存移动 | `product_id`, `product_uom_qty`, `picking_id`, `state` |
| `product.product` | 产品 | `name`, `type`, `uom_id`, `categ_id` |

### 状态码

| 状态 | 说明 |
|-----|------|
| `draft` | 草稿 |
| `waiting` | 等待可用 |
| `confirmed` | 已确认 |
| `assigned` | 已分配 (有库存) |
| `done` | 已完成 |
| `cancel` | 已取消 |

## 错误处理

### 常见错误

| 错误码 | 说明 | 解决方案 |
|-------|------|---------|
| `INSUFFICIENT_STOCK` | 库存不足 | 检查可用库存，调整数量 |
| `INVALID_PRODUCT` | 产品不存在 | 验证产品 ID |
| `INVALID_LOCATION` | 库位不存在 | 验证库位 ID |
| `PICKING_LOCKED` | 调拨单已锁定 | 无法修改已验证的调拨单 |

## 最佳实践

1. **库存查询**: 使用 `get_available_stock` 而非 `get_stock_quantity`，避免分配冲突
2. **批量操作**: 多个产品使用批量 API，减少网络往返
3. **状态检查**: 操作前检查调拨单状态，避免无效操作
4. **错误重试**: 网络错误实现指数退避重试
5. **日志记录**: 记录所有 API 调用，便于审计

## 依赖

- `requests` - HTTP 客户端
- `python-dateutil` - 日期处理

## 测试

```bash
# 运行单元测试
pytest tests/test_inventory.py

# 运行集成测试 (需要 Odoo 测试环境)
pytest tests/test_integration.py --odoo-url=https://test.odoo.com
```

## 版本历史

| 版本 | 日期 | 变更 |
|-----|------|------|
| 0.1.0 | 2026-04-12 | 初始版本，基础库存查询和调拨功能 |

## 待开发功能

- [ ] 批次/序列号管理
- [ ] 多仓库支持
- [ ] 补货规则管理
- [ ] 库存预测
- [ ] 条形码扫描集成
