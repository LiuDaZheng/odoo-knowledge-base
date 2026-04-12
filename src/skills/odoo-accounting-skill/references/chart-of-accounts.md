# 会计科目表 (Chart of Accounts)

## 标准科目结构

### 资产类 (1xxxx)

```
100000 - 流动资产
  101000 - 货币资金
    101001 - 现金 - 人民币
    101002 - 现金 - 美元
    101010 - 银行存款 - 工商银行
    101020 - 银行存款 - 建设银行
  102000 - 应收账款
    102001 - 应收账款 - 国内客户
    102002 - 应收账款 - 国外客户
  103000 - 预付账款
  104000 - 其他应收款
  105000 - 存货
    105001 - 原材料
    105002 - 在产品
    105003 - 库存商品

110000 - 非流动资产
  111000 - 固定资产
    111001 - 房屋建筑物
    111002 - 机器设备
    111003 - 运输工具
    111004 - 电子设备
  112000 - 累计折旧
  113000 - 无形资产
  114000 - 长期待摊费用
```

### 负债类 (2xxxx)

```
200000 - 流动负债
  201000 - 短期借款
  202000 - 应付账款
    202001 - 应付账款 - 国内供应商
    202002 - 应付账款 - 国外供应商
  203000 - 预收账款
  204000 - 应付职工薪酬
  205000 - 应交税费
    205001 - 应交增值税
    205002 - 应交企业所得税
    205003 - 应交个人所得税
  206000 - 其他应付款

210000 - 非流动负债
  211000 - 长期借款
  212000 - 应付债券
  213000 - 长期应付款
```

### 所有者权益类 (3xxxx)

```
300000 - 实收资本
  301000 - 国家资本
  302000 - 法人资本
  303000 - 个人资本
300100 - 资本公积
300200 - 盈余公积
300300 - 未分配利润
```

### 收入类 (4xxxx)

```
400000 - 主营业务收入
  401000 - 产品销售收入
  402000 - 服务收入
400100 - 其他业务收入
400200 - 营业外收入
```

### 费用类 (5xxxx)

```
500000 - 主营业务成本
500100 - 税金及附加
500200 - 销售费用
  502001 - 工资及福利
  502002 - 差旅费
  502003 - 业务招待费
  502004 - 广告费
500300 - 管理费用
  503001 - 工资及福利
  503002 - 办公费
  503003 - 折旧费
  503004 - 研发费用
500400 - 财务费用
  504001 - 利息支出
  504002 - 手续费
500500 - 营业外支出
```

## Odoo 科目类型映射

| Odoo 类型 | 代码 | 对应类别 |
|-----------|------|----------|
| asset_fixed | 固定资产 | 111xxx |
| asset_current | 流动资产 | 10xxxx |
| asset_receivable | 应收账款 | 102xxx |
| liability_payable | 应付账款 | 202xxx |
| liability_credit_card | 信用卡负债 | 201xxx |
| liability_current | 流动负债 | 20xxxx |
| liability_non_current | 非流动负债 | 21xxxx |
| equity | 所有者权益 | 30xxxx |
| income | 收入 | 40xxxx |
| expense | 费用 | 50xxxx |
| expense_depreciation | 折旧费用 | 503003 |

## 科目创建模板

```python
def create_account(odoo, db, uid, api_key, code, name, account_type, company_id=1):
    """创建会计科目"""
    account_data = {
        'code': code,
        'name': name,
        'account_type': account_type,
        'company_id': company_id,
        'reconcile': account_type in ['asset_receivable', 'liability_payable'],
        'currency_id': 1  # 本位币
    }
    return odoo.execute_kw(db, uid, api_key, 'account.account', 'create', [account_data])

# 使用示例
create_account(odoo, db, uid, api_key, '101001', '现金 - 人民币', 'asset_current')
create_account(odoo, db, uid, api_key, '102001', '应收账款 - 国内客户', 'asset_receivable')
create_account(odoo, db, uid, api_key, '202001', '应付账款 - 国内供应商', 'liability_payable')
```

## 科目余额查询

```python
def get_account_balance(odoo, db, uid, api_key, account_id, date_from, date_to):
    """查询科目余额"""
    domain = [
        ['account_id', '=', account_id],
        ['date', '>=', date_from],
        ['date', '<=', date_to],
        ['parent_state', '=', 'posted']
    ]
    fields = ['debit', 'credit', 'balance', 'date', 'move_id']
    lines = odoo.execute_kw(db, uid, api_key, 'account.move.line', 'search_read', [domain], {'fields': fields})
    
    total_debit = sum(line['debit'] for line in lines)
    total_credit = sum(line['credit'] for line in lines)
    balance = total_debit - total_credit
    
    return {
        'account_id': account_id,
        'debit': total_debit,
        'credit': total_credit,
        'balance': balance,
        'line_count': len(lines)
    }
```

## 科目辅助核算

```python
# 启用辅助核算的科目配置
analytic_account_data = {
    'name': '部门 A',
    'code': 'DEPT-A',
    'company_id': 1
}
analytic_id = odoo.execute_kw(db, uid, api_key, 'account.analytic.account', 'create', [analytic_account_data])

# 在分录中应用辅助核算
line_data = {
    'account_id': 503001,
    'debit': 1000.00,
    'analytic_distribution': {
        str(analytic_id): 100.0  # 100% 计入部门 A
    }
}
```

---

*版本：1.0.0*
*适用于：Odoo 16+/17+/18+*
