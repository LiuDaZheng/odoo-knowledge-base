# 应收管理 (Accounts Receivable - AR)

## AR 工作流程

```
创建客户 → 创建发票 → 发送发票 → 收款登记 → 核销对账 → 账龄分析
```

## 客户发票管理

### 创建客户发票

```python
def create_customer_invoice(odoo, db, uid, api_key, customer_id, invoice_date, lines):
    """创建客户发票"""
    invoice_data = {
        'move_type': 'out_invoice',
        'partner_id': customer_id,
        'invoice_date': invoice_date,
        'invoice_date_due': invoice_date,  # 到期日
        'invoice_line_ids': lines
    }
    invoice_id = odoo.execute_kw(db, uid, api_key, 'account.move', 'create', [invoice_data])
    return invoice_id

# 使用示例
lines = [
    (0, 0, {
        'product_id': 1,
        'name': '产品 A',
        'quantity': 10,
        'price_unit': 100.00,
        'account_id': 401000,  # 收入科目
        'tax_ids': [(6, 0, [1])]  # 税率 ID
    })
]
invoice_id = create_customer_invoice(odoo, db, uid, api_key, customer_id=5, invoice_date='2026-04-12', lines=lines)
```

### 发票状态管理

```python
# 确认发票
odoo.execute_kw(db, uid, api_key, 'account.move', 'action_post', [[invoice_id]])

# 取消发票
odoo.execute_kw(db, uid, api_key, 'account.move', 'action_cancel', [[invoice_id]])

# 重置为草稿
odoo.execute_kw(db, uid, api_key, 'account.move', 'action_reset_to_draft', [[invoice_id]])
```

### 查询应收账款

```python
def get_receivables(odoo, db, uid, api_key, customer_id=None, days_overdue=0):
    """查询应收账款"""
    domain = [
        ['account_type', '=', 'asset_receivable'],
        ['reconciled', '=', False]
    ]
    
    if customer_id:
        domain.append(['partner_id', '=', customer_id])
    
    fields = ['id', 'date', 'date_maturity', 'debit', 'credit', 'balance', 'partner_id', 'move_id']
    amls = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain], {'fields': fields})
    
    # 过滤逾期
    if days_overdue > 0:
        from datetime import datetime, timedelta
        cutoff_date = (datetime.now() - timedelta(days=days_overdue)).strftime('%Y-%m-%d')
        amls = [aml for aml in amls if aml.get('date_maturity') and aml['date_maturity'] < cutoff_date]
    
    return amls
```

## 收款管理

### 创建收款

```python
def create_payment(odoo, db, uid, api_key, partner_id, amount, payment_type, journal_id, payment_date):
    """创建收款/付款"""
    payment_data = {
        'payment_type': payment_type,  # 'inbound' 收款 / 'outbound' 付款
        'partner_id': partner_id,
        'amount': amount,
        'date': payment_date,
        'journal_id': journal_id
    }
    payment_id = odoo.execute_kw(db, uid, api_key, 'account.payment', 'create', [payment_data])
    return payment_id

# 收款示例
payment_id = create_payment(odoo, db, uid, api_key, 
                            partner_id=5, 
                            amount=1130.00, 
                            payment_type='inbound',
                            journal_id=1,  # 银行日记账
                            payment_date='2026-04-12')
```

### 发票与收款核销

```python
def reconcile_invoice_payment(odoo, db, uid, api_key, invoice_id, payment_id):
    """核销发票与收款"""
    # 获取发票的应收明细
    invoice_domain = [['move_id', '=', invoice_id], ['account_type', '=', 'asset_receivable']]
    invoice_lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [invoice_domain])
    
    # 获取收款的应付明细
    payment_domain = [['payment_id', '=', payment_id]]
    payment_lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [payment_domain])
    
    # 执行核销
    if invoice_lines and payment_lines:
        reconcile_data = {
            'to_reconcile': [invoice_lines[0]['id'], payment_lines[0]['id']]
        }
        odoo.execute_kw(db, uid, api_key, 'account.move.line', 'reconcile', [reconcile_data])
```

## AR 账龄分析

### 账龄区间定义

```python
AGING_BUCKETS = [
    {'name': '未到期', 'days_min': 0, 'days_max': 0},
    {'name': '1-30 天', 'days_min': 1, 'days_max': 30},
    {'name': '31-60 天', 'days_min': 31, 'days_max': 60},
    {'name': '61-90 天', 'days_min': 61, 'days_max': 90},
    {'name': '90 天以上', 'days_min': 91, 'days_max': 9999}
]
```

### 生成账龄报告

```python
def generate_ar_aging_report(odoo, db, uid, api_key, as_of_date=None):
    """生成 AR 账龄报告"""
    from datetime import datetime, timedelta
    
    as_of_date = as_of_date or datetime.now()
    
    # 获取所有未核销的应收明细
    domain = [
        ['account_type', '=', 'asset_receivable'],
        ['reconciled', '=', False],
        ['parent_state', '=', 'posted']
    ]
    fields = ['id', 'partner_id', 'date_maturity', 'balance', 'debit', 'credit']
    amls = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain], {'fields': fields})
    
    # 按客户汇总
    aging_report = {}
    for aml in amls:
        partner_id = aml['partner_id'][0] if isinstance(aml['partner_id'], list) else aml['partner_id']
        partner_name = aml['partner_id'][1] if isinstance(aml['partner_id'], list) else 'Unknown'
        
        if partner_id not in aging_report:
            aging_report[partner_id] = {
                'name': partner_name,
                'buckets': {b['name']: 0.0 for b in AGING_BUCKETS},
                'total': 0.0
            }
        
        # 计算逾期天数
        days_overdue = 0
        if aml.get('date_maturity'):
            maturity_date = datetime.strptime(aml['date_maturity'], '%Y-%m-%d')
            days_overdue = (as_of_date - maturity_date).days
        
        # 分配到对应区间
        balance = aml.get('balance', 0) or (aml.get('debit', 0) - aml.get('credit', 0))
        for bucket in AGING_BUCKETS:
            if bucket['days_min'] <= days_overdue <= bucket['days_max']:
                aging_report[partner_id]['buckets'][bucket['name']] += balance
                break
        
        aging_report[partner_id]['total'] += balance
    
    return aging_report
```

## 催收管理

### 发送催款提醒

```python
def send_payment_reminder(odoo, db, uid, api_key, customer_id, invoice_ids):
    """发送催款提醒"""
    # 获取客户邮箱
    customer = odoo.execute_kw(db, uid, api_key, 'res.partner', 'read', [[customer_id], {'fields': ['email']}])
    email = customer[0].get('email')
    
    if email:
        # 创建邮件
        mail_data = {
            'subject': '付款提醒 - 发票逾期',
            'body_html': f'<p>尊敬的客户，您的发票已逾期，请及时付款。</p>',
            'email_to': email,
            'model': 'account.move',
            'res_id': invoice_ids[0]
        }
        mail_id = odoo.execute_kw(db, uid, api_key, 'mail.mail', 'create', [mail_data])
        
        # 发送邮件
        odoo.execute_kw(db, uid, api_key, 'mail.mail', 'send', [[mail_id]])
```

### 客户信用管理

```python
# 设置客户信用额度
customer_data = {
    'credit': 50000.00,  # 信用额度
    'credit_limit': 50000.00,
    'payment_term_id': 1  # 付款条件
}
odoo.execute_kw(db, uid, api_key, 'res.partner', 'write', [[customer_id, customer_data]])

# 检查信用额度
def check_credit_limit(odoo, db, uid, api_key, customer_id, new_amount):
    """检查是否超出信用额度"""
    customer = odoo.execute_kw(db, uid, api_key, 'res.partner', 'read', [[customer_id], {'fields': ['credit', 'credit_limit']}])
    
    current_receivable = customer[0].get('credit', 0)
    credit_limit = customer[0].get('credit_limit', 0)
    
    if current_receivable + new_amount > credit_limit:
        return False, f'超出信用额度：当前={current_receivable}, 新增={new_amount}, 限额={credit_limit}'
    
    return True, '信用额度充足'
```

## 常见场景

### 场景 1：预收款处理

```python
# 收到预收款
payment_data = {
    'payment_type': 'inbound',
    'partner_id': customer_id,
    'amount': 5000.00,
    'date': '2026-04-01',
    'journal_id': 1
}
payment_id = odoo.execute_kw(db, uid, api_key, 'account.payment', 'create', [payment_data])

# 创建预收科目分录
entry_data = {
    'journal_id': 1,
    'date': '2026-04-01',
    'line_ids': [
        (0, 0, {'account_id': 101010, 'debit': 5000.00, 'credit': 0.00, 'name': '预收款'}),
        (0, 0, {'account_id': 203000, 'debit': 0.00, 'credit': 5000.00, 'name': '预收账款'})
    ]
}
```

### 场景 2：坏账处理

```python
# 确认坏账
bad_debt_data = {
    'journal_id': 4,
    'date': '2026-04-30',
    'line_ids': [
        (0, 0, {'account_id': 500500, 'debit': 1000.00, 'credit': 0.00, 'name': '坏账损失'}),
        (0, 0, {'account_id': 102001, 'debit': 0.00, 'credit': 1000.00, 'name': '核销应收账款'})
    ]
}
```

---

*版本：1.0.0*
*适用于：Odoo 16+/17+/18+*
