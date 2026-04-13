#!/usr/bin/env python3
"""
Odoo 会计科目批量导入工具

用法:
    python import_accounts.py --file accounts.csv --company 1
    python import_accounts.py --file accounts.xlsx --company 1 --dry-run

CSV 格式:
    code,name,account_type,reconcile,currency_id
    101001，现金 - 人民币，asset_current,True,1
    102001，应收账款 - 国内客户，asset_receivable,True,1
"""

import csv
import argparse
import sys
from typing import List, Dict

try:
    import xmlrpc.client
except ImportError:
    print("请安装 xmlrpc 库：pip install xmlrpc")
    sys.exit(1)


def connect_to_odoo(url: str, db: str, api_key: str, uid: int):
    """连接到 Odoo"""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # 验证连接
    user_id = common.authenticate(db, api_key, {})
    if not user_id:
        raise Exception("认证失败，请检查 API 密钥")
    
    return models, db, user_id, api_key


def read_csv_file(filepath: str) -> List[Dict]:
    """读取 CSV 文件"""
    accounts = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append({
                'code': row['code'],
                'name': row['name'],
                'account_type': row['account_type'],
                'reconcile': row.get('reconcile', 'False').lower() == 'true',
                'currency_id': int(row.get('currency_id', 1))
            })
    return accounts


def import_accounts(models, db, uid, api_key, accounts: List[Dict], company_id: int = 1, dry_run: bool = False):
    """导入会计科目"""
    results = {
        'success': 0,
        'failed': 0,
        'skipped': 0,
        'errors': []
    }
    
    for idx, account in enumerate(accounts, 1):
        print(f"[{idx}/{len(accounts)}] 处理科目：{account['code']} - {account['name']}")
        
        if dry_run:
            print(f"  ✓ [DRY RUN] 将创建科目")
            results['success'] += 1
            continue
        
        try:
            # 检查科目是否已存在
            domain = [['code', '=', account['code']], ['company_id', '=', company_id]]
            existing = models.execute_kw(db, uid, api_key, 'account.account', 'search', [domain])
            
            if existing:
                print(f"  ⚠ 科目已存在，跳过")
                results['skipped'] += 1
                continue
            
            # 创建科目
            account_data = {
                'code': account['code'],
                'name': account['name'],
                'account_type': account['account_type'],
                'company_id': company_id,
                'reconcile': account['reconcile'],
                'currency_id': account['currency_id']
            }
            
            account_id = models.execute_kw(db, uid, api_key, 'account.account', 'create', [account_data])
            print(f"  ✓ 创建成功，ID: {account_id}")
            results['success'] += 1
            
        except Exception as e:
            print(f"  ✗ 失败：{str(e)}")
            results['failed'] += 1
            results['errors'].append({
                'account': account['code'],
                'error': str(e)
            })
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Odoo 会计科目批量导入工具')
    parser.add_argument('--file', '-f', required=True, help='CSV 文件路径')
    parser.add_argument('--company', '-c', type=int, default=1, help='公司 ID')
    parser.add_argument('--url', '-u', default='https://your-company.odoo.com', help='Odoo URL')
    parser.add_argument('--db', '-d', required=True, help='数据库名称')
    parser.add_argument('--api-key', '-k', required=True, help='API 密钥')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不实际导入')
    
    args = parser.parse_args()
    
    print(f"=== Odoo 会计科目导入工具 ===")
    print(f"文件：{args.file}")
    print(f"公司 ID: {args.company}")
    print(f"Odoo URL: {args.url}")
    print(f"数据库：{args.db}")
    print(f"试运行：{'是' if args.dry_run else '否'}")
    print()
    
    try:
        # 连接 Odoo
        print("正在连接 Odoo...")
        models, db, uid, api_key = connect_to_odoo(args.url, args.db, args.api_key, 0)
        print("✓ 连接成功\n")
        
        # 读取 CSV
        print("正在读取 CSV 文件...")
        accounts = read_csv_file(args.file)
        print(f"✓ 读取 {len(accounts)} 个科目\n")
        
        # 导入科目
        print("开始导入科目...")
        results = import_accounts(models, db, uid, args.api_key, accounts, args.company, args.dry_run)
        
        # 输出结果
        print("\n=== 导入结果 ===")
        print(f"成功：{results['success']}")
        print(f"跳过：{results['skipped']}")
        print(f"失败：{results['failed']}")
        
        if results['errors']:
            print("\n错误详情:")
            for error in results['errors']:
                print(f"  - {error['account']}: {error['error']}")
        
        sys.exit(0 if results['failed'] == 0 else 1)
        
    except Exception as e:
        print(f"\n✗ 错误：{str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
