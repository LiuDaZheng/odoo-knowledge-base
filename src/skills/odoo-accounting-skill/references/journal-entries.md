# 日记账分录 (Journal Entries)

## 分录结构

### 基本结构

```python
{
    'journal_id': 1,           # 日记账 ID
    'date': '2026-04-12',      # 分录日期
    'ref': 'INV/2026/001',     # 参考号
    'state': 'draft',          # 状态：draft/posted/cancel
    'line_ids': [              # 分录明细
        (0, 0, {               # 创建新明细
            'account_id': 10,  # 科目 ID
            'debit': 1000.00,  # 借方金额
            'credit': 0.00,    # 贷方金额
            'name': '摘要'
        })
    ]
}
```

### 分录状态流转

```
draft (草稿) → posted (已过账) → cancel (已冲销)
     ↓              ↓
  action_post   action_reverse
```

## 常见分录示例

### 1. 销售收款

```python
# 销售商品收款
entry_data = {
    'journal_id': 1,  # 银行日记账
    'date': '2026-04-12',
    'ref': 'RCPT/2026/001',
    'line_ids': [
        (0, 0, {
            'account_id': 101010,  # 银行存款
            'debit': 1130.00,
            'credit': 0.00,
            'name': '收到客户 A 货款'
        }),
        (0, 0, {
            'account_id': 401000,  # 主营业务收入
            'debit': 0.00,
            'credit': 1000.00,
            'name': '销售收入'
        }),
        (0, 0, {
            'account_id': 205001,  # 应交增值税
            'debit': 0.00,
            'credit': 130.00,
            'name': '销项税额 (13%)'
        })
    ]
}
```

### 2. 采购付款

```python
# 采购商品付款
entry_data = {
    'journal_id': 2,  # 付款日记账
    'date': '2026-04-12',
    'ref': 'PAY/2026/001',
    'line_ids': [
        (0, 0, {
            'account_id': 202001,  # 应付账款
            'debit': 1130.00,
            'credit': 0.00,
            'name': '支付供应商 B 货款'
        }),
        (0, 0, {
            'account_id': 101010,  # 银行存款
            'debit': 0.00,
            'credit': 1130.00,
            'name': '银行付款'
        })
    ]
}
```

### 3. 费用报销

```python
# 员工费用报销
entry_data = {
    'journal_id': 3,  # 现金日记账
    'date': '2026-04-12',
    'ref': 'EXP/2026/001',
    'line_ids': [
        (0, 0, {
            'account_id': 503002,  # 管理费用 - 办公费
            'debit': 500.00,
            'credit': 0.00,
            'name': '办公用品采购'
        }),
        (0, 0, {
            'account_id': 101001,  # 现金
            'debit': 0.00,
            'credit': 500.00,
            'name': '现金报销'
        })
    ]
}
```

### 4. 计提折旧

```python
# 固定资产折旧
entry_data = {
    'journal_id': 4,  # 转账日记账
    'date': '2026-04-30',
    'ref': 'DEP/2026/04',
    'line_ids': [
        (0, 0, {
            'account_id': 503003,  # 管理费用 - 折旧费
            'debit': 5000.00,
            'credit': 0.00,
            'name': '4 月折旧费'
        }),
        (0, 0, {
            'account_id': 112000,  # 累计折旧
            'debit': 0.00,
            'credit': 5000.00,
            'name': '累计折旧'
        })
    ]
}
```

### 5. 结转损益

```python
# 期末结转收入
entry_data = {
    'journal_id': 4,
    'date': '2026-04-30',
    'ref': 'CLSE/2026/04/REV',
    'line_ids': [
        (0, 0, {
            'account_id': 401000,  # 主营业务收入
            'debit': 100000.00,
            'credit': 0.00,
            'name': '结转收入'
        }),
        (0, 0, {
            'account_id': 300300,  # 未分配利润
            'debit': 0.00,
            'credit': 100000.00,
            'name': '利润结转'
        })
    ]
}

# 期末结转费用
entry_data = {
    'journal_id': 4,
    'date': '2026-04-30',
    'ref': 'CLSE/2026/04/EXP',
    'line_ids': [
        (0, 0, {
            'account_id': 300300,  # 未分配利润
            'debit': 80000.00,
            'credit': 0.00,
            'name': '费用结转'
        }),
        (0, 0, {
            'account_id': 500000,  # 主营业务成本
            'debit': 0.00,
            'credit': 50000.00,
            'name': '结转成本'
        }),
        (0, 0, {
            'account_id': 500200,  # 销售费用
            'debit': 0.00,
            'credit': 15000.00,
            'name': '结转销售费用'
        }),
        (0, 0, {
            'account_id': 500300,  # 管理费用
            'debit': 0.00,
            'credit': 15000.00,
            'name': '结转管理费用'
        })
    ]
}
```

## 分录操作函数

### 创建分录

```python
def create_journal_entry(odoo, db, uid, api_key, journal_id, date, ref, lines):
    """创建日记账分录"""
    entry_data = {
        'journal_id': journal_id,
        'date': date,
        'ref': ref,
        'line_ids': lines
    }
    entry_id = odoo.execute_kw(db, uid, api_key, 'account.move', 'create', [entry_data])
    return entry_id
```

### 过账分录

```python
def post_journal_entry(odoo, db, uid, api_key, entry_id):
    """过账分录"""
    result = odoo.execute_kw(db, uid, api_key, 'account.move', 'action_post', [[entry_id]])
    return result
```

### 冲销分录

```python
def reverse_journal_entry(odoo, db, uid, api_key, entry_id, reverse_date=None):
    """冲销分录"""
    reverse_data = {
        'date': reverse_date or datetime.now().strftime('%Y-%m-%d'),
        'reversal_move_id': entry_id
    }
    reverse_id = odoo.execute_kw(db, uid, api_key, 'account.move', 'action_reverse', [[entry_id]], {'context': reverse_data})
    return reverse_id
```

### 查询分录

```python
def search_journal_entries(odoo, db, uid, api_key, journal_id=None, date_from=None, date_to=None, state='posted'):
    """查询日记账分录"""
    domain = []
    
    if journal_id:
        domain.append(['journal_id', '=', journal_id])
    if date_from:
        domain.append(['date', '>=', date_from])
    if date_to:
        domain.append(['date', '<=', date_to])
    if state:
        domain.append(['state', '=', state])
    
    fields = ['id', 'name', 'date', 'ref', 'journal_id', 'state', 'amount_total']
    entries = odoo.execute_kw(db, uid, api_key, 'account.move', 'search_read', [domain], {'fields': fields})
    return entries
```

## 分录验证规则

### 借贷平衡检查

```python
def validate_entry_balance(lines):
    """验证分录借贷平衡"""
    total_debit = 0
    total_credit = 0
    
    for line in lines:
        if isinstance(line, tuple) and line[0] == 0 and len(line) > 2:
            line_data = line[2]
            total_debit += line_data.get('debit', 0)
            total_credit += line_data.get('credit', 0)
    
    if abs(total_debit - total_credit) > 0.01:
        raise ValueError(f'分录不平衡：借方={total_debit}, 贷方={total_credit}')
    
    return True
```

### 必填字段检查

```python
def validate_entry_fields(entry_data):
    """验证分录必填字段"""
    required_fields = ['journal_id', 'date', 'line_ids']
    for field in required_fields:
        if field not in entry_data:
            raise ValueError(f'缺少必填字段：{field}')
    
    # 验证分录明细
    for line in entry_data['line_ids']:
        if isinstance(line, tuple) and line[0] == 0 and len(line) > 2:
            line_data = line[2]
            if 'account_id' not in line_data:
                raise ValueError('分录明细缺少科目 ID')
            if 'debit' not in line_data or 'credit' not in line_data:
                raise ValueError('分录明细缺少借贷金额')
    
    return True
```

---

*版本：1.0.0*
*适用于：Odoo 16+/17+/18+*
