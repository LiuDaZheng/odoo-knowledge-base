---
name: odoo-purchase-skill
description: >
  Odoo 采购流程 Skill。管理供应商、采购订单和采购分析。
  支持供应商管理、采购申请、采购订单、收货对账等核心功能。
  Use when: (1) 管理供应商信息，(2) 创建采购订单，(3) 跟踪采购进度，
  (4) 处理采购收货，(5) 进行采购对账，(6) 生成采购报表。
---

# Odoo Purchase Skill

管理 Odoo 采购核心业务：供应商、采购订单、采购分析。

## 📖 功能概览

| 功能模块 | 描述 | API 端点 |
|---------|------|---------|
| **供应商管理** | 供应商信息、评估、分类 | `/purchase/vendors` |
| **采购申请** | 需求申请、审批流程 | `/purchase/requisition` |
| **采购订单** | 订单创建、确认、跟踪 | `/purchase/orders` |
| **采购分析** | 采购报表、供应商分析 | `/purchase/report` |

## 🚀 快速开始

### 前置条件

1. **Odoo 实例**: Odoo v16.0+
2. **API 访问**: 配置 API Key
3. **权限**: 采购模块访问权限

### 配置认证

```bash
export ODOO_URL="https://your-company.odoo.com"
export ODOO_DB="your_database"
export ODOO_API_KEY="your_api_key"
```

## 📋 核心功能

### 1. 供应商管理 (Vendors)

#### 创建供应商

```bash
python3 {baseDir}/scripts/purchase.py vendor create \
  --name "某某供应商有限公司" \
  --email "sales@vendor.com" \
  --phone "+86 10 8888 8888" \
  --website "https://www.vendor.com"
```

#### 查看供应商

```bash
python3 {baseDir}/scripts/purchase.py vendor list
python3 {baseDir}/scripts/purchase.py vendor search --query "某某"
```

#### 供应商评估

```bash
python3 {baseDir}/scripts/purchase.py vendor rate <vendor_id> \
  --quality 4 \
  --delivery 5 \
  --service 4
```

### 2. 采购申请 (Requisition)

#### 创建采购申请

```bash
python3 {baseDir}/scripts/purchase.py requisition create \
  --origin "生产需求" \
  --lines "Product A:100,Product B:50" \
  --date_deadline "2026-05-01"
```

#### 审批采购申请

```bash
python3 {baseDir}/scripts/purchase.py requisition approve <requisition_id>
```

### 3. 采购订单 (Orders)

#### 创建采购订单

```bash
python3 {baseDir}/scripts/purchase.py order create \
  --partner_id 123 \
  --lines "Product A:100:10,Product B:50:20" \
  --date_planned "2026-04-30"
```

#### 查看采购订单

```bash
python3 {baseDir}/scripts/purchase.py order list
python3 {baseDir}/scripts/purchase.py order list --state purchase
```

#### 确认采购订单

```bash
python3 {baseDir}/scripts/purchase.py order confirm <order_id>
```

### 4. 采购收货 (Receipt)

#### 创建收货单

```bash
python3 {baseDir}/scripts/purchase.py receipt create <order_id>
```

#### 确认收货

```bash
python3 {baseDir}/scripts/purchase.py receipt validate <picking_id>
```

### 5. 采购分析 (Analysis)

#### 采购报表

```bash
python3 {baseDir}/scripts/purchase.py report by-vendor \
  --date_from "2026-01-01" \
  --date_to "2026-04-12"
```

#### 采购支出分析

```bash
python3 {baseDir}/scripts/purchase.py report spend-analysis
```

## 🔧 脚本说明

### purchase.py

主脚本文件，提供所有采购功能。

**位置**: `{baseDir}/scripts/purchase.py`

**用法**:
```bash
python3 purchase.py <module> <action> [options]
```

**模块**:
- `vendor`: 供应商管理
- `requisition`: 采购申请
- `order`: 采购订单
- `receipt`: 采购收货
- `report`: 采购分析

## 📁 目录结构

```
odoo-purchase-skill/
├── SKILL.md
├── _meta.json
├── .clawhub/
│   └── origin.json
├── references/
│   ├── api-reference.md
│   └── best-practices.md
└── scripts/
    ├── purchase.py
    └── odoo_client.py
```

## 🎯 最佳实践

### 供应商管理

1. **资质审核**: 新供应商必须资质审核
2. **定期评估**: 每季度评估供应商绩效
3. **分级管理**: ABC 分类管理供应商
4. **备选方案**: 关键物料至少 2 家供应商

### 采购订单

1. **价格比较**: 大额采购需三方比价
2. **合同管理**: 大金额订单需签合同
3. **交期跟踪**: 定期跟踪订单交期
4. **质量检验**: 收货后质量检验

### 采购分析

1. **支出分析**: 月度采购支出分析
2. **价格趋势**: 跟踪关键物料价格趋势
3. **供应商绩效**: 定期评估供应商绩效
4. **成本优化**: 持续优化采购成本

## ⚠️ 注意事项

1. **审批流程**: 按金额执行审批流程
2. **预算管理**: 控制在预算范围内
3. **合规要求**: 遵守采购合规要求
4. **风险管理**: 识别和管控采购风险

## 🔗 相关资源

- [Odoo 采购官方文档](https://www.odoo.com/documentation/16.0/applications/purchase.html)

## 📝 更新日志

### v0.1.0 (2026-04-12)
- 初始版本
- 供应商管理
- 采购订单
- 采购收货
- 采购分析

---

*Skill 版本：v0.1.0*
*Odoo 兼容版本：16.0+*
*最后更新：2026-04-12*
