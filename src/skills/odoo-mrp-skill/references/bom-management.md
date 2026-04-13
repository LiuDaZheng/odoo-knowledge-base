# BOM 管理详解

## BOM 结构

### 基本 BOM

```
产品 A (1 个)
├── 组件 B (2 个)
├── 组件 C (1 个)
└── 组件 D (4 个)
```

### 多层 BOM

```
成品 (1 个)
├── 半成品 A (1 个)
│   ├── 组件 B (2 个)
│   └── 组件 C (1 个)
└── 半成品 B (1 个)
    ├── 组件 D (1 个)
    └── 组件 E (3 个)
```

## BOM 操作 API

### 创建 BOM

```python
bom_data = {
    'product_tmpl_id': template_id,
    'product_id': product_id,
    'type': 'normal',
    'bom_line_ids': [
        (0, 0, {
            'product_id': component_id,
            'product_qty': quantity,
            'product_uom_id': uom_id
        })
    ]
}
```

### 更新 BOM

```python
# 更新 BOM 头
odoo.execute_kw(db, uid, api_key, 'mrp.bom', 'write', [[bom_id, {'active': False}]])

# 更新 BOM 行
odoo.execute_kw(db, uid, api_key, 'mrp.bom.line', 'write', [[line_id, {'product_qty': new_qty}]])
```

### 删除 BOM

```python
odoo.execute_kw(db, uid, api_key, 'mrp.bom', 'unlink', [[bom_id]])
```

## BOM 验证

```python
def validate_bom(odoo, db, uid, api_key, bom_id):
    """验证 BOM 完整性"""
    errors = []
    
    # 检查 BOM 是否存在
    bom = odoo.execute_kw(db, uid, api_key, 'mrp.bom', 'read', [[bom_id]])
    if not bom:
        errors.append('BOM 不存在')
        return errors
    
    # 检查 BOM 行
    lines = odoo.execute_kw(db, uid, api_key, 'mrp.bom', 'read', [[bom_id, {'fields': ['bom_line_ids']}]])[0]
    if not lines.get('bom_line_ids'):
        errors.append('BOM 没有明细行')
    
    # 检查组件是否有效
    for line_id in lines.get('bom_line_ids', []):
        line = odoo.execute_kw(db, uid, api_key, 'mrp.bom.line', 'read', [[line_id]])
        if not line[0].get('product_id'):
            errors.append(f'BOM 行 {line_id} 缺少组件')
        if line[0].get('product_qty', 0) <= 0:
            errors.append(f'BOM 行 {line_id} 数量无效')
    
    return errors
```

---

*版本：1.0.0*
