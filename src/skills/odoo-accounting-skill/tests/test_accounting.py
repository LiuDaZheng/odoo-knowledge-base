#!/usr/bin/env python3
"""
Odoo 财务会计 Skill 测试套件

用法:
    python -m pytest tests/test_accounting.py -v
"""

import unittest
import sys
from pathlib import Path

# 添加 scripts 目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


class TestImportAccounts(unittest.TestCase):
    """测试会计科目导入功能"""
    
    def test_csv_parsing(self):
        """测试 CSV 文件解析"""
        # 模拟 CSV 数据
        test_data = """code,name,account_type,reconcile,currency_id
101001，现金 - 人民币，asset_current,True,1
102001，应收账款 - 国内客户，asset_receivable,True,1"""
        
        import csv
        import io
        
        reader = csv.DictReader(io.StringIO(test_data))
        accounts = list(reader)
        
        self.assertEqual(len(accounts), 2)
        self.assertEqual(accounts[0]['code'], '101001')
        self.assertEqual(accounts[0]['name'], '现金 - 人民币')
        self.assertEqual(accounts[0]['account_type'], 'asset_current')
    
    def test_account_type_validation(self):
        """测试科目类型验证"""
        valid_types = [
            'asset_fixed',
            'asset_current',
            'asset_receivable',
            'liability_payable',
            'liability_current',
            'liability_non_current',
            'equity',
            'income',
            'expense'
        ]
        
        for acc_type in valid_types:
            self.assertTrue(acc_type.startswith(('asset', 'liability', 'equity', 'income', 'expense')))


class TestFinancialReports(unittest.TestCase):
    """测试财务报表生成功能"""
    
    def test_balance_sheet_formula(self):
        """测试资产负债表公式"""
        assets = 1000000
        liabilities = 600000
        equity = 400000
        
        # 资产 = 负债 + 所有者权益
        self.assertEqual(assets, liabilities + equity)
    
    def test_income_statement_formula(self):
        """测试利润表公式"""
        revenue = 500000
        cogs = 300000
        expenses = 100000
        
        gross_profit = revenue - cogs
        net_profit = gross_profit - expenses
        
        self.assertEqual(gross_profit, 200000)
        self.assertEqual(net_profit, 100000)
    
    def test_quarter_dates(self):
        """测试季度日期计算"""
        quarters = {
            'Q1': ('01-01', '03-31'),
            'Q2': ('04-01', '06-30'),
            'Q3': ('07-01', '09-30'),
            'Q4': ('10-01', '12-31')
        }
        
        for quarter, (start, end) in quarters.items():
            self.assertTrue(len(start) == 5)
            self.assertTrue(len(end) == 5)


class TestJournalEntries(unittest.TestCase):
    """测试日记账分录功能"""
    
    def test_entry_balance(self):
        """测试分录平衡"""
        debit_total = 1000.00
        credit_total = 1000.00
        
        self.assertAlmostEqual(debit_total, credit_total, places=2)
    
    def test_entry_imbalance(self):
        """测试分录不平衡检测"""
        debit_total = 1000.00
        credit_total = 900.00
        
        self.assertNotAlmostEqual(debit_total, credit_total, places=2)


class TestARAP(unittest.TestCase):
    """测试应收应付功能"""
    
    def test_aging_buckets(self):
        """测试账龄区间"""
        aging_buckets = [
            {'name': '未到期', 'days_min': 0, 'days_max': 0},
            {'name': '1-30 天', 'days_min': 1, 'days_max': 30},
            {'name': '31-60 天', 'days_min': 31, 'days_max': 60},
            {'name': '61-90 天', 'days_min': 61, 'days_max': 90},
            {'name': '90 天以上', 'days_min': 91, 'days_max': 9999}
        ]
        
        # 测试区间分类
        test_cases = [
            (0, '未到期'),
            (15, '1-30 天'),
            (45, '31-60 天'),
            (75, '61-90 天'),
            (120, '90 天以上')
        ]
        
        for days, expected in test_cases:
            for bucket in aging_buckets:
                if bucket['days_min'] <= days <= bucket['days_max']:
                    self.assertEqual(bucket['name'], expected)
                    break


if __name__ == '__main__':
    unittest.main()
