# 利润表 (Income Statement)

## 报表结构

```
利润表
├── 营业收入
│   ├── 主营业务收入
│   └── 其他业务收入
├── 营业成本
│   ├── 主营业务成本
│   └── 其他业务成本
├── 毛利润
├── 营业费用
│   ├── 销售费用
│   ├── 管理费用
│   └── 财务费用
├── 营业利润
├── 营业外收支
├── 利润总额
├── 所得税费用
└── 净利润
```

## 报表公式

```
毛利润 = 营业收入 - 营业成本
营业利润 = 毛利润 - 营业费用
利润总额 = 营业利润 + 营业外收入 - 营业外支出
净利润 = 利润总额 - 所得税费用
```

## 标准格式

```
一、营业收入                                    XXX
  减：营业成本                                 (XXX)
      税金及附加                               (XXX)
      销售费用                                 (XXX)
      管理费用                                 (XXX)
      财务费用                                 (XXX)
      研发费用                                 (XXX)
      资产减值损失                             (XXX)
  加：其他收益                                  XXX
      投资收益                                  XXX
      公允价值变动收益                          XXX
      资产处置收益                              XXX

二、营业利润                                    XXX
  加：营业外收入                                XXX
  减：营业外支出                               (XXX)

三、利润总额                                    XXX
  减：所得税费用                               (XXX)

四、净利润                                      XXX

五、每股收益：
  (一) 基本每股收益                             XXX
  (二) 稀释每股收益                             XXX
```

## 生成利润表

```python
def generate_income_statement(odoo, db, uid, api_key, date_from, date_to):
    """生成利润表"""
    
    # 收入类科目
    revenue_domain = [['account_type', 'like', 'revenue']]
    revenue_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [revenue_domain])
    
    # 成本类科目
    cogs_domain = [['code', 'like', '500000']]  # 主营业务成本
    cogs_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [cogs_domain])
    
    # 费用类科目
    expense_domain = [['account_type', 'like', 'expense']]
    expense_accounts = odoo.execute_kw(db, uid, api_key, 'account.account', 'search_read', [expense_domain])
    
    # 查询期间发生额
    def get_period_balance(accounts, date_from, date_to):
        total = 0
        for acc in accounts:
            domain = [
                ['account_id', '=', acc['id']],
                ['date', '>=', date_from],
                ['date', '<=', date_to],
                ['parent_state', '=', 'posted']
            ]
            lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain])
            # 收入类贷方为正，费用类借方为正
            if acc['account_type'].startswith('income') or acc['account_type'].startswith('revenue'):
                balance = sum(line.get('credit', 0) - line.get('debit', 0) for line in lines)
            else:
                balance = sum(line.get('debit', 0) - line.get('credit', 0) for line in lines)
            total += balance
        return total
    
    total_revenue = get_period_balance(revenue_accounts, date_from, date_to)
    total_cogs = get_period_balance(cogs_accounts, date_from, date_to)
    total_expenses = get_period_balance(expense_accounts, date_from, date_to)
    
    # 计算利润
    gross_profit = total_revenue - total_cogs
    operating_profit = gross_profit - total_expenses
    
    # 假设所得税率 25%
    tax_rate = 0.25
    income_tax = operating_profit * tax_rate if operating_profit > 0 else 0
    net_profit = operating_profit - income_tax
    
    income_statement = {
        'period': f"{date_from} 至 {date_to}",
        'revenue': {
            'total': total_revenue,
            'accounts': revenue_accounts
        },
        'cogs': {
            'total': total_cogs,
            'accounts': cogs_accounts
        },
        'gross_profit': gross_profit,
        'expenses': {
            'total': total_expenses,
            'accounts': expense_accounts
        },
        'operating_profit': operating_profit,
        'income_tax': income_tax,
        'net_profit': net_profit,
        'margin': {
            'gross_margin': (gross_profit / total_revenue * 100) if total_revenue else 0,
            'operating_margin': (operating_profit / total_revenue * 100) if total_revenue else 0,
            'net_margin': (net_profit / total_revenue * 100) if total_revenue else 0
        }
    }
    
    return income_statement
```

## 科目分类

| 费用类别 | Odoo 科目代码 | 说明 |
|----------|--------------|------|
| 主营业务成本 | 500000 | 直接成本 |
| 税金及附加 | 500100 | 城建税、教育费附加等 |
| 销售费用 | 500200 | 销售部门费用 |
| 管理费用 | 500300 | 管理部门费用 |
| 财务费用 | 500400 | 利息、手续费等 |
| 研发费用 | 503004 | 研发支出 |

## 利润表分析

```python
def analyze_income_statement(income_statement):
    """利润表分析"""
    analysis = {
        'profitability': {},
        'trends': {},
        'recommendations': []
    }
    
    # 盈利能力分析
    margin = income_statement['margin']
    
    if margin['gross_margin'] < 20:
        analysis['recommendations'].append('毛利率低于 20%，建议优化成本结构或提高定价')
    elif margin['gross_margin'] > 50:
        analysis['recommendations'].append('毛利率良好，保持竞争优势')
    
    if margin['net_margin'] < 10:
        analysis['recommendations'].append('净利率偏低，建议控制期间费用')
    
    # 费用结构分析
    expenses = income_statement['expenses']
    revenue = income_statement['revenue']['total']
    
    expense_ratio = expenses['total'] / revenue if revenue else 0
    analysis['profitability']['expense_ratio'] = expense_ratio
    
    if expense_ratio > 0.7:
        analysis['recommendations'].append('费用率超过 70%，需要严格控制费用')
    
    return analysis
```

## 多期比较

```python
def compare_income_statements(statements):
    """多期利润表比较"""
    comparison = {
        'periods': [],
        'metrics': {
            'revenue': [],
            'gross_profit': [],
            'operating_profit': [],
            'net_profit': []
        }
    }
    
    for stmt in statements:
        comparison['periods'].append(stmt['period'])
        comparison['metrics']['revenue'].append(stmt['revenue']['total'])
        comparison['metrics']['gross_profit'].append(stmt['gross_profit'])
        comparison['metrics']['operating_profit'].append(stmt['operating_profit'])
        comparison['metrics']['net_profit'].append(stmt['net_profit'])
    
    # 计算增长率
    if len(comparison['periods']) >= 2:
        comparison['growth'] = {
            'revenue_growth': (comparison['metrics']['revenue'][-1] - comparison['metrics']['revenue'][-2]) / comparison['metrics']['revenue'][-2] * 100 if comparison['metrics']['revenue'][-2] else 0,
            'profit_growth': (comparison['metrics']['net_profit'][-1] - comparison['metrics']['net_profit'][-2]) / comparison['metrics']['net_profit'][-2] * 100 if comparison['metrics']['net_profit'][-2] else 0
        }
    
    return comparison
```

---

*版本：1.0.0*
*适用于：Odoo 16+/17+/18+*
