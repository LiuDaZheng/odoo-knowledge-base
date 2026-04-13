---
name: odoo-inventory-skill
description: >
  Odoo 库存管理 Skill。管理入库、出库、库存调拨和库存盘点。
  支持库存转移、库存调整、库存查询、库存报表等核心功能。
  Use when: (1) 管理入库出库，(2) 执行库存调拨，(3) 进行库存盘点，
  (4) 查询库存数量，(5) 生成库存报表，(6) 跟踪库存移动。
---

# Odoo Inventory Skill

管理 Odoo 库存核心业务：入库、出库、调拨、盘点。

## 📖 功能概览

| 功能模块 | 描述 | API 端点 |
|---------|------|---------|
| **入库管理** | 采购入库、生产入库、退货入库 | `/stock/incoming` |
| **出库管理** | 销售出库、领料出库、退货出库 | `/stock/outgoing` |
| **库存调拨** | 仓库间调拨、库位间调拨 | `/stock/transfers` |
| **库存盘点** | 定期盘点、循环盘点、差异调整 | `/stock/inventory` |

## 🚀 快速开始

### 前置条件

1. **Odoo 实例**: Odoo v16.0+
2. **API 访问**: 配置 API Key
3. **权限**: 库存模块访问权限

### 配置认证

```bash
export ODOO_URL="https://your-company.odoo.com"
export ODOO_DB="your_database"
export ODOO_API_KEY="your_api_key"
```

## 📋 核心功能

### 1. 入库管理 (Incoming)

#### 创建入库单

```bash
python3 {baseDir}/scripts/inventory.py incoming create \
  --partner_id 123 \
  --warehouse_id 1 \
  --lines "Product A:10,Product B:20" \
  --scheduled_date "2026-04-15"
```

#### 查看入库单

```bash
python3 {baseDir}/scripts/inventory.py incoming list
python3 {baseDir}/scripts/inventory.py incoming list --state draft
```

#### 确认入库

```bash
python3 {baseDir}/scripts/inventory.py incoming validate <picking_id>
```

### 2. 出库管理 (Outgoing)

#### 创建出库单

```bash
python3 {baseDir}/scripts/inventory.py outgoing create \
  --partner_id 123 \
  --warehouse_id 1 \
  --lines "Product A:5,Product B:10"
```

#### 查看出库单

```bash
python3 {baseDir}/scripts/inventory.py outgoing list
python3 {baseDir}/scripts/inventory.py outgoing list --state assigned
```

#### 确认出库

```bash
python3 {baseDir}/scripts/inventory.py outgoing validate <picking_id>
```

### 3. 库存调拨 (Transfers)

#### 创建调拨单

```bash
python3 {baseDir}/scripts/inventory.py transfer create \
  --location_src_id 10 \
  --location_dest_id 20 \
  --lines "Product A:100,Product B:50"
```

#### 查看调拨单

```bash
python3 {baseDir}/scripts/inventory.py transfer list
```

### 4. 库存盘点 (Inventory Adjustment)

#### 创建盘点单

```bash
python3 {baseDir}/scripts/inventory.py adjustment create \
  --location_id 10 \
  --products "Product A,Product B"
```

#### 应用盘点

```bash
python3 {baseDir}/scripts/inventory.py adjustment apply <inventory_id>
```

### 5. 库存查询 (Stock Query)

#### 查询库存数量

```bash
python3 {baseDir}/scripts/inventory.py stock query \
  --product_id 456 \
  --location_id 10
```

#### 查看库存报表

```bash
python3 {baseDir}/scripts/inventory.py stock report
```

## 🔧 脚本说明

### inventory.py

主脚本文件，提供所有库存功能。

**位置**: `{baseDir}/scripts/inventory.py`

**用法**:
```bash
python3 inventory.py <module> <action> [options]
```

**模块**:
- `incoming`: 入库管理
- `outgoing`: 出库管理
- `transfer`: 库存调拨
- `adjustment`: 库存盘点
- `stock`: 库存查询

## 📁 目录结构

```
odoo-inventory-skill/
├── SKILL.md
├── _meta.json
├── .clawhub/
│   └── origin.json
├── references/
│   ├── api-reference.md
│   └── best-practices.md
└── scripts/
    ├── inventory.py
    └── odoo_client.py
```

## 🎯 最佳实践

### 入库管理

1. **及时验收**: 货物到达后及时验收
2. **准确录入**: 确保入库数量准确
3. **质量检查**: 执行质量检验流程
4. **及时上架**: 验收后及时上架

### 出库管理

1. **先进先出**: 遵循 FIFO 原则
2. **准确拣货**: 按订单准确拣货
3. **及时发货**: 确认后及时发货
4. **包装规范**: 按标准包装

### 库存管理

1. **定期盘点**: 每月/季度盘点
2. **差异分析**: 分析盘点差异原因
3. **安全库存**: 设置合理安全库存
4. **库位优化**: 优化库位布局

## ⚠️ 注意事项

1. **库存锁定**: 确保库存充足再确认订单
2. **批次管理**: 需要批次的产品严格管理
3. **有效期管理**: 注意产品有效期
4. **权限控制**: 库存调整需审批

## 🔗 相关资源

- [Odoo 库存官方文档](https://www.odoo.com/documentation/16.0/applications/inventory_and_mrp/inventory.html)

## 📝 更新日志

### v0.1.0 (2026-04-12)
- 初始版本
- 入库出库管理
- 库存调拨
- 库存盘点
- 库存查询

---

*Skill 版本：v0.1.0*
*Odoo 兼容版本：16.0+*
*最后更新：2026-04-12*
