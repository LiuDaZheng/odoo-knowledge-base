---
name: odoo-sales-skill
description: >
  Odoo 销售流程 Skill。管理报价、订单、价格策略和销售分析。
  支持销售报价单创建、订单确认、价格表配置、销售报表等核心功能。
  Use when: (1) 创建销售报价，(2) 管理销售订单，(3) 配置价格策略，
  (4) 分析销售数据，(5) 跟踪订单状态，(6) 生成销售报表。
---

# Odoo Sales Skill

管理 Odoo 销售核心业务：报价、订单、价格策略和销售分析。

## 📖 功能概览

| 功能模块 | 描述 | API 端点 |
|---------|------|---------|
| **报价管理** | 创建、发送、确认销售报价 | `/sale/quotations` |
| **订单管理** | 订单确认、发货、开票 | `/sale/orders` |
| **价格策略** | 价格表、折扣、促销 | `/product/pricelist` |
| **销售分析** | 销售报表、业绩分析 | `/sale/report` |

## 🚀 快速开始

### 前置条件

1. **Odoo 实例**: Odoo v16.0+
2. **API 访问**: 配置 API Key 或 OAuth
3. **权限**: 销售模块访问权限

### 配置认证

```bash
export ODOO_URL="https://your-company.odoo.com"
export ODOO_DB="your_database"
export ODOO_API_KEY="your_api_key"
```

## 📋 核心功能

### 1. 报价管理 (Quotations)

#### 创建报价

```bash
python3 {baseDir}/scripts/sales.py quotation create \
  --partner_id 123 \
  --validity_days 30 \
  --lines "Product A:10:100,Product B:5:200" \
  --notes "标准交货期：2 周"
```

**参数说明**:
- `--partner_id`: 客户 ID（必需）
- `--validity_days`: 报价有效期（天）
- `--lines`: 产品明细（产品：数量：单价）
- `--notes`: 备注

#### 查看报价

```bash
# 查看所有报价
python3 {baseDir}/scripts/sales.py quotation list

# 按状态筛选
python3 {baseDir}/scripts/sales.py quotation list --state draft

# 按客户筛选
python3 {baseDir}/scripts/sales.py quotation list --partner_id 123
```

#### 发送报价

```bash
python3 {baseDir}/scripts/sales.py quotation send <quotation_id> \
  --email "customer@example.com" \
  --subject "报价单 - 某某项目"
```

#### 确认报价

```bash
python3 {baseDir}/scripts/sales.py quotation confirm <quotation_id>
```

### 2. 订单管理 (Orders)

#### 创建订单

```bash
python3 {baseDir}/scripts/sales.py order create \
  --partner_id 123 \
  --lines "Product A:10:100,Product B:5:200" \
  --warehouse_id 1 \
  --commitment_date "2026-05-30"
```

#### 查看订单

```bash
# 查看所有订单
python3 {baseDir}/scripts/sales.py order list

# 按状态筛选
python3 {baseDir}/scripts/sales.py order list --state sale

# 查看订单详情
python3 {baseDir}/scripts/sales.py order get <order_id>
```

#### 订单发货

```bash
python3 {baseDir}/scripts/sales.py order deliver <order_id>
```

#### 创建发票

```bash
python3 {baseDir}/scripts/sales.py order invoice <order_id>
```

### 3. 价格策略 (Pricelists)

#### 查看价格表

```bash
python3 {baseDir}/scripts/sales.py pricelist list
```

#### 创建价格表

```bash
python3 {baseDir}/scripts/sales.py pricelist create \
  --name "VIP 客户价格表" \
  --currency_id 1 \
  --discount_policy "without_discount"
```

#### 添加价格表项目

```bash
python3 {baseDir}/scripts/sales.py pricelist add-item <pricelist_id> \
  --product_id 456 \
  --fixed_price 88.00 \
  --min_quantity 10
```

### 4. 销售分析 (Analysis)

#### 销售报表

```bash
# 按产品分析
python3 {baseDir}/scripts/sales.py report by-product \
  --date_from "2026-01-01" \
  --date_to "2026-04-12"

# 按客户分析
python3 {baseDir}/scripts/sales.py report by-customer \
  --date_from "2026-01-01" \
  --date_to "2026-04-12"

# 按销售员分析
python3 {baseDir}/scripts/sales.py report by-salesperson \
  --date_from "2026-01-01" \
  --date_to "2026-04-12"
```

#### 销售漏斗

```bash
python3 {baseDir}/scripts/sales.py report funnel
```

## 🔧 脚本说明

### sales.py

主脚本文件，提供所有销售功能。

**位置**: `{baseDir}/scripts/sales.py`

**用法**:
```bash
python3 sales.py <module> <action> [options]
```

**模块**:
- `quotation`: 报价管理
- `order`: 订单管理
- `pricelist`: 价格策略
- `report`: 销售分析

## 📁 目录结构

```
odoo-sales-skill/
├── SKILL.md
├── _meta.json
├── .clawhub/
│   └── origin.json
├── references/
│   ├── api-reference.md
│   ├── workflow.md
│   └── best-practices.md
└── scripts/
    ├── sales.py
    ├── odoo_client.py
    └── utils.py
```

## 🎯 最佳实践

### 报价管理

1. **及时响应**: 客户询价后 24 小时内提供报价
2. **明确有效期**: 所有报价必须设置有效期
3. **详细明细**: 报价单包含完整产品明细和条款
4. **跟进记录**: 记录所有报价跟进情况

### 订单管理

1. **准确录入**: 确保订单信息准确无误
2. **及时确认**: 收到订单后及时确认
3. **进度跟踪**: 实时更新订单状态
4. **异常处理**: 及时处理订单异常

### 价格策略

1. **统一标准**: 建立统一的价格体系
2. **分级管理**: 根据客户等级设置不同价格
3. **定期审核**: 定期审核和更新价格
4. **权限控制**: 价格修改需审批

## ⚠️ 注意事项

1. **库存检查**: 确认订单前检查库存
2. **信用控制**: 检查客户信用额度
3. **价格审批**: 特价需审批
4. **合同管理**: 大金额订单需签合同

## 🔗 相关资源

- [Odoo 销售官方文档](https://www.odoo.com/documentation/16.0/applications/sales/sales.html)
- [references/api-reference.md](references/api-reference.md) - API 参考
- [references/workflow.md](references/workflow.md) - 工作流程
- [references/best-practices.md](references/best-practices.md) - 最佳实践

## 📝 更新日志

### v0.1.0 (2026-04-12)
- 初始版本
- 报价管理功能
- 订单管理功能
- 价格策略功能
- 销售分析功能

---

*Skill 版本：v0.1.0*
*Odoo 兼容版本：16.0+*
*最后更新：2026-04-12*
