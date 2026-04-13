#!/usr/bin/env python3
"""
Odoo BOM 批量导入工具

用法:
    python import_boms.py --file boms.csv --company 1
"""

import csv
import argparse
import sys
import xmlrpc.client


def connect_to_odoo(url, db, api_key):
    """连接到 Odoo"""
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    user_id = common.authenticate(db, api_key, {})
    if not user_id:
        raise Exception("认证失败")
    
    return models, db, user_id, api_key


def import_boms(models, db, uid, api_key, filepath, company_id=1):
    """导入 BOM"""
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            bom_data = {
                'product_tmpl_id': int(row['product_tmpl_id']),
                'type': row.get('type', 'normal'),
                'bom_line_ids': []
            }
            
            # 解析组件行 (格式：component_id:qty:uom_id)
            if 'components' in row:
                components = row['components'].split(';')
                for idx, comp in enumerate(components):
                    parts = comp.split(':')
                    if len(parts) >= 2:
                        bom_data['bom_line_ids'].append((0, 0, {
                            'product_id': int(parts[0]),
                            'product_qty': float(parts[1]),
                            'product_uom_id': int(parts[2]) if len(parts) > 2 else 1,
                            'sequence': (idx + 1) * 10
                        }))
            
            bom_id = models.execute_kw(db, uid, api_key, 'mrp.bom', 'create', [bom_data])
            print(f"✓ 创建 BOM: {bom_id}")


def main():
    parser = argparse.ArgumentParser(description='Odoo BOM 批量导入工具')
    parser.add_argument('--file', '-f', required=True, help='CSV 文件路径')
    parser.add_argument('--company', '-c', type=int, default=1, help='公司 ID')
    parser.add_argument('--url', '-u', required=True, help='Odoo URL')
    parser.add_argument('--db', '-d', required=True, help='数据库名称')
    parser.add_argument('--api-key', '-k', required=True, help='API 密钥')
    
    args = parser.parse_args()
    
    try:
        models, db, uid, api_key = connect_to_odoo(args.url, args.db, args.api_key)
        import_boms(models, db, uid, api_key, args.file, args.company)
        print("✓ 导入完成")
    except Exception as e:
        print(f"✗ 错误：{str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
