# Odoo 核心模块关系总览

## ER 总览图

```mermaid
erDiagram
    crm_lead ||--o{ sale_order : "线索转化"
    sale_order ||--o{ account_move : "开票"
    sale_order ||--o{ stock_picking : "出货"
    stock_picking ||--o{ stock_quant : "库存"
    purchase_order ||--o{ stock_picking : "入库"
    purchase_order ||--o{ account_move : "供应商账单"
    product_template ||--o{ sale_order_line : "销售行"
    product_template ||--o{ purchase_order_line : "采购行"
    product_template ||--|| stock_quant : "库存"
    mrp_production ||--o{ stock_move : "生产领料/入库"
    mrp_bom ||--|| mrp_production : "物料清单"
    product_template ||--|| mrp_bom : "BOM清单"

    crm_lead {
        int id PK
        string name
        string type "lead/opportunity"
        int partner_id FK
        string stage_id
        string priority
        float planned_revenue
    }

    sale_order {
        int id PK
        string name
        int partner_id FK
        string state
        float amount_total
        datetime date_order
    }

    purchase_order {
        int id PK
        string name
        int partner_id FK "供应商"
        string state
        float amount_total
    }

    account_move {
        int id PK
        string name
        string type "out_invoice/in_invoice/..."
        int partner_id FK
        float amount_total
        string state "draft/post/paid"
    }

    stock_picking {
        int id PK
        string name
        string state
        string picking_type "incoming/outgoing"
        int partner_id FK
    }

    stock_quant {
        int id PK
        int product_id FK
        int location_id FK
        float quantity
    }

    mrp_production {
        int id PK
        string name
        string state
        int product_id FK
        float product_qty
    }

    product_template {
        int id PK
        string name
        string type
        float list_price
        float standard_price
    }
}
```

## 模块间数据流动

### CRM → Sales（线索转报价）

```
crm.lead (type=opportunity)
    │ (action_quotations_new)
    ▼
sale.order (自动填充客户/产品/金额)
    │ (state=draft → sent → sale)
    ▼
sale.order.line (产品明细)
```

**关键字段**:
- `crm_lead.partner_id` → `sale_order.partner_id`
- `crm_lead.planned_revenue` → `sale_order.amount_total`（参考）
- 报价确认后，crm_lead.state 变为 `won`

### Sales → Inventory（销售触发出货）

```
sale.order (state=sale)
    │ 自动创建
    ▼
stock.picking (picking_type=outgoing)
    │ (confirm → assigned → done)
    ▼
stock.move (从库存位置到客户地址)
    │ 完成后
    ▼
stock.quant (库存扣减)
```

**关键触发**:
- `sale.order` 确认后立即生成 `stock.picking`（草稿状态）
- 仓库人员确认 picking，系统自动预留 `stock.quant`
- picking done → 实际库存 `quantity` 扣减

### Sales → Accounting（销售开票）

```
sale.order (state=sale)
    │ 创建发票按钮 或 自动发票
    ▼
account.move (type=out_invoice)
    │ (draft → posted → paid)
    ▼
account.move.line (应收明细行)
```

**关键字段**:
- `account_move.partner_id` → 客户
- `account_move.invoice_date` → 开票日期
- 客户付款后 → `account_payment` 创建 → 核销 `account_move`

### Purchase → Inventory（采购入库）

```
purchase.order (state=purchase)
    │ 确认采购
    ▼
stock.picking (picking_type=incoming)
    │ (receive goods)
    ▼
stock.move (供应商 → 仓库)
    │ 完成后
    ▼
stock.quant (库存增加)
```

### Purchase → Accounting（供应商账单）

```
purchase.order
    │ 收到账单
    ▼
account.move (type=in_invoice, vendor_bill)
    │ 三单匹配验证
    ▼
account.move.line (应付明细)
```

**三单匹配**:
- 采购订单数量/金额
- 收货单数量（stock.picking done 数量）
- 供应商账单金额
- 三者一致才能过账

### MRP → Inventory（生产）

```
mrp.production
    │ (confirm → in_production → done)
    ▼
stock.move (picking_type=consume)
    │ 领料（原材料库存减少）
    ▼
stock.move (picking_type=produce)
    │ 产成品入库（成品库存增加）
```

**MRP 物料清单**:
- `mrp.bom`: 定义产品配方（原材料 + 数量）
- 生产确认时，自动生成 `stock.move` 消耗/产出

## 版本主要特性对比

| 特性 | Odoo 16.0 | Odoo 17.0 | Odoo 18.0 |
|------|-----------|-----------|-----------|
| 发布日期 | 2022.10 | 2023.10 | 2024.10 |
| Studio | 重度改进 | Studio 包拆分 | 更灵活的 Studio |
| 仪表盘 | 改进图表 | 全新仪表盘 | 实时数据 |
| 电商 | 可视化 builder | 产品批量编辑 | 直播销售 |
| MRP | 产能计划 | 计划外生产 | 生产工单拆分 |
| 财务 | 按需发票 | 发票批量审批 | 简化财务流程 |
| 国际化 | 60+ 国家 | 80+ 国家 | 90+ 国家 |
| HTML5 | 支持 | 改进 | 全新编辑器 |
| POS | 多店铺 | 离线模式 | 多仓库支持 |
| Studio 限制 | 基础视图限制 | 扩展视图 | 完全自定义 |
