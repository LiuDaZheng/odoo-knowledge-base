# 应付管理 (Accounts Payable - AP)

## AP 工作流程

```
创建供应商 → 采购订单 → 收货入库 → 供应商账单 → 付款申请 → 付款登记 → 核销对账
```

## 供应商账单管理

### 创建供应商账单

```python
def create_vendor_bill(odoo, db, uid, api_key, vendor_id, bill_date, lines):
    """创建供应商账单"""
    bill_data = {
        'move_type': 'in_invoice',
        'partner_id': vendor_id,
        'invoice_date': bill_date,
        'invoice_date_due': bill_date,
        'invoice_line_ids': lines
    }
    bill_id = odoo.execute_kw(db, uid, api_key, 'account.move', 'create', [bill_data])
    return bill_id

# 使用示例
lines = [
    (0, 0, {
        'product_id': 10,
        'name': '原材料 A',
        'quantity': 100,
        'price_unit': 50.00,
        'account_id': 500000,  # 成本科目
        'tax_ids': [(6, 0, [1])]
    })
]
bill_id = create_vendor_bill(odoo, db, uid, api_key, vendor_id=20, bill_date='2026-04-12', lines=lines)
```

### 账单确认

```python
# 确认账单
odoo.execute_kw(db, uid, api_key, 'account.move', 'action_post', [[bill_id]])

# 取消账单
odoo.execute_kw(db, uid, api_key, 'account.move', 'action_cancel', [[bill_id]])
```

### 查询应付账款

```python
def get_payables(odoo, db, uid, api_key, vendor_id=None, days_overdue=0):
    """查询应付账款"""
    domain = [
        ['account_type', '=', 'liability_payable'],
        ['reconciled', '=', False]
    ]
    
    if vendor_id:
        domain.append(['partner_id', '=', vendor_id])
    
    fields = ['id', 'date', 'date_maturity', 'debit', 'credit', 'balance', 'partner_id', 'move_id']
    amls = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain], {'fields': fields})
    
    return amls
```

## 付款管理

### 创建付款

```python
def create_vendor_payment(odoo, db, uid, api_key, vendor_id, amount, journal_id, payment_date):
    """创建供应商付款"""
    payment_data = {
        'payment_type': 'outbound',
        'partner_id': vendor_id,
        'amount': amount,
        'date': payment_date,
        'journal_id': journal_id
    }
    payment_id = odoo.execute_kw(db, uid, api_key, 'account.payment', 'create', [payment_data])
    
    # 过账付款
    odoo.execute_kw(db, uid, api_key, 'account.payment', 'action_post', [[payment_id]])
    
    return payment_id

# 使用示例
payment_id = create_vendor_payment(odoo, db, uid, api_key,
                                   vendor_id=20,
                                   amount=5650.00,
                                   journal_id=2,  # 银行日记账
                                   payment_date='2026-04-12')
```

### 批量付款

```python
def create_batch_payments(odoo, db, uid, api_key, payments, journal_id, payment_date):
    """创建批量付款"""
    payment_ids = []
    for payment in payments:
        payment_data = {
            'payment_type': 'outbound',
            'partner_id': payment['vendor_id'],
            'amount': payment['amount'],
            'date': payment_date,
            'journal_id': journal_id,
            'ref': payment.get('ref', '')
        }
        pid = odoo.execute_kw(db, uid, api_key, 'account.payment', 'create', [payment_data])
        payment_ids.append(pid)
    
    # 批量过账
    odoo.execute_kw(db, uid, api_key, 'account.payment', 'action_post', [payment_ids])
    
    return payment_ids
```

## AP 账龄分析

### 生成账龄报告

```python
def generate_ap_aging_report(odoo, db, uid, api_key, as_of_date=None):
    """生成 AP 账龄报告"""
    from datetime import datetime, timedelta
    
    as_of_date = as_of_date or datetime.now()
    
    # 获取所有未核销的应付明细
    domain = [
        ['account_type', '=', 'liability_payable'],
        ['reconciled', '=', False],
        ['parent_state', '=', 'posted']
    ]
    fields = ['id', 'partner_id', 'date_maturity', 'balance', 'debit', 'credit']
    amls = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain], {'fields': fields})
    
    # 按供应商汇总
    aging_report = {}
    for aml in amls:
        partner_id = aml['partner_id'][0] if isinstance(aml['partner_id'], list) else aml['partner_id']
        partner_name = aml['partner_id'][1] if isinstance(aml['partner_id'], list) else 'Unknown'
        
        if partner_id not in aging_report:
            aging_report[partner_id] = {
                'name': partner_name,
                'buckets': {
                    '未到期': 0.0,
                    '1-30 天': 0.0,
                    '31-60 天': 0.0,
                    '61-90 天': 0.0,
                    '90 天以上': 0.0
                },
                'total': 0.0
            }
        
        # 计算逾期天数
        days_overdue = 0
        if aml.get('date_maturity'):
            maturity_date = datetime.strptime(aml['date_maturity'], '%Y-%m-%d')
            days_overdue = (as_of_date - maturity_date).days
        
        # 分配到对应区间
        balance = aml.get('balance', 0) or (aml.get('debit', 0) - aml.get('credit', 0))
        if days_overdue <= 0:
            aging_report[partner_id]['buckets']['未到期'] += abs(balance)
        elif days_overdue <= 30:
            aging_report[partner_id]['buckets']['1-30 天'] += abs(balance)
        elif days_overdue <= 60:
            aging_report[partner_id]['buckets']['31-60 天'] += abs(balance)
        elif days_overdue <= 90:
            aging_report[partner_id]['buckets']['61-90 天'] += abs(balance)
        else:
            aging_report[partner_id]['buckets']['90 天以上'] += abs(balance)
        
        aging_report[partner_id]['total'] += abs(balance)
    
    return aging_report
```

## 付款条件

### 设置付款条件

```python
# 创建付款条件
payment_term_data = {
    'name': 'Net 30',
    'line_ids': [
        (0, 0, {
            'value': 'balance',
            'value_amount': 0.0,
            'months': 1,
            'days': 0
        })
    ]
}
payment_term_id = odoo.execute_kw(db, uid, api_key, 'account.payment.term', 'create', [payment_term_data])

# 应用到供应商
odoo.execute_kw(db, uid, api_key, 'res.partner', 'write', [[vendor_id, {'property_payment_term_id': payment_term_id}]])
```

### 常见付款条件

```python
PAYMENT_TERMS = {
    'COD': '货到付款',
    'Net 15': '15 天付款',
    'Net 30': '30 天付款',
    'Net 60': '60 天付款',
    '2/10 Net 30': '10 天内付款享受 2% 折扣，否则 30 天全额'
}
```

## 供应商管理

### 创建供应商

```python
def create_vendor(odoo, db, uid, api_key, name, email, phone, tax_id=None):
    """创建供应商"""
    vendor_data = {
        'name': name,
        'email': email,
        'phone': phone,
        'supplier_rank': 1,  # 标记为供应商
        'company_type': 'company',
        'vat': tax_id
    }
    vendor_id = odoo.execute_kw(db, uid, api_key, 'res.partner', 'create', [vendor_data])
    return vendor_id
```

### 供应商对账

```python
def reconcile_vendor_statement(odoo, db, uid, api_key, vendor_id, statement_lines):
    """供应商对账"""
    # 获取供应商未核销明细
    domain = [
        ['partner_id', '=', vendor_id],
        ['account_type', '=', 'liability_payable'],
        ['reconciled', '=', False]
    ]
    amls = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain])
    
    # 匹配对账
    for statement_line in statement_lines:
        for aml in amls:
            if abs(aml['balance'] - statement_line['amount']) < 0.01:
                # 执行核销
                reconcile_data = {
                    'to_reconcile': [aml['id'], statement_line['move_line_id']]
                }
                odoo.execute_kw(db, uid, api_key, 'account.move.line', 'reconcile', [reconcile_data])
                break
```

## 常见场景

### 场景 1：预付供应商货款

```python
# 创建预付款
prepayment_data = {
    'payment_type': 'outbound',
    'partner_id': vendor_id,
    'amount': 10000.00,
    'date': '2026-04-01',
    'journal_id': 2
}
payment_id = odoo.execute_kw(db, uid, api_key, 'account.payment', 'create', [prepayment_data])

# 预付款分录
entry_data = {
    'journal_id': 2,
    'date': '2026-04-01',
    'line_ids': [
        (0, 0, {'account_id': 103000, 'debit': 10000.00, 'credit': 0.00, 'name': '预付账款'}),
        (0, 0, {'account_id': 101010, 'debit': 0.00, 'credit': 10000.00, 'name': '银行付款'})
    ]
}
```

### 场景 2：现金折扣

```python
# 2/10 Net 30 - 10 天内付款享受 2% 折扣
original_amount = 10000.00
discount = original_amount * 0.02  # 200 元
payment_amount = original_amount - discount  # 9800 元

# 付款分录
entry_data = {
    'journal_id': 2,
    'date': '2026-04-10',
    'line_ids': [
        (0, 0, {'account_id': 202001, 'debit': 10000.00, 'credit': 0.00, 'name': '应付账款'}),
        (0, 0, {'account_id': 101010, 'debit': 0.00, 'credit': 9800.00, 'name': '银行付款'}),
        (0, 0, {'account_id': 400200, 'debit': 0.00, 'credit': 200.00, 'name': '现金折扣收入'})
    ]
}
```

---

*版本：1.0.0*
*适用于：Odoo 16+/17+/18+*
