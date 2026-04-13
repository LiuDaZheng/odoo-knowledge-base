#!/usr/bin/env python3
"""
Odoo 财务报表生成工具

用法:
    python generate_financial_reports.py --type balance-sheet --period 2026-04-12 --format pdf
    python generate_financial_reports.py --type income-statement --date-from 2026-01-01 --date-to 2026-03-31
    python generate_financial_reports.py --type cash-flow --quarter Q1 --year 2026
"""

import argparse
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

try:
    import xmlrpc.client
except ImportError:
    print("请安装 xmlrpc 库：pip install xmlrpc")
    sys.exit(1)


def connect_to_odoo(url: str, db: str, api_key: str):
    """连接到 Odoo"""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    user_id = common.authenticate(db, api_key, {})
    if not user_id:
        raise Exception("认证失败")
    
    return models, db, user_id, api_key


def get_quarter_dates(quarter: str, year: int) -> tuple:
    """获取季度日期范围"""
    quarters = {
        'Q1': ('01-01', '03-31'),
        'Q2': ('04-01', '06-30'),
        'Q3': ('07-01', '09-30'),
        'Q4': ('10-01', '12-31')
    }
    
    if quarter not in quarters:
        raise ValueError(f"无效的季度：{quarter}")
    
    start, end = quarters[quarter]
    return f"{year}-{start}", f"{year}-{end}"


def generate_balance_sheet(models, db, uid, api_key, as_of_date: str) -> Dict:
    """生成资产负债表"""
    print(f"生成资产负债表 - 日期：{as_of_date}")
    
    # 获取科目
    asset_domain = [['account_type', 'like', 'asset']]
    liability_domain = [['account_type', 'like', 'liability']]
    equity_domain = [['account_type', 'like', 'equity']]
    
    asset_accounts = models.execute_kw(db, uid, api_key, 'account.account', 'search_read', [asset_domain])
    liability_accounts = models.execute_kw(db, uid, api_key, 'account.account', 'search_read', [liability_domain])
    equity_accounts = models.execute_kw(db, uid, api_key, 'account.account', 'search_read', [equity_domain])
    
    # 简化：实际应查询每个科目的余额
    report = {
        'type': 'balance_sheet',
        'date': as_of_date,
        'assets': {
            'total': sum(acc.get('balance', 0) for acc in asset_accounts),
            'accounts': asset_accounts
        },
        'liabilities': {
            'total': sum(acc.get('balance', 0) for acc in liability_accounts),
            'accounts': liability_accounts
        },
        'equity': {
            'total': sum(acc.get('balance', 0) for acc in equity_accounts),
            'accounts': equity_accounts
        }
    }
    
    # 验证平衡
    report['balanced'] = abs(report['assets']['total'] - (report['liabilities']['total'] + report['equity']['total'])) < 0.01
    
    return report


def generate_income_statement(models, db, uid, api_key, date_from: str, date_to: str) -> Dict:
    """生成利润表"""
    print(f"生成利润表 - 期间：{date_from} 至 {date_to}")
    
    revenue_domain = [['account_type', 'like', 'revenue'], ['date', '>=', date_from], ['date', '<=', date_to]]
    expense_domain = [['account_type', 'like', 'expense'], ['date', '>=', date_from], ['date', '<=', date_to]]
    
    revenue_accounts = models.execute_kw(db, uid, api_key, 'account.account', 'search_read', [revenue_domain])
    expense_accounts = models.execute_kw(db, uid, api_key, 'account.account', 'search_read', [expense_domain])
    
    report = {
        'type': 'income_statement',
        'period': f"{date_from} 至 {date_to}",
        'revenue': {
            'total': sum(acc.get('balance', 0) for acc in revenue_accounts),
            'accounts': revenue_accounts
        },
        'expenses': {
            'total': sum(acc.get('balance', 0) for acc in expense_accounts),
            'accounts': expense_accounts
        },
        'net_profit': sum(acc.get('balance', 0) for acc in revenue_accounts) - sum(acc.get('balance', 0) for acc in expense_accounts)
    }
    
    return report


def generate_cash_flow(models, db, uid, api_key, date_from: str, date_to: str) -> Dict:
    """生成现金流量表"""
    print(f"生成现金流量表 - 期间：{date_from} 至 {date_to}")
    
    # 简化实现
    report = {
        'type': 'cash_flow',
        'period': f"{date_from} 至 {date_to}",
        'operating_activities': {'net_cash_flow': 0},
        'investing_activities': {'net_cash_flow': 0},
        'financing_activities': {'net_cash_flow': 0},
        'net_increase': 0
    }
    
    return report


def export_to_json(report: Dict, filename: str):
    """导出为 JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"✓ 已导出到：{filename}")


def export_to_csv(report: Dict, filename: str):
    """导出为 CSV"""
    import csv
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        if report['type'] == 'balance_sheet':
            writer.writerow(['类别', '科目', '金额'])
            writer.writerow(['资产合计', '', report['assets']['total']])
            for acc in report['assets']['accounts']:
                writer.writerow(['资产', acc['name'], acc.get('balance', 0)])
            writer.writerow(['负债合计', '', report['liabilities']['total']])
            for acc in report['liabilities']['accounts']:
                writer.writerow(['负债', acc['name'], acc.get('balance', 0)])
            writer.writerow(['权益合计', '', report['equity']['total']])
            for acc in report['equity']['accounts']:
                writer.writerow(['权益', acc['name'], acc.get('balance', 0)])
        
        elif report['type'] == 'income_statement':
            writer.writerow(['类别', '科目', '金额'])
            writer.writerow(['收入合计', '', report['revenue']['total']])
            writer.writerow(['费用合计', '', report['expenses']['total']])
            writer.writerow(['净利润', '', report['net_profit']])
    
    print(f"✓ 已导出到：{filename}")


def main():
    parser = argparse.ArgumentParser(description='Odoo 财务报表生成工具')
    parser.add_argument('--type', '-t', required=True, 
                       choices=['balance-sheet', 'income-statement', 'cash-flow'],
                       help='报表类型')
    parser.add_argument('--period', '-p', help='报表日期 (YYYY-MM-DD)')
    parser.add_argument('--date-from', help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--date-to', help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--quarter', '-q', choices=['Q1', 'Q2', 'Q3', 'Q4'], help='季度')
    parser.add_argument('--year', '-y', type=int, default=datetime.now().year, help='年份')
    parser.add_argument('--format', '-f', choices=['json', 'csv'], default='json', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--url', '-u', default='https://your-company.odoo.com', help='Odoo URL')
    parser.add_argument('--db', '-d', required=True, help='数据库名称')
    parser.add_argument('--api-key', '-k', required=True, help='API 密钥')
    
    args = parser.parse_args()
    
    print(f"=== Odoo 财务报表生成工具 ===")
    print(f"报表类型：{args.type}")
    
    try:
        # 连接 Odoo
        print("正在连接 Odoo...")
        models, db, uid, api_key = connect_to_odoo(args.url, args.db, args.api_key)
        print("✓ 连接成功\n")
        
        # 确定日期范围
        if args.type == 'balance-sheet':
            as_of_date = args.period or datetime.now().strftime('%Y-%m-%d')
            report = generate_balance_sheet(models, db, uid, api_key, as_of_date)
        
        elif args.type == 'income-statement':
            if args.quarter:
                date_from, date_to = get_quarter_dates(args.quarter, args.year)
            else:
                date_from = args.date_from or (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                date_to = args.date_to or datetime.now().strftime('%Y-%m-%d')
            report = generate_income_statement(models, db, uid, api_key, date_from, date_to)
        
        elif args.type == 'cash-flow':
            if args.quarter:
                date_from, date_to = get_quarter_dates(args.quarter, args.year)
            else:
                date_from = args.date_from or (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
                date_to = args.date_to or datetime.now().strftime('%Y-%m-%d')
            report = generate_cash_flow(models, db, uid, api_key, date_from, date_to)
        
        # 导出报表
        output_file = args.output or f"{report['type']}_{datetime.now().strftime('%Y%m%d')}.{args.format}"
        
        if args.format == 'json':
            export_to_json(report, output_file)
        elif args.format == 'csv':
            export_to_csv(report, output_file)
        
        print("\n✓ 报表生成完成")
        
    except Exception as e:
        print(f"\n✗ 错误：{str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
