---
name: odoo-accounting-skill
description: Odoo 财务会计 Skill - 提供会计科目管理、日记账分录、应收应付 (AR/AP)、财务报表 (资产负债表、利润表、现金流量表) 功能。Use when working with Odoo accounting modules for: (1) Managing chart of accounts, (2) Creating journal entries, (3) Accounts receivable/payable management, (4) Generating financial reports, (5) Financial analysis and reconciliation.
---

# Odoo 财务会计 Skill

## 快速开始

### 认证配置

```bash
# 设置 Odoo 连接参数
export ODOO_URL="https://your-company.odoo.com"
export ODOO_DB="your_database"
export ODOO_API_KEY="your_api_key"
export ODOO_UID="your_user_id"
```

### 基础用法

```bash
# 查询会计科目
odoo-accounting list-accounts --type asset

# 创建日记账分录
odoo-accounting create-entry --journal "General Journal" --date 2026-04-12

# 生成资产负债表
odoo-accounting generate-report --type balance-sheet --period 2026-Q1
```

## 核心功能

### 1. 会计科目管理 (Chart of Accounts)

#### 查询科目

```python
# 使用 XML-RPC 查询科目
models = ['account.account']
domain = [['company_id', '=', 1]]
fields = ['code', 'name', 'account_type', 'balance']

accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [domain], {'fields': fields})
```

#### 科目类型

| 类型 | 代码范围 | 说明 |
|------|----------|------|
| Asset | 1xxxx | 资产类科目 |
| Liability | 2xxxx | 负债类科目 |
| Equity | 3xxxx | 所有者权益类科目 |
| Revenue | 4xxxx | 收入类科目 |
| Expense | 5xxxx | 费用类科目 |

#### 创建新科目

```python
account_data = {
    'code': '101001',
    'name': '现金 - 人民币',
    'account_type': 'asset_current',
    'company_id': 1,
    'currency_id': 1,
    'reconcile': True
}
account_id = odoo.execute_kw(db, uid, api_key, 'account.account', 'create', [account_data])
```

**详细科目模板**: 参见 [references/chart-of-accounts.md](references/chart-of-accounts.md)

### 2. 日记账分录 (Journal Entries)

#### 创建分录

```python
entry_data = {
    'journal_id': 1,
    'date': '2026-04-12',
    'ref': 'INV/2026/001',
    'line_ids': [
        (0, 0, {
            'account_id': 10,  # 借方科目
            'debit': 1000.00,
            'credit': 0.00,
            'name': '销售收入'
        }),
        (0, 0, {
            'account_id': 20,  # 贷方科目
            'debit': 0.00,
            'credit': 1000.00,
            'name': '应收账款'
        })
    ]
}
entry_id = odoo.execute_kw(db, uid, api_key, 'account.move', 'create', [entry_data])
```

#### 过账分录

```python
# 提交过账
odoo.execute_kw(db, uid, api_key, 'account.move', 'action_post', [[entry_id]])

# 冲销分录
odoo.execute_kw(db, uid, api_key, 'account.move', 'action_reverse', [[entry_id]])
```

#### 查询分录

```python
domain = [
    ['journal_id', '=', 1],
    ['date', '>=', '2026-01-01'],
    ['date', '<=', '2026-03-31'],
    ['state', '=', 'posted']
]
entries = odoo.execute_kw(db, uid, api_key, 'account.move', 'search_read', [domain])
```

**详细分录示例**: 参见 [references/journal-entries.md](references/journal-entries.md)

### 3. 应收管理 (Accounts Receivable - AR)

#### 创建客户发票

```python
invoice_data = {
    'move_type': 'out_invoice',
    'partner_id': customer_id,
    'invoice_date': '2026-04-12',
    'invoice_line_ids': [
        (0, 0, {
            'product_id': product_id,
            'name': '产品名称',
            'quantity': 10,
            'price_unit': 100.00,
            'account_id': revenue_account_id
        })
    ]
}
invoice_id = odoo.execute_kw(db, uid, api_key, 'account.move', 'create', [invoice_data])
```

#### 收款登记

```python
# 创建收款记录
payment_data = {
    'payment_type': 'inbound',
    'partner_id': customer_id,
    'amount': 1000.00,
    'date': '2026-04-12',
    'journal_id': cash_journal_id
}
payment_id = odoo.execute_kw(db, uid, api_key, 'account.payment', 'create', [payment_data])

# 发票与收款核销
odoo.execute_kw(db, uid, api_key, 'account.payment', 'action_post', [[payment_id]])
```

#### 应收账款账龄分析

```python
# 获取 AR 账龄报告
domain = [['account_type', '=', 'asset_receivable'], ['reconcile', '=', True]]
ar_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [domain])

for account in ar_accounts:
    # 查询未核销明细
    domain = [
        ['account_id', '=', account['id']],
        ['reconciled', '=', False]
    ]
    amls = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain])
```

**详细 AR 流程**: 参见 [references/accounts-receivable.md](references/accounts-receivable.md)

### 4. 应付管理 (Accounts Payable - AP)

#### 创建供应商账单

```python
bill_data = {
    'move_type': 'in_invoice',
    'partner_id': vendor_id,
    'invoice_date': '2026-04-12',
    'invoice_line_ids': [
        (0, 0, {
            'product_id': product_id,
            'name': '采购商品',
            'quantity': 5,
            'price_unit': 200.00,
            'account_id': expense_account_id
        })
    ]
}
bill_id = odoo.execute_kw(db, uid, api_key, 'account.move', 'create', [bill_data])
```

#### 付款登记

```python
# 创建付款记录
payment_data = {
    'payment_type': 'outbound',
    'partner_id': vendor_id,
    'amount': 1000.00,
    'date': '2026-04-12',
    'journal_id': bank_journal_id
}
payment_id = odoo.execute_kw(db, uid, api_key, 'account.payment', 'create', [payment_data])
```

#### 应付账款账龄分析

```python
domain = [['account_type', '=', 'liability_payable'], ['reconcile', '=', True]]
ap_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [domain])
```

**详细 AP 流程**: 参见 [references/accounts-payable.md](references/accounts-payable.md)

### 5. 财务报表 (Financial Reports)

#### 资产负债表 (Balance Sheet)

```python
# 查询资产类科目
asset_domain = [['account_type', 'like', 'asset']]
asset_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [asset_domain])

# 查询负债类科目
liability_domain = [['account_type', 'like', 'liability']]
liability_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [liability_domain])

# 查询权益类科目
equity_domain = [['account_type', 'like', 'equity']]
equity_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [equity_domain])
```

**资产负债表模板**: 参见 [references/balance-sheet.md](references/balance-sheet.md)

#### 利润表 (Income Statement)

```python
# 查询收入类科目
revenue_domain = [['account_type', 'like', 'revenue']]
revenue_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [revenue_domain])

# 查询费用类科目
expense_domain = [['account_type', 'like', 'expense']]
expense_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [expense_domain])

# 计算净利润
total_revenue = sum(acc.get('balance', 0) for acc in revenue_accounts)
total_expense = sum(acc.get('balance', 0) for acc in expense_accounts)
net_profit = total_revenue - total_expense
```

**利润表模板**: 参见 [references/income-statement.md](references/income-statement.md)

#### 现金流量表 (Cash Flow Statement)

```python
# 经营活动现金流
operating_domain = [
    ['account_id.account_type', 'like', 'asset_receivable'],
    ['date', '>=', '2026-01-01'],
    ['date', '<=', '2026-03-31']
]
operating_lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [operating_domain])

# 投资活动现金流
investing_domain = [
    ['account_id.account_type', 'like', 'asset_fixed']
]
investing_lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [investing_domain])

# 筹资活动现金流
financing_domain = [
    ['account_id.account_type', 'like', 'equity']
]
financing_lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [financing_domain])
```

**现金流量表模板**: 参见 [references/cash-flow.md](references/cash-flow.md)

## 高级功能

### 多币种处理

```python
# 创建外币分录
entry_data = {
    'journal_id': 1,
    'date': '2026-04-12',
    'currency_id': 2,  # USD
    'line_ids': [
        (0, 0, {
            'account_id': 10,
            'debit': 1000.00,
            'credit': 0.00,
            'amount_currency': 140.00,  # USD 金额
            'currency_id': 2
        })
    ]
}
```

### 辅助核算 (Analytic Accounting)

```python
# 创建带辅助核算的分录
entry_data = {
    'journal_id': 1,
    'date': '2026-04-12',
    'line_ids': [
        (0, 0, {
            'account_id': 10,
            'debit': 1000.00,
            'analytic_distribution': {
                '1': 60.0,  # 部门 A 60%
                '2': 40.0   # 部门 B 40%
            }
        })
    ]
}
```

### 自动对账

```python
# 自动核销
reconcile_model_id = 1  # 对账模型
odoo.execute_kw(db, uid, api_key, 'account.reconcile.model', 'apply_rules', [
    [reconcile_model_id],
    {'active_ids': [move_line_id1, move_line_id2]}
])
```

## 脚本工具

### 批量导入科目

```bash
python scripts/import_accounts.py --file accounts.csv --company 1
```

### 生成财务报表

```bash
python scripts/generate_financial_reports.py --type balance-sheet --period 2026-Q1 --format pdf
```

### 数据导出

```bash
python scripts/export_accounting_data.py --module all --output ./backup/
```

## 最佳实践

### 1. 数据安全

- 定期备份财务数据
- 使用权限控制限制敏感操作
- 启用审计日志追踪所有变更

### 2. 性能优化

- 使用索引优化大额查询
- 定期归档历史数据
- 使用缓存减少重复查询

### 3. 合规性

- 遵循当地会计准则
- 保留完整的审计轨迹
- 定期生成税务报告

## 故障排查

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 分录不平衡 | 借贷金额不等 | 检查 line_ids 借贷方合计 |
| 科目不存在 | 科目 ID 错误 | 先查询科目列表确认 |
| 权限不足 | 用户角色限制 | 检查用户会计权限 |
| 期间已关闭 | 会计期间锁定 | 联系管理员打开期间 |

### 调试技巧

```python
# 启用详细日志
odoo.execute_kw(db, uid, api_key, 'account.move', 'create', [data], {'context': {'tracking_disable': False}})

# 检查权限
user_groups = odoo.execute_kw(db, uid, api_key, 'res.users', 'read', [[uid], {'fields': ['groups_id']}])
```

## 参考资料

- [会计科目模板](references/chart-of-accounts.md)
- [日记账分录示例](references/journal-entries.md)
- [应收管理流程](references/accounts-receivable.md)
- [应付管理流程](references/accounts-payable.md)
- [资产负债表模板](references/balance-sheet.md)
- [利润表模板](references/income-statement.md)
- [现金流量表模板](references/cash-flow.md)

## 支持的 Odoo 版本

- Odoo 16.0 LTS
- Odoo 17.0 LTS
- Odoo 18.0 (最新)

---

*Skill 版本：1.0.0*
*最后更新：2026-04-12*
*维护者：大正*
