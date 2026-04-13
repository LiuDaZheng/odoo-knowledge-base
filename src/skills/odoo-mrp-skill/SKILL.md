---
name: odoo-mrp-skill
description: Odoo 生产制造 Skill - 提供 BOM 管理 (创建/编辑/版本控制/成本计算)、工单管理 (创建/跟踪/成本分析)、生产计划、质量控制功能。Use when working with Odoo MRP modules for: (1) Managing bills of materials, (2) Creating and tracking manufacturing orders, (3) Production planning and scheduling, (4) Cost analysis and control, (5) Quality management.
---

# Odoo 生产制造 Skill

## 快速开始

### 认证配置

```bash
export ODOO_URL="https://your-company.odoo.com"
export ODOO_DB="your_database"
export ODOO_API_KEY="your_api_key"
export ODOO_UID="your_user_id"
```

### 基础用法

```bash
# 查询 BOM 列表
odoo-mrp list-boms --product "Product A"

# 创建工单
odoo-mrp create-order --bom 1 --qty 100

# 查看生产进度
odoo-mrp track-orders --status in_progress
```

## 核心功能

### 1. BOM 管理 (Bill of Materials)

#### 查询 BOM

```python
# 使用 XML-RPC 查询 BOM
domain = [['product_tmpl_id', '=', product_template_id]]
fields = ['product_tmpl_id', 'bom_line_ids', 'type', 'active']

boms = odoo.execute_kw(db, uid, api_key, 'mrp.bom', 'search_read', [domain], {'fields': fields})
```

#### BOM 类型

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| Manufacture | 制造 BOM | 自己生产 |
| Kit | 套件 BOM | 直接组装销售 |
| Subcontract | 委外加工 | 外包生产 |

#### 创建 BOM

```python
bom_data = {
    'product_tmpl_id': product_template_id,
    'product_id': product_id,
    'type': 'normal',  # normal 或 kit
    'bom_line_ids': [
        (0, 0, {
            'product_id': component_id_1,
            'product_qty': 2.0,
            'product_uom_id': 1,  # 单位 ID
            'sequence': 10
        }),
        (0, 0, {
            'product_id': component_id_2,
            'product_qty': 1.0,
            'product_uom_id': 1,
            'sequence': 20
        })
    ]
}
bom_id = odoo.execute_kw(db, uid, api_key, 'mrp.bom', 'create', [bom_data])
```

#### BOM 版本控制

```python
# 创建 BOM 版本
bom_version_data = {
    'bom_id': bom_id,
    'name': 'V2.0',
    'active_date': '2026-04-12',
    'change_description': '更新组件规格'
}
version_id = odoo.execute_kw(db, uid, api_key, 'mrp.bom.version', 'create', [bom_version_data])

# 查询历史版本
domain = [['bom_id', '=', bom_id]]
versions = odoo.execute_kw(db, uid, api_key, 'mrp.bom.version', 'search_read', [domain])
```

#### BOM 成本计算

```python
def calculate_bom_cost(odoo, db, uid, api_key, bom_id):
    """计算 BOM 成本"""
    # 获取 BOM 明细
    domain = [['bom_id', '=', bom_id]]
    fields = ['product_id', 'product_qty', 'product_uom_id']
    bom_lines = odoo.execute_kw(db, uid, api_key, 'mrp.bom.line', 'search_read', [domain], {'fields': fields})
    
    total_cost = 0
    cost_details = []
    
    for line in bom_lines:
        # 获取组件成本
        product = odoo.execute_kw(db, uid, api_key, 'product.product', 'read', [[line['product_id'][0]], {'fields': ['standard_price']}])
        unit_cost = product[0].get('standard_price', 0)
        line_cost = unit_cost * line['product_qty']
        
        total_cost += line_cost
        cost_details.append({
            'component': line['product_id'][1],
            'quantity': line['product_qty'],
            'unit_cost': unit_cost,
            'line_total': line_cost
        })
    
    return {
        'bom_id': bom_id,
        'total_cost': total_cost,
        'details': cost_details
    }
```

**详细 BOM 管理**: 参见 [references/bom-management.md](references/bom-management.md)

### 2. 工单管理 (Manufacturing Orders)

#### 创建工单

```python
mo_data = {
    'product_id': product_id,
    'product_qty': 100,
    'product_uom_id': 1,
    'bom_id': bom_id,
    'date_start': '2026-04-12',
    'date_deadline': '2026-04-20'
}
mo_id = odoo.execute_kw(db, uid, api_key, 'mrp.production', 'create', [mo_data])
```

#### 工单状态流转

```python
# 确认工单
odoo.execute_kw(db, uid, api_key, 'mrp.production', 'button_confirm', [[mo_id]])

# 开始生产
odoo.execute_kw(db, uid, api_key, 'mrp.production', 'button_mark_started', [[mo_id]])

# 完成生产
odoo.execute_kw(db, uid, api_key, 'mrp.production', 'button_mark_done', [[mo_id]])

# 取消工单
odoo.execute_kw(db, uid, api_key, 'mrp.production', 'action_cancel', [[mo_id]])
```

#### 工单跟踪

```python
def track_manufacturing_order(odoo, db, uid, api_key, mo_id):
    """跟踪工单进度"""
    mo = odoo.execute_kw(db, uid, api_key, 'mrp.production', 'read', [[mo_id], {
        'fields': ['name', 'state', 'product_qty', 'qty_produced', 'date_start', 'date_deadline']
    }])[0]
    
    # 计算进度
    progress = (mo.get('qty_produced', 0) / mo.get('product_qty', 1)) * 100 if mo.get('product_qty') else 0
    
    # 获取领料情况
    move_domain = [['production_id', '=', mo_id]]
    moves = odoo.execute_kw(db, uid, api_key, 'stock.move', 'search_read', [move_domain])
    
    return {
        'order': mo['name'],
        'state': mo['state'],
        'progress': f"{progress:.1f}%",
        'produced': mo.get('qty_produced', 0),
        'planned': mo.get('product_qty', 0),
        'start_date': mo.get('date_start'),
        'deadline': mo.get('date_deadline'),
        'moves': moves
    }
```

#### 工单成本分析

```python
def analyze_mo_cost(odoo, db, uid, api_key, mo_id):
    """工单成本分析"""
    mo = odoo.execute_kw(db, uid, api_key, 'mrp.production', 'read', [[mo_id], {
        'fields': ['product_qty', 'qty_produced']
    }])[0]
    
    # 材料成本
    material_domain = [['production_id', '=', mo_id], ['move_dest_ids', '=', False]]
    material_moves = odoo.execute_kw(db, uid, api_key, 'stock.move', 'search_read', [material_domain])
    material_cost = sum(move.get('price_unit', 0) * move.get('product_uom_qty', 0) for move in material_moves)
    
    # 工时成本
    work_domain = [['production_id', '=', mo_id]]
    work_orders = odoo.execute_kw(db, uid, api_key, 'mrp.workcenter.productivity', 'search_read', [work_domain])
    labor_cost = sum(wo.get('cost', 0) for wo in work_orders)
    
    # 总成本
    total_cost = material_cost + labor_cost
    unit_cost = total_cost / mo.get('qty_produced', 1) if mo.get('qty_produced') else 0
    
    return {
        'mo_id': mo_id,
        'material_cost': material_cost,
        'labor_cost': labor_cost,
        'total_cost': total_cost,
        'produced_qty': mo.get('qty_produced', 0),
        'unit_cost': unit_cost
    }
```

**详细工单管理**: 参见 [references/manufacturing-orders.md](references/manufacturing-orders.md)

### 3. 生产计划 (Production Planning)

#### 创建生产计划

```python
planning_data = {
    'name': '2026 年 4 月生产计划',
    'date_start': '2026-04-01',
    'date_end': '2026-04-30',
    'state': 'draft'
}
planning_id = odoo.execute_kw(db, uid, api_key, 'mrp.planning', 'create', [planning_data])
```

#### 产能规划

```python
def check_workcenter_capacity(odoo, db, uid, api_key, workcenter_id, date_from, date_to):
    """检查工作中心产能"""
    # 获取工作中心信息
    wc = odoo.execute_kw(db, uid, api_key, 'mrp.workcenter', 'read', [[workcenter_id], {
        'fields': ['name', 'capacity', 'time_efficiency']
    }])[0]
    
    # 查询已安排工单
    domain = [
        ['workcenter_id', '=', workcenter_id],
        ['date_start', '>=', date_from],
        ['date_end', '<=', date_to]
    ]
    scheduled_orders = odoo.execute_kw(db, uid, api_key, 'mrp.workorder', 'search_read', [domain])
    
    # 计算已用产能
    used_hours = sum(order.get('duration', 0) for order in scheduled_orders)
    
    # 计算可用产能
    total_days = (datetime.strptime(date_to, '%Y-%m-%d') - datetime.strptime(date_from, '%Y-%m-%d')).days + 1
    available_hours = total_days * wc.get('capacity', 8) * (wc.get('time_efficiency', 100) / 100)
    
    return {
        'workcenter': wc['name'],
        'period': f"{date_from} 至 {date_to}",
        'available_hours': available_hours,
        'used_hours': used_hours,
        'remaining_hours': available_hours - used_hours,
        'utilization_rate': (used_hours / available_hours * 100) if available_hours else 0
    }
```

### 4. 质量控制 (Quality Control)

#### 创建质检单

```python
quality_check_data = {
    'production_id': mo_id,
    'quality_point_id': quality_point_id,
    'product_id': product_id,
    'lot_id': lot_id,
    'qty_done': 100,
    'state': 'pending'
}
qc_id = odoo.execute_kw(db, uid, api_key, 'quality.check', 'create', [quality_check_data])
```

#### 质检结果记录

```python
# 通过质检
odoo.execute_kw(db, uid, api_key, 'quality.check', 'action_passed', [[qc_id]])

# 失败质检
odoo.execute_kw(db, uid, api_key, 'quality.check', 'action_failed', [[qc_id]])

# 记录测量值
measurement_data = {
    'check_id': qc_id,
    'name': '尺寸测量',
    'value': 10.5,
    'target_min': 10.0,
    'target_max': 11.0
}
odoo.execute_kw(db, uid, api_key, 'quality.measure', 'create', [measurement_data])
```

## 脚本工具

### BOM 批量导入

```bash
python scripts/import_boms.py --file boms.csv --company 1
```

### 工单批量创建

```bash
python scripts/batch_create_mo.py --file orders.xlsx --start-date 2026-04-12
```

### 生产报表导出

```bash
python scripts/export_production_report.py --month 2026-04 --format pdf
```

## 最佳实践

### 1. BOM 管理

- 使用版本控制追踪变更
- 定期审核 BOM 准确性
- 建立 BOM 审批流程

### 2. 工单管理

- 及时更新工单状态
- 准确记录领料和工时
- 定期分析工单成本差异

### 3. 生产计划

- 考虑产能约束
- 预留安全缓冲时间
- 定期滚动更新计划

## 故障排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| BOM 无法创建 | 产品未设置可制造 | 在产品表单勾选"可制造" |
| 工单状态无法变更 | 前置条件未满足 | 检查领料是否完成 |
| 成本计算错误 | 标准价格未设置 | 更新产品标准成本 |

## 参考资料

- [BOM 管理详解](references/bom-management.md)
- [工单管理详解](references/manufacturing-orders.md)
- [生产计划指南](references/production-planning.md)
- [质量控制流程](references/quality-control.md)

## 支持的 Odoo 版本

- Odoo 16.0 LTS
- Odoo 17.0 LTS
- Odoo 18.0 (最新)

---

*Skill 版本：1.0.0*
*最后更新：2026-04-12*
*维护者：大正*
