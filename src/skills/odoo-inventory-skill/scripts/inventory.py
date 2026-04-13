#!/usr/bin/env python3
"""
Odoo 库存管理脚本

提供入库、出库、调拨、盘点功能。

用法:
    python3 inventory.py <module> <action> [options]
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'odoo-crm-skill', 'scripts'))
from odoo_client import create_client, OdooClient


def cmd_incoming_create(client: OdooClient, args):
    """创建入库单"""
    values = {
        "picking_type_id": 1,  # Incoming
        "partner_id": args.partner_id,
        "scheduled_date": args.scheduled_date,
    }
    
    picking_id = client.create("stock.picking", values)
    print(f"✅ 入库单创建成功！ID: {picking_id}")
    
    if args.lines:
        lines = parse_product_lines(args.lines)
        for line in lines:
            client.create("stock.move", {
                "picking_id": picking_id,
                "product_id": line["product_id"],
                "product_uom_qty": line["qty"],
            })
        print(f"   已添加 {len(lines)} 个产品行")
    
    return picking_id


def cmd_incoming_list(client: OdooClient, args):
    """查看入库单"""
    domain = [["picking_type_code", "=", "incoming"]]
    if args.state:
        domain.append(["state", "=", args.state])
    
    pickings = client.search_read("stock.picking", domain, limit=args.limit or 50)
    
    print(f"\n📥 入库单列表 (共 {len(pickings)} 条)\n")
    for p in pickings:
        print(f"ID: {p['id']} - {p.get('name', 'N/A')} - 状态：{p.get('state', 'N/A')}")
    
    return pickings


def cmd_incoming_validate(client: OdooClient, args):
    """确认入库"""
    print(f"✅ 正在确认入库单 {args.picking_id}...")
    client.execute("stock.picking", "button_validate", [[args.picking_id]])
    print("   入库单已确认")
    return True


def cmd_outgoing_create(client: OdooClient, args):
    """创建出库单"""
    values = {
        "picking_type_id": 2,  # Outgoing
        "partner_id": args.partner_id,
    }
    
    picking_id = client.create("stock.picking", values)
    print(f"✅ 出库单创建成功！ID: {picking_id}")
    
    if args.lines:
        lines = parse_product_lines(args.lines)
        for line in lines:
            client.create("stock.move", {
                "picking_id": picking_id,
                "product_id": line["product_id"],
                "product_uom_qty": line["qty"],
            })
    
    return picking_id


def cmd_outgoing_list(client: OdooClient, args):
    """查看出库单"""
    domain = [["picking_type_code", "=", "outgoing"]]
    if args.state:
        domain.append(["state", "=", args.state])
    
    pickings = client.search_read("stock.picking", domain, limit=args.limit or 50)
    
    print(f"\n📤 出库单列表 (共 {len(pickings)} 条)\n")
    for p in pickings:
        print(f"ID: {p['id']} - {p.get('name', 'N/A')} - 状态：{p.get('state', 'N/A')}")
    
    return pickings


def cmd_outgoing_validate(client: OdooClient, args):
    """确认出库"""
    print(f"✅ 正在确认出库单 {args.picking_id}...")
    client.execute("stock.picking", "button_validate", [[args.picking_id]])
    print("   出库单已确认")
    return True


def cmd_transfer_create(client: OdooClient, args):
    """创建调拨单"""
    values = {
        "picking_type_id": 3,  # Internal
        "location_id": args.location_src_id,
        "location_dest_id": args.location_dest_id,
    }
    
    picking_id = client.create("stock.picking", values)
    print(f"✅ 调拨单创建成功！ID: {picking_id}")
    
    if args.lines:
        lines = parse_product_lines(args.lines)
        for line in lines:
            client.create("stock.move", {
                "picking_id": picking_id,
                "product_id": line["product_id"],
                "product_uom_qty": line["qty"],
            })
    
    return picking_id


def cmd_transfer_list(client: OdooClient, args):
    """查看调拨单"""
    domain = [["picking_type_code", "=", "internal"]]
    pickings = client.search_read("stock.picking", domain, limit=args.limit or 50)
    
    print(f"\n🔄 调拨单列表 (共 {len(pickings)} 条)\n")
    for p in pickings:
        print(f"ID: {p['id']} - {p.get('name', 'N/A')}")
    
    return pickings


def cmd_adjustment_create(client: OdooClient, args):
    """创建盘点单"""
    print(f"📋 正在创建盘点单...")
    # TODO: 实现盘点单创建
    return True


def cmd_adjustment_apply(client: OdooClient, args):
    """应用盘点"""
    print(f"✅ 正在应用盘点 {args.inventory_id}...")
    # TODO: 实现盘点应用
    return True


def cmd_stock_query(client: OdooClient, args):
    """查询库存"""
    domain = []
    if args.product_id:
        domain.append(["product_id", "=", args.product_id])
    if args.location_id:
        domain.append(["location_id", "=", args.location_id])
    
    quants = client.search_read("stock.quant", domain, fields=["product_id", "location_id", "quantity"])
    
    print(f"\n📦 库存查询结果 (共 {len(quants)} 条)\n")
    for q in quants:
        product = q.get("product_id", [None, "N/A"])
        product_name = product[1] if isinstance(product, list) else "N/A"
        print(f"产品：{product_name} - 数量：{q.get('quantity', 0)}")
    
    return quants


def cmd_stock_report(client: OdooClient, args):
    """库存报表"""
    print("📊 库存报表")
    # TODO: 实现报表
    return True


def parse_product_lines(lines_str: str):
    lines = []
    for line in lines_str.split(","):
        parts = line.split(":")
        if len(parts) >= 2:
            lines.append({"product_id": parts[0], "qty": float(parts[1])})
    return lines


def main():
    parser = argparse.ArgumentParser(description="Odoo 库存管理脚本")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--verbose", action="store_true")
    
    subparsers = parser.add_subparsers(dest="module")
    
    # Incoming
    inc = subparsers.add_parser("incoming", help="入库管理")
    inc_sub = inc.add_subparsers(dest="action")
    
    inc_create = inc_sub.add_parser("create", help="创建入库单")
    inc_create.add_argument("--partner_id", type=int, required=True)
    inc_create.add_argument("--warehouse_id", type=int)
    inc_create.add_argument("--lines", help="产品行")
    inc_create.add_argument("--scheduled_date", help="计划日期")
    inc_create.set_defaults(func=cmd_incoming_create)
    
    inc_list = inc_sub.add_parser("list", help="查看入库单")
    inc_list.add_argument("--state", help="状态")
    inc_list.add_argument("--limit", type=int)
    inc_list.set_defaults(func=cmd_incoming_list)
    
    inc_val = inc_sub.add_parser("validate", help="确认入库")
    inc_val.add_argument("picking_id", type=int)
    inc_val.set_defaults(func=cmd_incoming_validate)
    
    # Outgoing
    out = subparsers.add_parser("outgoing", help="出库管理")
    out_sub = out.add_subparsers(dest="action")
    
    out_create = out_sub.add_parser("create", help="创建出库单")
    out_create.add_argument("--partner_id", type=int, required=True)
    out_create.add_argument("--lines", help="产品行")
    out_create.set_defaults(func=cmd_outgoing_create)
    
    out_list = out_sub.add_parser("list", help="查看出库单")
    out_list.add_argument("--state", help="状态")
    out_list.add_argument("--limit", type=int)
    out_list.set_defaults(func=cmd_outgoing_list)
    
    out_val = out_sub.add_parser("validate", help="确认出库")
    out_val.add_argument("picking_id", type=int)
    out_val.set_defaults(func=cmd_outgoing_validate)
    
    # Transfer
    trans = subparsers.add_parser("transfer", help="库存调拨")
    trans_sub = trans.add_subparsers(dest="action")
    
    trans_create = trans_sub.add_parser("create", help="创建调拨单")
    trans_create.add_argument("--location_src_id", type=int, required=True)
    trans_create.add_argument("--location_dest_id", type=int, required=True)
    trans_create.add_argument("--lines", help="产品行")
    trans_create.set_defaults(func=cmd_transfer_create)
    
    trans_list = trans_sub.add_parser("list", help="查看调拨单")
    trans_list.add_argument("--limit", type=int)
    trans_list.set_defaults(func=cmd_transfer_list)
    
    # Adjustment
    adj = subparsers.add_parser("adjustment", help="库存盘点")
    adj_sub = adj.add_subparsers(dest="action")
    
    adj_create = adj_sub.add_parser("create", help="创建盘点单")
    adj_create.add_argument("--location_id", type=int, required=True)
    adj_create.add_argument("--products", help="产品列表")
    adj_create.set_defaults(func=cmd_adjustment_create)
    
    adj_apply = adj_sub.add_parser("apply", help="应用盘点")
    adj_apply.add_argument("inventory_id", type=int)
    adj_apply.set_defaults(func=cmd_adjustment_apply)
    
    # Stock
    stock = subparsers.add_parser("stock", help="库存查询")
    stock_sub = stock.add_subparsers(dest="action")
    
    stock_query = stock_sub.add_parser("query", help="查询库存")
    stock_query.add_argument("--product_id", type=int)
    stock_query.add_argument("--location_id", type=int)
    stock_query.set_defaults(func=cmd_stock_query)
    
    stock_report = stock_sub.add_parser("report", help="库存报表")
    stock_report.set_defaults(func=cmd_stock_report)
    
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
