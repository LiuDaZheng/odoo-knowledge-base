#!/usr/bin/env python3
"""
Odoo 采购管理脚本

提供供应商、采购订单、收货、分析功能。

用法:
    python3 purchase.py <module> <action> [options]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'odoo-crm-skill', 'scripts'))
from odoo_client import create_client, OdooClient


def cmd_vendor_create(client: OdooClient, args):
    """创建供应商"""
    values = {
        "name": args.name,
        "supplier_rank": 1,  # 标记为供应商
    }
    
    if args.email:
        values["email"] = args.email
    if args.phone:
        values["phone"] = args.phone
    if args.website:
        values["website"] = args.website
    
    vendor_id = client.create("res.partner", values)
    print(f"✅ 供应商创建成功！ID: {vendor_id}")
    return vendor_id


def cmd_vendor_list(client: OdooClient, args):
    """查看供应商列表"""
    domain = [["supplier_rank", ">", 0]]
    
    vendors = client.search_read(
        "res.partner",
        domain,
        fields=["id", "name", "email", "phone", "website"],
        limit=args.limit or 50
    )
    
    print(f"\n🏭 供应商列表 (共 {len(vendors)} 条)\n")
    for v in vendors:
        print(f"ID: {v['id']} - {v['name']} ({v.get('email', 'N/A')})")
    
    return vendors


def cmd_vendor_search(client: OdooClient, args):
    """搜索供应商"""
    domain = [
        ["supplier_rank", ">", 0],
        ["|", ["name", "ilike", args.query], ["email", "ilike", args.query]]
    ]
    
    vendors = client.search_read("res.partner", domain, fields=["id", "name", "email"], limit=args.limit or 20)
    
    print(f"\n🔍 供应商搜索：'{args.query}' (共 {len(vendors)} 条)\n")
    for v in vendors:
        print(f"ID: {v['id']} - {v['name']}")
    
    return vendors


def cmd_vendor_rate(client: OdooClient, args):
    """供应商评估"""
    print(f"📊 正在评估供应商 {args.vendor_id}...")
    # TODO: 实现评估逻辑
    print(f"   质量评分：{args.quality}/5")
    print(f"   交货评分：{args.delivery}/5")
    print(f"   服务评分：{args.service}/5")
    return True


def cmd_requisition_create(client: OdooClient, args):
    """创建采购申请"""
    print(f"📝 正在创建采购申请...")
    # TODO: 实现采购申请
    return True


def cmd_requisition_approve(client: OdooClient, args):
    """审批采购申请"""
    print(f"✅ 正在审批采购申请 {args.requisition_id}...")
    return True


def cmd_order_create(client: OdooClient, args):
    """创建采购订单"""
    values = {
        "partner_id": args.partner_id,
        "date_order": args.date_order,
    }
    
    order_id = client.create("purchase.order", values)
    print(f"✅ 采购订单创建成功！ID: {order_id}")
    
    if args.lines:
        lines = parse_order_lines(args.lines)
        for line in lines:
            client.create("purchase.order.line", {
                "order_id": order_id,
                "product_id": line["product_id"],
                "product_qty": line["qty"],
                "price_unit": line["price"],
            })
        print(f"   已添加 {len(lines)} 个产品行")
    
    return order_id


def cmd_order_list(client: OdooClient, args):
    """查看采购订单"""
    domain = []
    if args.state:
        domain.append(["state", "=", args.state])
    if args.partner_id:
        domain.append(["partner_id", "=", args.partner_id])
    
    orders = client.search_read(
        "purchase.order",
        domain,
        fields=["id", "name", "partner_id", "date_order", "state", "amount_total"],
        limit=args.limit or 50
    )
    
    print(f"\n📦 采购订单列表 (共 {len(orders)} 条)\n")
    for o in orders:
        partner = o.get("partner_id", [None, "N/A"])
        partner_name = partner[1] if isinstance(partner, list) else "N/A"
        print(f"ID: {o['id']} - {o.get('name', 'N/A')} - 供应商：{partner_name} - 总额：¥{o.get('amount_total', 0):,.2f}")
    
    return orders


def cmd_order_confirm(client: OdooClient, args):
    """确认采购订单"""
    print(f"✅ 正在确认采购订单 {args.order_id}...")
    client.execute("purchase.order", "button_confirm", [[args.order_id]])
    print("   订单已确认")
    return True


def cmd_receipt_create(client: OdooClient, args):
    """创建收货单"""
    print(f"📥 正在为订单 {args.order_id} 创建收货单...")
    # TODO: 实现收货单创建
    return True


def cmd_receipt_validate(client: OdooClient, args):
    """确认收货"""
    print(f"✅ 正在确认收货单 {args.picking_id}...")
    client.execute("stock.picking", "button_validate", [[args.picking_id]])
    print("   收货已确认")
    return True


def cmd_report_by_vendor(client: OdooClient, args):
    """按供应商分析"""
    print("📊 供应商采购分析报表")
    # TODO: 实现分析
    return True


def cmd_report_spend_analysis(client: OdooClient, args):
    """支出分析"""
    print("📊 采购支出分析")
    # TODO: 实现分析
    return True


def parse_order_lines(lines_str: str):
    lines = []
    for line in lines_str.split(","):
        parts = line.split(":")
        if len(parts) >= 3:
            lines.append({
                "product_id": parts[0],
                "qty": float(parts[1]),
                "price": float(parts[2]),
            })
    return lines


def main():
    parser = argparse.ArgumentParser(description="Odoo 采购管理脚本")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--verbose", action="store_true")
    
    subparsers = parser.add_subparsers(dest="module")
    
    # Vendor
    vendor = subparsers.add_parser("vendor", help="供应商管理")
    vendor_sub = vendor.add_subparsers(dest="action")
    
    vendor_create = vendor_sub.add_parser("create", help="创建供应商")
    vendor_create.add_argument("--name", required=True)
    vendor_create.add_argument("--email", help="邮箱")
    vendor_create.add_argument("--phone", help="电话")
    vendor_create.add_argument("--website", help="网站")
    vendor_create.set_defaults(func=cmd_vendor_create)
    
    vendor_list = vendor_sub.add_parser("list", help="查看供应商")
    vendor_list.add_argument("--limit", type=int)
    vendor_list.set_defaults(func=cmd_vendor_list)
    
    vendor_search = vendor_sub.add_parser("search", help="搜索供应商")
    vendor_search.add_argument("--query", required=True)
    vendor_search.add_argument("--limit", type=int)
    vendor_search.set_defaults(func=cmd_vendor_search)
    
    vendor_rate = vendor_sub.add_parser("rate", help="供应商评估")
    vendor_rate.add_argument("vendor_id", type=int)
    vendor_rate.add_argument("--quality", type=int, default=3)
    vendor_rate.add_argument("--delivery", type=int, default=3)
    vendor_rate.add_argument("--service", type=int, default=3)
    vendor_rate.set_defaults(func=cmd_vendor_rate)
    
    # Requisition
    req = subparsers.add_parser("requisition", help="采购申请")
    req_sub = req.add_subparsers(dest="action")
    
    req_create = req_sub.add_parser("create", help="创建申请")
    req_create.add_argument("--origin", help="来源")
    req_create.add_argument("--lines", help="产品行")
    req_create.add_argument("--date_deadline", help="截止日期")
    req_create.set_defaults(func=cmd_requisition_create)
    
    req_approve = req_sub.add_parser("approve", help="审批申请")
    req_approve.add_argument("requisition_id", type=int)
    req_approve.set_defaults(func=cmd_requisition_approve)
    
    # Order
    order = subparsers.add_parser("order", help="采购订单")
    order_sub = order.add_subparsers(dest="action")
    
    order_create = order_sub.add_parser("create", help="创建订单")
    order_create.add_argument("--partner_id", type=int, required=True)
    order_create.add_argument("--lines", help="产品行")
    order_create.add_argument("--date_order", help="订单日期")
    order_create.set_defaults(func=cmd_order_create)
    
    order_list = order_sub.add_parser("list", help="查看订单")
    order_list.add_argument("--state", help="状态")
    order_list.add_argument("--partner_id", type=int)
    order_list.add_argument("--limit", type=int)
    order_list.set_defaults(func=cmd_order_list)
    
    order_confirm = order_sub.add_parser("confirm", help="确认订单")
    order_confirm.add_argument("order_id", type=int)
    order_confirm.set_defaults(func=cmd_order_confirm)
    
    # Receipt
    receipt = subparsers.add_parser("receipt", help="采购收货")
    receipt_sub = receipt.add_subparsers(dest="action")
    
    receipt_create = receipt_sub.add_parser("create", help="创建收货单")
    receipt_create.add_argument("order_id", type=int)
    receipt_create.set_defaults(func=cmd_receipt_create)
    
    receipt_validate = receipt_sub.add_parser("validate", help="确认收货")
    receipt_validate.add_argument("picking_id", type=int)
    receipt_validate.set_defaults(func=cmd_receipt_validate)
    
    # Report
    report = subparsers.add_parser("report", help="采购分析")
    report_sub = report.add_subparsers(dest="action")
    
    report_vendor = report_sub.add_parser("by-vendor", help="按供应商分析")
    report_vendor.add_argument("--date_from", help="开始日期")
    report_vendor.add_argument("--date_to", help="结束日期")
    report_vendor.set_defaults(func=cmd_report_by_vendor)
    
    report_spend = report_sub.add_parser("spend-analysis", help="支出分析")
    report_spend.set_defaults(func=cmd_report_spend_analysis)
    
    args = parser.parse_args()
    
    if not args.module or not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    try:
        client = create_client(args.config)
        args.func(client, args)
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
