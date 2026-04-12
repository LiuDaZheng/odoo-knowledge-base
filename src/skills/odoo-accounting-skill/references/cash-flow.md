# 现金流量表 (Cash Flow Statement)

## 报表结构

```
现金流量表
├── 经营活动产生的现金流量
│   ├── 销售商品、提供劳务收到的现金
│   ├── 收到的税费返还
│   ├── 收到其他与经营活动有关的现金
│   ├── 现金流入小计
│   ├── 购买商品、接受劳务支付的现金
│   ├── 支付给职工以及为职工支付的现金
│   ├── 支付的各项税费
│   ├── 支付其他与经营活动有关的现金
│   ├── 现金流出小计
│   └── 经营活动产生的现金流量净额
├── 投资活动产生的现金流量
│   ├── 收回投资收到的现金
│   ├── 取得投资收益收到的现金
│   ├── 处置固定资产、无形资产和其他长期资产收回的现金净额
│   ├── 现金流入小计
│   ├── 购建固定资产、无形资产和其他长期资产支付的现金
│   ├── 投资支付的现金
│   ├── 现金流出小计
│   └── 投资活动产生的现金流量净额
├── 筹资活动产生的现金流量
│   ├── 吸收投资收到的现金
│   ├── 取得借款收到的现金
│   ├── 现金流入小计
│   ├── 偿还债务支付的现金
│   ├── 分配股利、利润或偿付利息支付的现金
│   ├── 现金流出小计
│   └── 筹资活动产生的现金流量净额
├── 汇率变动对现金及现金等价物的影响
├── 现金及现金等价物净增加额
├── 加：期初现金及现金等价物余额
└── 期末现金及现金等价物余额
```

## 编制方法

### 直接法

直接法通过分析现金日记账和银行存款日记账，直接列示各项现金流入和流出。

### 间接法

间接法以净利润为基础，调整不涉及现金的收入、费用、营业外收支等项目。

## 生成现金流量表 (间接法)

```python
def generate_cash_flow_statement(odoo, db, uid, api_key, date_from, date_to):
    """生成现金流量表 (间接法)"""
    
    # 1. 获取净利润
    net_profit = get_net_profit(odoo, db, uid, api_key, date_from, date_to)
    
    # 2. 调整项目
    # 折旧和摊销
    depreciation = get_depreciation(odoo, db, uid, api_key, date_from, date_to)
    
    # 财务费用
    finance_expense = get_finance_expense(odoo, db, uid, api_key, date_from, date_to)
    
    # 投资损失 (减收益)
    investment_loss = get_investment_loss(odoo, db, uid, api_key, date_from, date_to)
    
    # 递延所得税
    deferred_tax = get_deferred_tax(odoo, db, uid, api_key, date_from, date_to)
    
    # 3. 营运资本变动
    # 存货的减少 (减增加)
    inventory_change = get_inventory_change(odoo, db, uid, api_key, date_from, date_to)
    
    # 经营性应收项目的减少 (减增加)
    receivables_change = get_receivables_change(odoo, db, uid, api_key, date_from, date_to)
    
    # 经营性应付项目的增加 (减减少)
    payables_change = get_payables_change(odoo, db, uid, api_key, date_from, date_to)
    
    # 计算经营活动现金流量净额
    operating_cash_flow = (
        net_profit +
        depreciation +
        finance_expense +
        investment_loss +
        deferred_tax +
        inventory_change +
        receivables_change +
        payables_change
    )
    
    # 4. 投资活动现金流量
    investing_inflow = get_investing_inflow(odoo, db, uid, api_key, date_from, date_to)
    investing_outflow = get_investing_outflow(odoo, db, uid, api_key, date_from, date_to)
    investing_cash_flow = investing_inflow - investing_outflow
    
    # 5. 筹资活动现金流量
    financing_inflow = get_financing_inflow(odoo, db, uid, api_key, date_from, date_to)
    financing_outflow = get_financing_outflow(odoo, db, uid, api_key, date_from, date_to)
    financing_cash_flow = financing_inflow - financing_outflow
    
    # 6. 汇总
    net_cash_increase = operating_cash_flow + investing_cash_flow + financing_cash_flow
    
    cash_flow_statement = {
        'period': f"{date_from} 至 {date_to}",
        'operating_activities': {
            'net_profit': net_profit,
            'adjustments': {
                'depreciation': depreciation,
                'finance_expense': finance_expense,
                'investment_loss': investment_loss,
                'deferred_tax': deferred_tax
            },
            'working_capital_changes': {
                'inventory_change': inventory_change,
                'receivables_change': receivables_change,
                'payables_change': payables_change
            },
            'net_cash_flow': operating_cash_flow
        },
        'investing_activities': {
            'inflow': investing_inflow,
            'outflow': investing_outflow,
            'net_cash_flow': investing_cash_flow
        },
        'financing_activities': {
            'inflow': financing_inflow,
            'outflow': financing_outflow,
            'net_cash_flow': financing_cash_flow
        },
        'summary': {
            'net_increase': net_cash_increase,
            'opening_balance': get_opening_cash_balance(odoo, db, uid, api_key, date_from),
            'closing_balance': get_closing_cash_balance(odoo, db, uid, api_key, date_to)
        }
    }
    
    return cash_flow_statement
```

## 辅助函数

```python
def get_depreciation(odoo, db, uid, api_key, date_from, date_to):
    """获取折旧和摊销"""
    domain = [
        ['account_id.code', 'like', '112'],  # 累计折旧
        ['date', '>=', date_from],
        ['date', '<=', date_to],
        ['parent_state', '=', 'posted']
    ]
    lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain])
    return sum(line.get('credit', 0) for line in lines)

def get_receivables_change(odoo, db, uid, api_key, date_from, date_to):
    """获取经营性应收项目变动"""
    # 期初余额
    opening_domain = [
        ['account_type', '=', 'asset_receivable'],
        ['date', '<', date_from]
    ]
    opening = get_account_balance_sum(odoo, db, uid, api_key, opening_domain)
    
    # 期末余额
    closing_domain = [
        ['account_type', '=', 'asset_receivable'],
        ['date', '<=', date_to]
    ]
    closing = get_account_balance_sum(odoo, db, uid, api_key, closing_domain)
    
    # 减少为正，增加为负
    return opening - closing

def get_payables_change(odoo, db, uid, api_key, date_from, date_to):
    """获取经营性应付项目变动"""
    # 期初余额
    opening_domain = [
        ['account_type', '=', 'liability_payable'],
        ['date', '<', date_from]
    ]
    opening = get_account_balance_sum(odoo, db, uid, api_key, opening_domain)
    
    # 期末余额
    closing_domain = [
        ['account_type', '=', 'liability_payable'],
        ['date', '<=', date_to]
    ]
    closing = get_account_balance_sum(odoo, db, uid, api_key, closing_domain)
    
    # 增加为正，减少为负
    return closing - opening

def get_account_balance_sum(odoo, db, uid, api_key, domain):
    """获取科目余额合计"""
    lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain])
    return sum(line.get('debit', 0) - line.get('credit', 0) for line in lines)
```

## 现金流量分析指标

```python
def analyze_cash_flow(cash_flow_statement):
    """现金流量分析"""
    analysis = {
        'ratios': {},
        'health': '',
        'recommendations': []
    }
    
    operating = cash_flow_statement['operating_activities']['net_cash_flow']
    investing = cash_flow_statement['investing_activities']['net_cash_flow']
    financing = cash_flow_statement['financing_activities']['net_cash_flow']
    
    # 现金流量结构分析
    total_cash_flow = operating + investing + financing
    
    if total_cash_flow != 0:
        analysis['ratios']['operating_ratio'] = operating / total_cash_flow * 100
        analysis['ratios']['investing_ratio'] = investing / total_cash_flow * 100
        analysis['ratios']['financing_ratio'] = financing / total_cash_flow * 100
    
    # 健康度评估
    if operating > 0 and investing < 0 and financing < 0:
        analysis['health'] = '健康 - 经营造血能力强，正在投资和偿还债务'
    elif operating > 0 and investing > 0 and financing < 0:
        analysis['health'] = '良好 - 经营良好，处置资产还债'
    elif operating < 0 and financing > 0:
        analysis['health'] = '警示 - 经营亏损，依赖融资'
        analysis['recommendations'].append('经营活动现金流为负，需要改善经营')
    else:
        analysis['health'] = '需要关注'
    
    # 现金再投资比率
    net_assets = get_net_assets()  # 需要从资产负债表获取
    if net_assets:
        analysis['ratios']['reinvestment_ratio'] = (operating - 0) / net_assets * 100
    
    return analysis
```

## 现金流量表模板

| 项目 | 本期金额 | 上期金额 |
|------|----------|----------|
| **一、经营活动产生的现金流量** | | |
| 销售商品、提供劳务收到的现金 | XXX | XXX |
| 收到的税费返还 | XXX | XXX |
| 收到其他与经营活动有关的现金 | XXX | XXX |
| 经营活动现金流入小计 | XXX | XXX |
| 购买商品、接受劳务支付的现金 | XXX | XXX |
| 支付给职工以及为职工支付的现金 | XXX | XXX |
| 支付的各项税费 | XXX | XXX |
| 支付其他与经营活动有关的现金 | XXX | XXX |
| 经营活动现金流出小计 | XXX | XXX |
| **经营活动产生的现金流量净额** | **XXX** | **XXX** |
| **二、投资活动产生的现金流量** | | |
| 收回投资收到的现金 | XXX | XXX |
| 取得投资收益收到的现金 | XXX | XXX |
| 处置固定资产、无形资产收回的现金净额 | XXX | XXX |
| 投资活动现金流入小计 | XXX | XXX |
| 购建固定资产、无形资产支付的现金 | XXX | XXX |
| 投资支付的现金 | XXX | XXX |
| 投资活动现金流出小计 | XXX | XXX |
| **投资活动产生的现金流量净额** | **XXX** | **XXX** |
| **三、筹资活动产生的现金流量** | | |
| 吸收投资收到的现金 | XXX | XXX |
| 取得借款收到的现金 | XXX | XXX |
| 筹资活动现金流入小计 | XXX | XXX |
| 偿还债务支付的现金 | XXX | XXX |
| 分配股利、利润或偿付利息支付的现金 | XXX | XXX |
| 筹资活动现金流出小计 | XXX | XXX |
| **筹资活动产生的现金流量净额** | **XXX** | **XXX** |
| **四、现金及现金等价物净增加额** | **XXX** | **XXX** |
| 加：期初现金及现金等价物余额 | XXX | XXX |
| **五、期末现金及现金等价物余额** | **XXX** | **XXX** |

---

*版本：1.0.0*
*适用于：Odoo 16+/17+/18+*
