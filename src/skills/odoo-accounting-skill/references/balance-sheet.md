# 资产负债表 (Balance Sheet)

## 报表结构

```
资产负债表
├── 资产 (Assets)
│   ├── 流动资产 (Current Assets)
│   └── 非流动资产 (Non-Current Assets)
├── 负债 (Liabilities)
│   ├── 流动负债 (Current Liabilities)
│   └── 非流动负债 (Non-Current Liabilities)
└── 所有者权益 (Equity)
```

## 报表公式

```
资产 = 负债 + 所有者权益
```

## 标准格式

### 资产方

```
流动资产：
  货币资金                                    XXX
  应收账款                                    XXX
  预付账款                                    XXX
  其他应收款                                  XXX
  存货                                        XXX
  其他流动资产                                XXX
流动资产合计                                  XXX

非流动资产：
  固定资产                                    XXX
  减：累计折旧                               (XXX)
  固定资产净值                                XXX
  无形资产                                    XXX
  长期待摊费用                                XXX
  其他非流动资产                              XXX
非流动资产合计                                XXX

资产总计                                      XXX
```

### 负债和权益方

```
流动负债：
  短期借款                                    XXX
  应付账款                                    XXX
  预收账款                                    XXX
  应付职工薪酬                                XXX
  应交税费                                    XXX
  其他应付款                                  XXX
流动负债合计                                  XXX

非流动负债：
  长期借款                                    XXX
  应付债券                                    XXX
  长期应付款                                  XXX
非流动负债合计                                XXX

负债合计                                      XXX

所有者权益：
  实收资本                                    XXX
  资本公积                                    XXX
  盈余公积                                    XXX
  未分配利润                                  XXX
所有者权益合计                                XXX

负债和所有者权益总计                          XXX
```

## 生成资产负债表

```python
def generate_balance_sheet(odoo, db, uid, api_key, as_of_date):
    """生成资产负债表"""
    
    # 资产类科目
    asset_domain = [['account_type', 'like', 'asset']]
    asset_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [asset_domain])
    
    # 负债类科目
    liability_domain = [['account_type', 'like', 'liability']]
    liability_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [liability_domain])
    
    # 权益类科目
    equity_domain = [['account_type', 'like', 'equity']]
    equity_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [equity_domain])
    
    # 计算各类余额
    def get_balance(accounts):
        total = 0
        for acc in accounts:
            # 查询科目余额
            domain = [
                ['account_id', '=', acc['id']],
                ['date', '<=', as_of_date],
                ['parent_state', '=', 'posted']
            ]
            lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain])
            balance = sum(line.get('debit', 0) - line.get('credit', 0) for line in lines)
            total += balance
        return total
    
    total_assets = get_balance(asset_accounts)
    total_liabilities = get_balance(liability_accounts)
    total_equity = get_balance(equity_accounts)
    
    balance_sheet = {
        'date': as_of_date,
        'assets': {
            'total': total_assets,
            'accounts': asset_accounts
        },
        'liabilities': {
            'total': total_liabilities,
            'accounts': liability_accounts
        },
        'equity': {
            'total': total_equity,
            'accounts': equity_accounts
        },
        'check': {
            'balanced': abs(total_assets - (total_liabilities + total_equity)) < 0.01,
            'difference': total_assets - (total_liabilities + total_equity)
        }
    }
    
    return balance_sheet
```

## 科目映射表

| 报表项目 | Odoo 科目类型 | 科目代码范围 |
|----------|--------------|--------------|
| 货币资金 | asset_current | 101xxx |
| 应收账款 | asset_receivable | 102xxx |
| 预付账款 | asset_current | 103xxx |
| 存货 | asset_current | 105xxx |
| 固定资产 | asset_fixed | 111xxx |
| 累计折旧 | asset_fixed (contra) | 112xxx |
| 无形资产 | asset_fixed | 113xxx |
| 短期借款 | liability_current | 201xxx |
| 应付账款 | liability_payable | 202xxx |
| 预收账款 | liability_current | 203xxx |
| 应付职工薪酬 | liability_current | 204xxx |
| 应交税费 | liability_current | 205xxx |
| 长期借款 | liability_non_current | 211xxx |
| 实收资本 | equity | 300xxx |
| 未分配利润 | equity | 300300 |

## 报表分析指标

```python
def calculate_financial_ratios(balance_sheet):
    """计算财务比率"""
    assets = balance_sheet['assets']
    liabilities = balance_sheet['liabilities']
    equity = balance_sheet['equity']
    
    # 流动比率 = 流动资产 / 流动负债
    current_ratio = assets['current'] / liabilities['current'] if liabilities['current'] else 0
    
    # 速动比率 = (流动资产 - 存货) / 流动负债
    quick_ratio = (assets['current'] - assets.get('inventory', 0)) / liabilities['current'] if liabilities['current'] else 0
    
    # 资产负债率 = 负债总额 / 资产总额
    debt_ratio = liabilities['total'] / assets['total'] if assets['total'] else 0
    
    # 权益乘数 = 资产总额 / 所有者权益
    equity_multiplier = assets['total'] / equity['total'] if equity['total'] else 0
    
    return {
        'current_ratio': current_ratio,
        'quick_ratio': quick_ratio,
        'debt_ratio': debt_ratio,
        'equity_multiplier': equity_multiplier
    }
```

## 导出报表

```python
def export_balance_sheet_to_excel(balance_sheet, filename):
    """导出资产负债表到 Excel"""
    import openpyxl
    from openpyxl import Workbook
    
    wb = Workbook()
    ws = wb.active
    ws.title = "资产负债表"
    
    # 标题
    ws['A1'] = f"资产负债表 - {balance_sheet['date']}"
    
    # 资产方
    ws['A3'] = "资产"
    ws['B3'] = "金额"
    row = 4
    for acc in balance_sheet['assets']['accounts']:
        ws[f'A{row}'] = acc['name']
        ws[f'B{row}'] = acc.get('balance', 0)
        row += 1
    ws[f'A{row}'] = "资产合计"
    ws[f'B{row}'] = balance_sheet['assets']['total']
    
    # 负债和权益方
    ws['D3'] = "负债和所有者权益"
    ws['E3'] = "金额"
    row = 4
    for acc in balance_sheet['liabilities']['accounts'] + balance_sheet['equity']['accounts']:
        ws[f'D{row}'] = acc['name']
        ws[f'E{row}'] = acc.get('balance', 0)
        row += 1
    ws[f'D{row}'] = "负债和权益合计"
    ws[f'E{row}'] = balance_sheet['liabilities']['total'] + balance_sheet['equity']['total']
    
    wb.save(filename)
```

---

*版本：1.0.0*
*适用于：Odoo 16+/17+/18+*
