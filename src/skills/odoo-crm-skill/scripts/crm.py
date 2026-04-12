#!/usr/bin/env python3
"""
Odoo CRM 管理脚本

提供线索、机会、客户、销售管道的完整管理功能。

用法:
    python3 crm.py <module> <action> [options]

模块:
    lead         线索管理
    opportunity  机会管理
    customer     客户管理
    pipeline     管道管理
    report       报表分析

示例:
    python3 crm.py lead create --name "测试线索" --contact_name "张三"
    python3 crm.py lead list --priority high
    python3 crm.py opportunity create --name "测试机会" --customer_id 123
    python3 crm.py customer list --industry "制造业"
    python3 crm.py pipeline view
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from odoo_client import create_client, OdooClient


# ========== 线索管理 ==========

def cmd_lead_create(client: OdooClient, args):
    """创建线索"""
    values = {
        "name": args.name,
    }
    
    if args.contact_name:
        values["contact_name"] = args.contact_name
    if args.email:
        values["email_from"] = args.email
    if args.phone:
        values["phone"] = args.phone
    if args.company:
        values["partner_name"] = args.company
    if args.revenue:
        values["revenue"] = args.revenue
    if args.priority:
        priority_map = {"low": "1", "medium": "2", "high": "3"}
        values["priority"] = priority_map.get(args.priority, "2")
    if args.description:
        values["description"] = args.description
    if args.tags:
        # TODO: 实现标签处理
        pass
    
    lead_id = client.create("crm.lead", values)
    print(f"✅ 线索创建成功！ID: {lead_id}")
    return lead_id


def cmd_lead_list(client: OdooClient, args):
    """查看线索列表"""
    domain = []
    
    if args.stage:
        # TODO: 根据阶段名称查询阶段 ID
        pass
    if args.priority:
        priority_map = {"low": "1", "medium": "2", "high": "3"}
        domain.append(["priority", "=", priority_map.get(args.priority, "2")])
    if args.user_id:
        domain.append(["user_id", "=", args.user_id])
    
    fields = [
        "id", "name", "contact_name", "email_from", "phone",
        "partner_name", "revenue", "priority", "stage_id", "create_date"
    ]
    
    leads = client.search_read(
        "crm.lead",
        domain,
        fields=fields,
        limit=args.limit,
        offset=args.offset,
        order="create_date desc"
    )
    
    print(f"\n📋 线索列表 (共 {len(leads)} 条)\n")
    print("-" * 100)
    
    for lead in leads:
        stage_name = lead.get("stage_id", [None, "Unknown"])[1] if isinstance(lead.get("stage_id"), list) else "Unknown"
        print(f"ID: {lead['id']}")
        print(f"  名称：{lead['name']}")
        print(f"  联系人：{lead.get('contact_name', 'N/A')}")
        print(f"  公司：{lead.get('partner_name', 'N/A')}")
        print(f"  邮箱：{lead.get('email_from', 'N/A')}")
        print(f"  电话：{lead.get('phone', 'N/A')}")
        print(f"  预计收入：{lead.get('revenue', 0):,.0f}")
        print(f"  优先级：{lead.get('priority', 'N/A')}")
        print(f"  阶段：{stage_name}")
        print(f"  创建日期：{lead.get('create_date', 'N/A')}")
        print("-" * 100)
    
    return leads


def cmd_lead_update(client: OdooClient, args):
    """更新线索"""
    values = {}
    
    if args.name:
        values["name"] = args.name
    if args.priority:
        priority_map = {"low": "1", "medium": "2", "high": "3"}
        values["priority"] = priority_map.get(args.priority, "2")
    if args.stage:
        # TODO: 根据阶段名称查询阶段 ID
        pass
    if args.description:
        values["description"] = args.description
    if args.email:
        values["email_from"] = args.email
    if args.phone:
        values["phone"] = args.phone
    
    if not values:
        print("❌ 错误：没有提供要更新的字段")
        return False
    
    success = client.write("crm.lead", [args.lead_id], values)
    
    if success:
        print(f"✅ 线索 {args.lead_id} 更新成功！")
    else:
        print(f"❌ 线索 {args.lead_id} 更新失败")
    
    return success


def cmd_lead_convert(client: OdooClient, args):
    """转化线索"""
    # TODO: 实现线索转化逻辑
    print(f"🔄 正在转化线索 {args.lead_id}...")
    print("   此功能需要调用 Odoo 的 convert_to_opportunity 方法")
    print("   将在后续版本实现")
    return True


def cmd_lead_delete(client: OdooClient, args):
    """删除线索"""
    if args.force:
        print(f"⚠️  警告：即将永久删除线索 {args.lead_id}")
        confirm = input("确认删除？(yes/no): ")
        if confirm.lower() != "yes":
            print("❌ 取消删除")
            return False
    
    success = client.unlink("crm.lead", [args.lead_id])
    
    if success:
        print(f"✅ 线索 {args.lead_id} 已删除")
    else:
        print(f"❌ 线索 {args.lead_id} 删除失败")
    
    return success


# ========== 机会管理 ==========

def cmd_opportunity_create(client: OdooClient, args):
    """创建机会"""
    values = {
        "name": args.name,
        "partner_id": args.customer_id,
    }
    
    if args.expected_revenue:
        values["expected_revenue"] = args.expected_revenue
    if args.probability:
        values["probability"] = args.probability
    if args.stage:
        # TODO: 根据阶段名称查询阶段 ID
        pass
    if args.salesperson_id:
        values["user_id"] = args.salesperson_id
    if args.deadline:
        values["date_deadline"] = args.deadline
    if args.description:
        values["description"] = args.description
    
    opportunity_id = client.create("crm.lead", values)
    print(f"✅ 机会创建成功！ID: {opportunity_id}")
    return opportunity_id


def cmd_opportunity_list(client: OdooClient, args):
    """查看机会列表"""
    domain = [["type", "=", "opportunity")]  # 只查询机会，不包括线索
    
    if args.stage:
        pass
    if args.min_probability:
        domain.append(["probability", ">=", args.min_probability])
    if args.min_revenue:
        domain.append(["expected_revenue", ">=", args.min_revenue])
    if args.user_id:
        domain.append(["user_id", "=", args.user_id])
    elif args.my:
        # TODO: 获取当前用户 ID
        pass
    
    fields = [
        "id", "name", "partner_id", "expected_revenue", "probability",
        "stage_id", "user_id", "date_deadline", "create_date"
    ]
    
    opportunities = client.search_read(
        "crm.lead",
        domain,
        fields=fields,
        limit=args.limit,
        offset=args.offset,
        order="create_date desc"
    )
    
    print(f"\n💼 机会列表 (共 {len(opportunities)} 条)\n")
    print("-" * 100)
    
    for opp in opportunities:
        partner = opp.get("partner_id", [None, "N/A"])
        partner_name = partner[1] if isinstance(partner, list) else "N/A"
        stage_name = opp.get("stage_id", [None, "Unknown"])
        stage_name = stage_name[1] if isinstance(stage_name, list) else "Unknown"
        
        print(f"ID: {opp['id']}")
        print(f"  名称：{opp['name']}")
        print(f"  客户：{partner_name}")
        print(f"  预计收入：{opp.get('expected_revenue', 0):,.0f}")
        print(f"  成功概率：{opp.get('probability', 0)}%")
        print(f"  阶段：{stage_name}")
        print(f"  截止日期：{opp.get('date_deadline', 'N/A')}")
        print("-" * 100)
    
    return opportunities


def cmd_opportunity_update(client: OdooClient, args):
    """更新机会"""
    values = {}
    
    if args.stage:
        pass
    if args.probability:
        values["probability"] = args.probability
    if args.expected_revenue:
        values["expected_revenue"] = args.expected_revenue
    if args.activity:
        # TODO: 创建活动记录
        pass
    
    if not values:
        print("❌ 错误：没有提供要更新的字段")
        return False
    
    success = client.write("crm.lead", [args.opportunity_id], values)
    
    if success:
        print(f"✅ 机会 {args.opportunity_id} 更新成功！")
    else:
        print(f"❌ 机会 {args.opportunity_id} 更新失败")
    
    return success


def cmd_opportunity_pipeline(client: OdooClient, args):
    """查看销售管道"""
    # 获取所有阶段
    stages = client.search_read("crm.stage", [], fields=["id", "name", "sequence"])
    
    print("\n📊 销售管道\n")
    
    for stage in sorted(stages, key=lambda x: x.get("sequence", 0)):
        stage_id = stage["id"]
        stage_name = stage["name"]
        
        # 查询该阶段的机会
        domain = [["type", "=", "opportunity"], ["stage_id", "=", stage_id]]
        opportunities = client.search_read(
            "crm.lead",
            domain,
            fields=["id", "name", "expected_revenue", "probability"]
        )
        
        total_revenue = sum(opp.get("expected_revenue", 0) for opp in opportunities)
        
        print(f"{stage_name}: {len(opportunities)} 个机会，总计 ¥{total_revenue:,.0f}")
        for opp in opportunities[:5]:  # 只显示前 5 个
            print(f"  - {opp['name']} (¥{opp.get('expected_revenue', 0):,.0f})")
        if len(opportunities) > 5:
            print(f"  ... 还有 {len(opportunities) - 5} 个")
        print()


# ========== 客户管理 ==========

def cmd_customer_create(client: OdooClient, args):
    """创建客户"""
    values = {
        "name": args.name,
        "company_type": "company" if args.type == "company" else "person",
    }
    
    if args.email:
        values["email"] = args.email
    if args.phone:
        values["phone"] = args.phone
    if args.website:
        values["website"] = args.website
    if args.street:
        values["street"] = args.street
    if args.city:
        values["city"] = args.city
    if args.zip:
        values["zip"] = args.zip
    if args.country:
        # TODO: 根据国家名称查询国家 ID
        pass
    if args.industry:
        values["industry"] = args.industry
    
    customer_id = client.create("res.partner", values)
    print(f"✅ 客户创建成功！ID: {customer_id}")
    return customer_id


def cmd_customer_list(client: OdooClient, args):
    """查看客户列表"""
    domain = [["customer", "=", True]]
    
    if args.industry:
        domain.append(["industry", "=", args.industry])
    
    fields = [
        "id", "name", "email", "phone", "website",
        "city", "country_id", "industry", "create_date"
    ]
    
    customers = client.search_read(
        "res.partner",
        domain,
        fields=fields,
        limit=args.limit,
        order="create_date desc"
    )
    
    print(f"\n👥 客户列表 (共 {len(customers)} 条)\n")
    print("-" * 100)
    
    for customer in customers:
        print(f"ID: {customer['id']}")
        print(f"  名称：{customer['name']}")
        print(f"  邮箱：{customer.get('email', 'N/A')}")
        print(f"  电话：{customer.get('phone', 'N/A')}")
        print(f"  网站：{customer.get('website', 'N/A')}")
        print(f"  城市：{customer.get('city', 'N/A')}")
        print(f"  行业：{customer.get('industry', 'N/A')}")
        print("-" * 100)
    
    return customers


def cmd_customer_search(client: OdooClient, args):
    """搜索客户"""
    domain = [
        ["customer", "=", True],
        ["|", ["name", "ilike", args.query], ["email", "ilike", args.query]]
    ]
    
    fields = ["id", "name", "email", "phone", "website"]
    
    customers = client.search_read("res.partner", domain, fields=fields, limit=args.limit)
    
    print(f"\n🔍 搜索结果：'{args.query}' (共 {len(customers)} 条)\n")
    
    for customer in customers:
        print(f"ID: {customer['id']} - {customer['name']} ({customer.get('email', 'N/A')})")
    
    return customers


def cmd_customer_get(client: OdooClient, args):
    """查看客户详情"""
    customer = client.read("res.partner", [args.customer_id])
    
    if not customer:
        print(f"❌ 客户 {args.customer_id} 不存在")
        return None
    
    c = customer[0]
    
    print(f"\n👤 客户详情 (ID: {c['id']})\n")
    print("-" * 50)
    print(f"名称：{c['name']}")
    print(f"类型：{'公司' if c.get('company_type') == 'company' else '个人'}")
    print(f"邮箱：{c.get('email', 'N/A')}")
    print(f"电话：{c.get('phone', 'N/A')}")
    print(f"网站：{c.get('website', 'N/A')}")
    print(f"地址：{c.get('street', 'N/A')} {c.get('city', 'N/A')} {c.get('zip', 'N/A')}")
    print(f"行业：{c.get('industry', 'N/A')}")
    print(f"创建日期：{c.get('create_date', 'N/A')}")
    print("-" * 50)
    
    return c


# ========== 主程序 ==========

def main():
    parser = argparse.ArgumentParser(
        description="Odoo CRM 管理脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument("--config", help="配置文件路径", default=None)
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--dry-run", action="store_true", help="模拟执行")
    
    subparsers = parser.add_subparsers(dest="module", help="功能模块")
    
    # 线索管理
    lead_parser = subparsers.add_parser("lead", help="线索管理")
    lead_subparsers = lead_parser.add_subparsers(dest="action")
    
    # lead create
    lead_create = lead_subparsers.add_parser("create", help="创建线索")
    lead_create.add_argument("--name", required=True, help="线索名称")
    lead_create.add_argument("--contact_name", help="联系人姓名")
    lead_create.add_argument("--email", help="联系邮箱")
    lead_create.add_argument("--phone", help="联系电话")
    lead_create.add_argument("--company", help="公司名称")
    lead_create.add_argument("--revenue", type=float, help="预计收入")
    lead_create.add_argument("--priority", choices=["low", "medium", "high"], help="优先级")
    lead_create.add_argument("--description", help="描述")
    lead_create.add_argument("--tags", help="标签（逗号分隔）")
    lead_create.set_defaults(func=cmd_lead_create)
    
    # lead list
    lead_list = lead_subparsers.add_parser("list", help="查看线索列表")
    lead_list.add_argument("--stage", help="阶段")
    lead_list.add_argument("--priority", choices=["low", "medium", "high"], help="优先级")
    lead_list.add_argument("--user_id", type=int, help="负责人 ID")
    lead_list.add_argument("--limit", type=int, default=50, help="返回数量")
    lead_list.add_argument("--offset", type=int, default=0, help="偏移量")
    lead_list.set_defaults(func=cmd_lead_list)
    
    # lead update
    lead_update = lead_subparsers.add_parser("update", help="更新线索")
    lead_update.add_argument("lead_id", type=int, help="线索 ID")
    lead_update.add_argument("--name", help="线索名称")
    lead_update.add_argument("--priority", choices=["low", "medium", "high"], help="优先级")
    lead_update.add_argument("--stage", help="阶段")
    lead_update.add_argument("--description", help="描述")
    lead_update.add_argument("--email", help="邮箱")
    lead_update.add_argument("--phone", help="电话")
    lead_update.set_defaults(func=cmd_lead_update)
    
    # lead convert
    lead_convert = lead_subparsers.add_parser("convert", help="转化线索")
    lead_convert.add_argument("lead_id", type=int, help="线索 ID")
    lead_convert.add_argument("--opportunity_name", help="机会名称")
    lead_convert.add_argument("--expected_revenue", type=float, help="预计收入")
    lead_convert.add_argument("--probability", type=int, help="成功概率")
    lead_convert.add_argument("--create_customer", action="store_true", help="创建客户")
    lead_convert.add_argument("--create_opportunity", action="store_true", help="创建机会")
    lead_convert.set_defaults(func=cmd_lead_convert)
    
    # lead delete
    lead_delete = lead_subparsers.add_parser("delete", help="删除线索")
    lead_delete.add_argument("lead_id", type=int, help="线索 ID")
    lead_delete.add_argument("--force", action="store_true", help="强制删除")
    lead_delete.set_defaults(func=cmd_lead_delete)
    
    # 机会管理
    opp_parser = subparsers.add_parser("opportunity", help="机会管理")
    opp_subparsers = opp_parser.add_subparsers(dest="action")
    
    # opportunity create
    opp_create = opp_subparsers.add_parser("create", help="创建机会")
    opp_create.add_argument("--name", required=True, help="机会名称")
    opp_create.add_argument("--customer_id", type=int, required=True, help="客户 ID")
    opp_create.add_argument("--expected_revenue", type=float, help="预计收入")
    opp_create.add_argument("--probability", type=int, help="成功概率")
    opp_create.add_argument("--stage", help="阶段")
    opp_create.add_argument("--salesperson_id", type=int, help="销售负责人 ID")
    opp_create.add_argument("--deadline", help="预计成交日期 (YYYY-MM-DD)")
    opp_create.add_argument("--description", help="描述")
    opp_create.add_argument("--tags", help="标签")
    opp_create.set_defaults(func=cmd_opportunity_create)
    
    # opportunity list
    opp_list = opp_subparsers.add_parser("list", help="查看机会列表")
    opp_list.add_argument("--stage", help="阶段")
    opp_list.add_argument("--min_probability", type=int, help="最小概率")
    opp_list.add_argument("--min_revenue", type=float, help="最小预计收入")
    opp_list.add_argument("--user_id", type=int, help="负责人 ID")
    opp_list.add_argument("--my", action="store_true", help="只看我的")
    opp_list.add_argument("--limit", type=int, default=50, help="返回数量")
    opp_list.add_argument("--offset", type=int, default=0, help="偏移量")
    opp_list.set_defaults(func=cmd_opportunity_list)
    
    # opportunity update
    opp_update = opp_subparsers.add_parser("update", help="更新机会")
    opp_update.add_argument("opportunity_id", type=int, help="机会 ID")
    opp_update.add_argument("--stage", help="阶段")
    opp_update.add_argument("--probability", type=int, help="成功概率")
    opp_update.add_argument("--expected_revenue", type=float, help="预计收入")
    opp_update.add_argument("--activity", help="活动记录")
    opp_update.add_argument("--activity_note", help="活动备注")
    opp_update.set_defaults(func=cmd_opportunity_update)
    
    # opportunity pipeline
    opp_pipeline = opp_subparsers.add_parser("pipeline", help="查看销售管道")
    opp_pipeline.set_defaults(func=cmd_opportunity_pipeline)
    
    # 客户管理
    cust_parser = subparsers.add_parser("customer", help="客户管理")
    cust_subparsers = cust_parser.add_subparsers(dest="action")
    
    # customer create
    cust_create = cust_subparsers.add_parser("create", help="创建客户")
    cust_create.add_argument("--name", required=True, help="客户名称")
    cust_create.add_argument("--type", choices=["company", "individual"], default="company", help="类型")
    cust_create.add_argument("--email", help="邮箱")
    cust_create.add_argument("--phone", help="电话")
    cust_create.add_argument("--website", help="网站")
    cust_create.add_argument("--street", help="街道地址")
    cust_create.add_argument("--city", help="城市")
    cust_create.add_argument("--zip", help="邮编")
    cust_create.add_argument("--country", help="国家")
    cust_create.add_argument("--industry", help="行业")
    cust_create.add_argument("--tags", help="标签")
    cust_create.set_defaults(func=cmd_customer_create)
    
    # customer list
    cust_list = cust_subparsers.add_parser("list", help="查看客户列表")
    cust_list.add_argument("--industry", help="行业")
    cust_list.add_argument("--tags", help="标签")
    cust_list.add_argument("--limit", type=int, default=50, help="返回数量")
    cust_list.set_defaults(func=cmd_customer_list)
    
    # customer search
    cust_search = cust_subparsers.add_parser("search", help="搜索客户")
    cust_search.add_argument("--query", required=True, help="搜索关键词")
    cust_search.add_argument("--limit", type=int, default=20, help="返回数量")
    cust_search.set_defaults(func=cmd_customer_search)
    
    # customer get
    cust_get = cust_subparsers.add_parser("get", help="查看客户详情")
    cust_get.add_argument("customer_id", type=int, help="客户 ID")
    cust_get.set_defaults(func=cmd_customer_get)
    
    # 管道管理
    pipe_parser = subparsers.add_parser("pipeline", help="管道管理")
    pipe_subparsers = pipe_parser.add_subparsers(dest="action")
    
    pipe_view = pipe_subparsers.add_parser("view", help="查看管道")
    pipe_view.set_defaults(func=cmd_opportunity_pipeline)
    
    # 解析参数
    args = parser.parse_args()
    
    if not args.module:
        parser.print_help()
        sys.exit(1)
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)
    
    # 创建客户端
    try:
        client = create_client(args.config)
        
        if args.verbose:
            print(f"✅ 已连接到 Odoo: {client.url}")
            print(f"   数据库：{client.database}")
            print(f"   用户：{client.username}")
        
        # 执行命令
        result = args.func(client, args)
        
        if args.json and result is not None:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
