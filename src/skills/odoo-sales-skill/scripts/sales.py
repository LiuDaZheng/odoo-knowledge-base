#!/usr/bin/env python3
"""
Odoo 销售管理脚本

提供报价、订单、价格策略和销售分析功能。

用法:
    python3 sales.py <module> <action> [options]
"""

import argparse
import sys
from typing import Any, Dict, List

# 导入 Odoo 客户端（与 CRM Skill 共享）
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'odoo-crm-skill', 'scripts'))
from odoo_client import create_client, OdooClient


# ========== 报价管理 ==========

def cmd_quotation_create(client: OdooClient, args):
    """创建报价单"""
    values = {
        "partner_id": args.partner_id,
        "validity_days": args.validity_days or 30,
    }
    
    if args.notes:
        values["note"] = args.notes
    
    # 创建报价单
    quotation_id = client.create("sale.order", values)
    print(f"✅ 报价单创建成功！ID: {quotation_id}")
    
    # 添加产品行
    if args.lines:
        lines = parse_order_lines(args.lines)
        for line in lines:
            line_values = {
                "order_id": quotation_id,
                "product_id": line["product_id"],
                "product_uom_qty": line["qty"],
                "price_unit": line["price"],
            }
            client.create("sale.order.line", line_values)
        print(f"   已添加 {len(lines)} 个产品行")
    
    return quotation_id


def cmd_quotation_list(client: OdooClient, args):
    """查看报价单列表"""
    domain = [["state", "in", ["draft", "sent"]]]
    
    if args.partner_id:
        domain.append(["partner_id", "=", args.partner_id])
    if args.state:
        domain.append(["state", "=", args.state])
    
    fields = [
        "id", "name", "partner_id", "date_order", "state",
        "amount_total", "validity_date", "user_id"
    ]
    
    quotations = client.search_read(
        "sale.order",
        domain,
        fields=fields,
        limit=args.limit or 50
    )
    
    print(f"\n📋 报价单列表 (共 {len(quotations)} 条)\n")
    print("-" * 100)
    
    for q in quotations:
        partner = q.get("partner_id", [None, "N/A"])
        partner_name = partner[1] if isinstance(partner, list) else "N/A"
        
        print(f"ID: {q['id']} - {q['name']}")
        print(f"  客户：{partner_name}")
        print(f"  日期：{q.get('date_order', 'N/A')}")
        print(f"  状态：{q.get('state', 'N/A')}")
        print(f"  总额：¥{q.get('amount_total', 0):,.2f}")
        print(f"  有效期至：{q.get('validity_date', 'N/A')}")
        print("-" * 100)
    
    return quotations


def cmd_quotation_send(client: OdooClient, args):
    """发送报价单"""
    print(f"📧 正在发送报价单 {args.quotation_id}...")
    # TODO: 实现邮件发送
    print("   此功能需要配置邮件服务器")
    return True


def cmd_quotation_confirm(client: OdooClient, args):
    """确认报价单"""
    print(f"✅ 正在确认报价单 {args.quotation_id}...")
    
    # 调用 Odoo 的 action_confirm 方法
    result = client.execute("sale.order", "action_confirm", [[args.quotation_id]])
    
    print(f"   报价单已确认，转为销售订单")
    return result


# ========== 订单管理 ==========

def cmd_order_create(client: OdooClient, args):
    """创建销售订单"""
    values = {
        "partner_id": args.partner_id,
    }
    
    if args.warehouse_id:
        values["warehouse_id"] = args.warehouse_id
    if args.commitment_date:
        values["commitment_date"] = args.commitment_date
    
    order_id = client.create("sale.order", values)
    print(f"✅ 销售订单创建成功！ID: {order_id}")
    
    # 添加产品行
    if args.lines:
        lines = parse_order_lines(args.lines)
        for line in lines:
            line_values = {
                "order_id": order_id,
                "product_id": line["product_id"],
                "product_uom_qty": line["qty"],
                "price_unit": line["price"],
            }
            client.create("sale.order.line", line_values)
        print(f"   已添加 {len(lines)} 个产品行")
    
    return order_id


def cmd_order_list(client: OdooClient, args):
    """查看订单列表"""
    domain = [["state", "in", ["sale", "done"]]]
    
    if args.partner_id:
        domain.append(["partner_id", "=", args.partner_id])
    if args.state:
        domain.append(["state", "=", args.state])
    
    fields = [
        "id", "name", "partner_id", "date_order", "state",
        "amount_total", "commitment_date"
    ]
    
    orders = client.search_read(
        "sale.order",
        domain,
        fields=fields,
        limit=args.limit or 50
    )
    
    print(f"\n📦 销售订单列表 (共 {len(orders)} 条)\n")
    print("-" * 100)
    
    for o in orders:
        partner = o.get("partner_id", [None, "N/A"])
        partner_name = partner[1] if isinstance(partner, list) else "N/A"
        
        print(f"ID: {o['id']} - {o['name']}")
        print(f"  客户：{partner_name}")
        print(f"  日期：{o.get('date_order', 'N/A')}")
        print(f"  状态：{o.get('state', 'N/A')}")
        print(f"  总额：¥{o.get('amount_total', 0):,.2f}")
        print(f"  承诺交货期：{o.get('commitment_date', 'N/A')}")
        print("-" * 100)
    
    return orders


def cmd_order_get(client: OdooClient, args):
    """查看订单详情"""
    order = client.read("sale.order", [args.order_id])
    
    if not order:
        print(f"❌ 订单 {args.order_id} 不存在")
        return None
    
    print_order_detail(order[0])
    return order[0]


def cmd_order_deliver(client: OdooClient, args):
    """订单发货"""
    print(f"🚚 正在处理订单 {args.order_id} 发货...")
    # TODO: 创建发货单
    return True


def cmd_order_invoice(client: OdooClient, args):
    """创建发票"""
    print(f"📄 正在为订单 {args.order_id} 创建发票...")
    # TODO: 创建发票
    return True


# ========== 价格策略 ==========

def cmd_pricelist_list(client: OdooClient, args):
    """查看价格表"""
    pricelists = client.search_read(
        "product.pricelist",
        [],
        fields=["id", "name", "currency_id", "discount_policy"]
    )
    
    print(f"\n💰 价格表列表 (共 {len(pricelists)} 条)\n")
    
    for pl in pricelists:
        currency = pl.get("currency_id", [None, "CNY"])
        currency_name = currency[1] if isinstance(currency, list) else "CNY"
        
        print(f"ID: {pl['id']} - {pl['name']}")
        print(f"  货币：{currency_name}")
        print(f"  折扣策略：{pl.get('discount_policy', 'N/A')}")
        print("-" * 50)
    
    return pricelists


def cmd_pricelist_create(client: OdooClient, args):
    """创建价格表"""
    values = {
        "name": args.name,
        "currency_id": args.currency_id or 1,
    }
    
    if args.discount_policy:
        values["discount_policy"] = args.discount_policy
    
    pricelist_id = client.create("product.pricelist", values)
    print(f"✅ 价格表创建成功！ID: {pricelist_id}")
    return pricelist_id


def cmd_pricelist_add_item(client: OdooClient, args):
    """添加价格表项目"""
    values = {
        "pricelist_id": args.pricelist_id,
        "product_id": args.product_id,
        "fixed_price": args.fixed_price,
    }
    
    if args.min_quantity:
        values["min_quantity"] = args.min_quantity
    
    item_id = client.create("product.pricelist.item", values)
    print(f"✅ 价格表项目创建成功！ID: {item_id}")
    return item_id


# ========== 销售分析 ==========

def cmd_report_by_product(client: OdooClient, args):
    """按产品分析"""
    print("📊 产品销售分析报表")
    # TODO: 实现分析逻辑
    print("   此功能需要查询销售分析视图")


def cmd_report_by_customer(client: OdooClient, args):
    """按客户分析"""
    print("📊 客户销售分析报表")
    # TODO: 实现分析逻辑


def cmd_report_by_salesperson(client: OdooClient, args):
    """按销售员分析"""
    print("📊 销售员业绩分析报表")
    # TODO: 实现分析逻辑


# ========== 辅助函数 ==========

def parse_order_lines(lines_str: str) -> List[Dict]:
    """解析订单行字符串"""
    lines = []
    for line in lines_str.split(","):
        parts = line.split(":")
        if len(parts) >= 3:
            lines.append({
                "product_id": parts[0],  # TODO: 根据产品名称查询 ID
                "qty": float(parts[1]),
                "price": float(parts[2]),
            })
    return lines


def print_order_detail(order: Dict):
    """打印订单详情"""
    print(f"\n📦 订单详情 (ID: {order['id']})\n")
    print("-" * 50)
    print(f"订单号：{order.get('name', 'N/A')}")
    print(f"客户：{order.get('partner_id', 'N/A')}")
    print(f"日期：{order.get('date_order', 'N/A')}")
    print(f"状态：{order.get('state', 'N/A')}")
    print(f"总额：¥{order.get('amount_total', 0):,.2f}")
    print("-" * 50)


# ========== 主程序 ==========

def main():
    parser = argparse.ArgumentParser(description="Odoo 销售管理脚本")
    parser.add_argument("--config", help="配置文件路径", default=None)
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    
    subparsers = parser.add_subparsers(dest="module", help="功能模块")
    
    # 报价管理
    quote_parser = subparsers.add_parser("quotation", help="报价管理")
    quote_subparsers = quote_parser.add_subparsers(dest="action")
    
    quote_create = quote_subparsers.add_parser("create", help="创建报价")
    quote_create.add_argument("--partner_id", type=int, required=True, help="客户 ID")
    quote_create.add_argument("--validity_days", type=int, help="有效期（天）")
    quote_create.add_argument("--lines", help="产品行")
    quote_create.add_argument("--notes", help="备注")
    quote_create.set_defaults(func=cmd_quotation_create)
    
    quote_list = quote_subparsers.add_parser("list", help="查看报价")
    quote_list.add_argument("--partner_id", type=int, help="客户 ID")
    quote_list.add_argument("--state", help="状态")
    quote_list.add_argument("--limit", type=int, help="返回数量")
    quote_list.set_defaults(func=cmd_quotation_list)
    
    quote_send = quote_subparsers.add_parser("send", help="发送报价")
    quote_send.add_argument("quotation_id", type=int, help="报价单 ID")
    quote_send.add_argument("--email", help="收件人邮箱")
    quote_send.add_argument("--subject", help="邮件主题")
    quote_send.set_defaults(func=cmd_quotation_send)
    
    quote_confirm = quote_subparsers.add_parser("confirm", help="确认报价")
    quote_confirm.add_argument("quotation_id", type=int, help="报价单 ID")
    quote_confirm.set_defaults(func=cmd_quotation_confirm)
    
    # 订单管理
    order_parser = subparsers.add_parser("order", help="订单管理")
    order_subparsers = order_parser.add_subparsers(dest="action")
    
    order_create = order_subparsers.add_parser("create", help="创建订单")
    order_create.add_argument("--partner_id", type=int, required=True, help="客户 ID")
    order_create.add_argument("--lines", help="产品行")
    order_create.add_argument("--warehouse_id", type=int, help="仓库 ID")
    order_create.add_argument("--commitment_date", help="承诺交货期")
    order_create.set_defaults(func=cmd_order_create)
    
    order_list = order_subparsers.add_parser("list", help="查看订单")
    order_list.add_argument("--partner_id", type=int, help="客户 ID")
    order_list.add_argument("--state", help="状态")
    order_list.add_argument("--limit", type=int, help="返回数量")
    order_list.set_defaults(func=cmd_order_list)
    
    order_get = order_subparsers.add_parser("get", help="订单详情")
    order_get.add_argument("order_id", type=int, help="订单 ID")
    order_get.set_defaults(func=cmd_order_get)
    
    order_deliver = order_subparsers.add_parser("deliver", help="订单发货")
    order_deliver.add_argument("order_id", type=int, help="订单 ID")
    order_deliver.set_defaults(func=cmd_order_deliver)
    
    order_invoice = order_subparsers.add_parser("invoice", help="创建发票")
    order_invoice.add_argument("order_id", type=int, help="订单 ID")
    order_invoice.set_defaults(func=cmd_order_invoice)
    
    # 价格策略
    pl_parser = subparsers.add_parser("pricelist", help="价格策略")
    pl_subparsers = pl_parser.add_subparsers(dest="action")
    
    pl_list = pl_subparsers.add_parser("list", help="查看价格表")
    pl_list.set_defaults(func=cmd_pricelist_list)
    
    pl_create = pl_subparsers.add_parser("create", help="创建价格表")
    pl_create.add_argument("--name", required=True, help="价格表名称")
    pl_create.add_argument("--currency_id", type=int, help="货币 ID")
    pl_create.add_argument("--discount_policy", help="折扣策略")
    pl_create.set_defaults(func=cmd_pricelist_create)
    
    pl_add_item = pl_subparsers.add_parser("add-item", help="添加价格项目")
    pl_add_item.add_argument("pricelist_id", type=int, help="价格表 ID")
    pl_add_item.add_argument("--product_id", type=int, required=True, help="产品 ID")
    pl_add_item.add_argument("--fixed_price", type=float, required=True, help="固定价格")
    pl_add_item.add_argument("--min_quantity", type=int, help="最小数量")
    pl_add_item.set_defaults(func=cmd_pricelist_add_item)
    
    # 销售分析
    report_parser = subparsers.add_parser("report", help="销售分析")
    report_subparsers = report_parser.add_subparsers(dest="action")
    
    report_product = report_subparsers.add_parser("by-product", help="按产品分析")
    report_product.add_argument("--date_from", help="开始日期")
    report_product.add_argument("--date_to", help="结束日期")
    report_product.set_defaults(func=cmd_report_by_product)
    
    report_customer = report_subparsers.add_parser("by-customer", help="按客户分析")
    report_customer.add_argument("--date_from", help="开始日期")
    report_customer.add_argument("--date_to", help="结束日期")
    report_customer.set_defaults(func=cmd_report_by_customer)
    
    report_salesperson = report_subparsers.add_parser("by-salesperson", help="按销售员分析")
    report_salesperson.add_argument("--date_from", help="开始日期")
    report_salesperson.add_argument("--date_to", help="结束日期")
    report_salesperson.set_defaults(func=cmd_report_by_salesperson)
    
    args = parser.parse_args()
    
    if not args.module:
        parser.print_help()
        sys.exit(1)
    
    if not hasattr(args, 'func'):
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
