# 库存移动（Stock Moves）

## 库存移动的双条目原则

```mermaid
erDiagram
    stock_move ||--|| stock_location_from : "源库位"
    stock_move ||--|| stock_location_to : "目标库位"
    stock_move ||--o{ stock_quant : "创建 quant"
    stock_move ||--|| stock_picking : "归属调拨单"

    stock_move {
        int id PK
        string name
        int product_id FK
        float product_uom_qty "数量"
        int location_id FK "源库位"
        int location_dest_id FK "目标库位"
        string state "draft/assigned/done/cancel"
        float reserved_availability "已预留"
        float quantity_done "已完成"
    }

    stock_location {
        int id PK
        string name
        string location_type "supplier/customer/internal/view/scrap"
        int location_id FK "父库位"
        bool putaway_strategy_id
        int company_id FK
    }

    stock_quant {
        int id PK
        int product_id FK
        int location_id FK
        float quantity "可用数量"
        float reserved_quantity "预留数量"
        int lot_id FK "批次/序列号"
    }
```

**双条目原则**: 每一次库存移动，源库位数量减少，目标库位数量增加，通过 `stock.move` 记录这两条边的状态变化。

## 移动类型

```mermaid
graph TD
    A["库存移动类型"] --> B["incoming\n入库"]
    A --> C["outgoing\n出库"]
    A --> D["internal\n库间调拨"]
    A --> E["scrap\n报废"]
    
    B --> B1["供应商→仓库\n采购入库"]
    C --> C1["仓库→客户\n销售出库"]
    D --> D1["仓库A→仓库B\n调拨"]
    E --> E1["仓库→报废区\n损耗处理"]
    
    style B fill:#9f9
    style C fill:#f99
    style D fill:#99f
    style E fill:#999
```

| 类型 | picking_type | 方向 | 典型场景 |
|------|-------------|------|---------|
| incoming | vendors | 供应商→仓库 | 采购入库、退货入库 |
| outgoing | customers | 仓库→客户 | 销售出库、退货出库 |
| internal | internal | 仓库→仓库 | 库间调拨、质量检查 |
| scrap | scrap | 仓库→报废 | 损耗、过期 |

## 批次（Lot）和序列号（Serial）追踪

### lot_id vs serial_id

| 字段 | 说明 | 追踪粒度 |
|------|------|---------|
| `lot_id` | 批次号 | 同批次商品共享一个追踪ID |
| `serial_id` | 序列号 | 每个商品唯一序列号 |

```python
# 产品设置
product = env['product.product'].browse(product_id)
product.tracking = 'lot'    # 批次追踪
product.tracking = 'serial'  # 序列号追踪
product.tracking = 'none'    # 不追踪
```

### 批次管理流程

```
采购入库 → 录入/扫描批次号 → 批次入库
   ↓
销售出库 → 指定批次 → 批次出库 → 库存扣减指定批次
   ↓
库存查询 → 按批次查询 → 批次追溯（供应商/日期）
```

### 库存预留与批次

```python
# 出库时选择批次
move_ids.action_assign()
# 系统根据 FIFO 原则选择最早批次
# 也可以手动指定批次

# 序列号全程追踪
# 入库时必须指定 serial
# 出库时系统校验 serial 已入过库
```

## 操作详情 vs 即时转移

### 操作详情（Draft → Done）

```mermaid
graph LR
    A["draft\n草稿"] --> B["confirm\n确认"]
    B --> C["assigned\n已预留"]
    C --> D["move.quantity_done += N\n填写完成数"]
    D --> E["done\n完成"]
    C -->|"数量不足"| F["部分可用"]
```

**关键状态**:
- `draft`: 创建调拨单，尚未确认
- `confirm`: 确认调拨（源库位检查可用性）
- `assigned`: 库存已预留（reserved_availability = product_uom_qty）
- `done`: 移动完成，quant 更新

### 即时转移（Immediate Transfer）

```
选项: "立即转移" (Immediate Transfer)
含义: 不经过 draft → assigned → done 流程
     直接在确认时完成调拨
效果: 跳过操作详情界面，直接更新 quant

适用场景:
- 快速调拨，不需要逐行确认
- 系统自动填充 quantity_done = product_uom_qty
- 直接 done 状态
```

### 对比

| 维度 | 操作详情模式 | 即时转移 |
|------|-------------|---------|
| 界面 | 有独立的确认→填写→完成步骤 | 直接完成 |
| 灵活性 | 可填写不同数量 | 必须填写完整数量 |
| 批次指定 | 逐行选择批次/序列号 | 无法选择 |
| 适用场景 | 需要复核的调拨 | 快速内部调拨 |
| 状态演变 | draft→assigned→done | draft→done（一步） |

### 操作详情模式示例

```
1. 创建调拨单 (state=draft)
   └─ 添加 move: 产品A x 10, 位置: WH→客户

2. 确认调拨 (state=assigned)
   └─ 系统检查 WH 的 quant 是否 >= 10
   └─ 预留 10 个 (reserved_quantity=10)

3. 仓库人员填写完成数 (quantity_done=8)
   └─ 实际出库 8 个

4. 完成 (state=done)
   └─ 源库位 quant -= 8
   └─ 目标库位 quant += 8
```
