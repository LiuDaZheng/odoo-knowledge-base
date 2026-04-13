# E-Commerce 模块数据模型

## ER 关系图

```mermaid
erDiagram
    product_template ||--o{ product_product : "产品模板"
    product_template ||--o{ sale_order_line : "模板销售行"
    product_product ||--o{ sale_order_line : "变体销售行"
    product_template ||--o{ product_pricelist_item : "价格规则"
    sale_order ||--o{ sale_order_line : "订单行"
    sale_order ||--o{ payment_transaction : "支付流水"
    sale_order ||--|{ stock_picking : "出库单"
    sale_order ||--|{ account_move : "销售发票"
    product_product ||--o{ stock_quant : "库存数量"
    payment_provider ||--o{ payment_transaction : "支付方式"
    website ||--o{ sale_order : "网站购物车"
    product_pricelist ||--o{ product_pricelist_item : "价格表规则"

    product_template {
        int id PK
        string name
        float list_price
        float standard_price
        bool website_published "上架状态"
        int website_sequence "网站排序"
        text description_sale "销售描述"
        int categ_id FK "产品分类"
        bool sale_ok "可售"
        bool purchase_ok "可采购"
        string type "product/consumable/service"
    }

    product_product {
        int id PK
        int product_tmpl_id FK
        string combination_indices "组合索引"
        int website_id FK "多网站可见性"
        float volume
        float weight
        string barcode
        string default_code
    }

    sale_order {
        int id PK
        string name "订单编号"
        int partner_id FK "客户"
        int website_id FK "来源网站"
        string state "draft/sent/sale/done/cancel"
        int cart_quantity "购物车商品数"
        float amount_total "订单总额"
        float amount_untaxed "未税金额"
        float amount_tax "税额"
        datetime date_order
        datetime confirmation_date "确认时间"
        int user_id FK "销售员"
        int pricelist_id FK "价格表"
    }

    sale_order_line {
        int id PK
        int order_id FK
        int product_id FK "product.product"
        float product_uom_qty "数量"
        float product_uom "单位"
        float price_unit "单价"
        float price_subtotal "小计"
        float discount "折扣率"
        string name "产品描述"
        int salesman_id FK
    }

    payment_transaction {
        int id PK
        string reference "支付流水号"
        int provider_id FK
        float amount
        string currency_id FK
        string state "draft/pending/done/cancel/error"
        int sale_order_id FK
        datetime date
        string acquirer_reference "第三方参考号"
    }

    payment_provider {
        int id PK
        string name "支付方式名称"
        string code "alipay/wechat/paypal/stripe"
        string state "enabled/disabled/test"
        int company_id FK
        bool journal_id FK "会计凭证"
    }

    stock_picking {
        int id PK
        string name "调拨单号"
        string state "draft/confirm/done/cancel"
        string picking_type_id "incoming/outgoing/internal"
        int partner_id FK "客户/供应商"
        int sale_id FK "关联销售订单"
    }
}
```

## 核心表字段说明

### product.template（产品模板）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 产品唯一标识 |
| name | char(128) | 产品名称 | 商品展示名称 |
| list_price | float | 网站售价 | 面向客户的标价 |
| standard_price | float | 成本价 | 产品成本，用于利润计算 |
| website_published | boolean | 上架状态 | true=在网站显示，false=下架 |
| website_sequence | integer | 网站排序 | 网站产品列表排序权重 |
| description_sale | text | 销售描述 | 前端产品详情页显示 |
| categ_id | integer | 产品分类 | 产品归类 |
| sale_ok | boolean | 可售 | 能否作为销售产品 |
| purchase_ok | boolean | 可采购 | 能否作为采购产品 |
| type | selection | 类型 | product(可库存)/consumable(消耗品)/service(服务) |

### product.product（产品变体）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 变体唯一标识 |
| product_tmpl_id | integer | 模板ID | 归属的模板 |
| combination_indices | char(64) | 组合索引 | 属性组合哈希值 |
| website_id | integer | 可见网站 | 多网站产品可见性 |
| volume | float | 体积 | 物流计算用 |
| weight | float | 重量 | 物流计算用 |
| barcode | char(64) | 条码 | 扫码识别 |
| default_code | char(64) | 产品编码 | 内部SKU |

### sale.order（购物车/订单）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 订单唯一标识 |
| name | char(64) | 订单编号 | 自动编号，如 S00089 |
| partner_id | integer | 客户ID | 购买方 |
| website_id | integer | 来源网站 | 哪个网站产生的订单 |
| state | selection | 状态 | draft=购物车, sent=已发报价, sale=确认订单, done=完成, cancel=取消 |
| cart_quantity | integer | 购物车商品数 | 订单行数量汇总 |
| amount_total | float | 订单总额 | 含税总计 |
| amount_untaxed | float | 未税金额 | 不含税小计 |
| amount_tax | float | 税额 | 税额 |
| date_order | datetime | 下单时间 | 创建/下单时间 |
| confirmation_date | datetime | 确认时间 | state 变为 sale 的时间 |
| user_id | integer | 销售员 | 负责跟单的销售人员 |
| pricelist_id | integer | 价格表 | 使用的价格表 |

### sale.order.line（订单行）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 行唯一标识 |
| order_id | integer | 订单ID | 归属订单 |
| product_id | integer | 产品ID | 实际关联 product.product |
| product_uom_qty | float | 数量 | 订购数量 |
| product_uom | integer | 单位 | 计量单位 |
| price_unit | float | 单价 | 行项目单价 |
| price_subtotal | float | 小计 | 未税小计 = qty × price_unit × (1-discount) |
| discount | float | 折扣率 | 0.0 ~ 1.0，如 0.1 表示 10% 折扣 |
| name | text | 描述 | 行项目描述（取产品名称） |

### payment.transaction（支付流水）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 流水唯一标识 |
| reference | char(64) | 流水号 | 内部流水号 |
| provider_id | integer | 支付渠道ID | 如支付宝、微信 |
| amount | float | 支付金额 | 本次支付金额 |
| currency_id | integer | 币种 | 支付币种 |
| state | selection | 状态 | draft/pending(待付)/done(成功)/cancel(取消)/error(失败) |
| sale_order_id | integer | 关联订单 | 所属销售订单 |
| date | datetime | 支付时间 | 完成时间 |
| acquirer_reference | char(128) | 第三方参考号 | 支付宝/微信交易号 |

### payment.provider（支付提供商）

| 字段名 | 类型 | 说明 | 业务含义 |
|--------|------|------|---------|
| id | integer | 主键 | 提供商ID |
| name | char(128) | 名称 | 如"支付宝"、"微信支付" |
| code | char(32) | 代码 | alipay/wechat/paypal/stripe/manual |
| state | selection | 状态 | enabled/disabled/test |
| company_id | integer | 公司 | 所属公司 |
| journal_id | integer | 收款账户 | 会计科目标记 |

## 业务场景映射

### 电商数据流转

```
┌──────────────────┐
│ product.template │
│ website_published │
│    = True         │──上架──▶ 用户浏览网站商品
└────────┬─────────┘
         │ (选择规格/变体)
         ▼
┌──────────────────┐
│  product.product │
│ (combination_idx)│──加入购物车──▶ sale.order (state=draft)
└────────┬─────────┘                            │
         │                                      │ (确认购买)
         │                                      ▼
         │                              ┌─────────────────┐
         │                              │  sale.order     │
         │                              │  state = sale   │
         │                              └────────┬────────┘
         │                                         │
    ┌────┴────┬──────────────────┬─────────────────┼─────────────────┐
    ▼         ▼                  ▼                 ▼                 ▼
┌────────┐ ┌────────┐    ┌────────────┐  ┌───────────┐  ┌──────────┐
│payment │ │  stock │    │account.move│  │sale.order │  │  Email   │
│trans.  │ │picking │    │ (Invoice)  │  │  发票      │  │ 确认邮件 │
│ 支付   │ │  出货   │    │   应收发票  │  │           │  │          │
└────────┘ └────────┘    └────────────┘  └───────────┘  └──────────┘
```

### 状态对应关系

| sale.order state | 含义 | 前端显示 |
|-----------------|------|---------|
| draft | 购物车 | 我的购物车 |
| sent | 报价单已发送 | 待确认 |
| sale | 订单已确认 | 生产中/已确认 |
| done | 订单完成 | 已完成 |
| cancel | 订单取消 | 已取消 |

### 购物车与订单转换

```python
# 购物车 draft → 确认 sale
order = request.website.sale_get_order()
order.action_confirm()  # state: draft → sale

# 触发自动行为
# 1. stock.picking 创建（state='draft'）
# 2. account.move 创建（客户发票，state='draft'）
# 3. payment.transaction 创建待支付记录
```

### 多网站价格隔离

- `product_product.website_id`: NULL 表示全局可用，非 NULL 仅该网站可见
- `sale_order.website_id`: 追踪订单来源
- `pricelist_id` 绑定 website，实现网站级定价
