# odoo-sales-skill 开发计划

**项目**: Odoo Knowledge Base Skill  
**Skill 名称**: odoo-sales-skill  
**版本**: 1.0.0  
**创建日期**: 2026-04-12  
**状态**: 规划中

---

## 1. Skill 概述

### 1.1 目标

提供 Odoo Sales 模块的完整操作能力，使 OpenClaw 能够：
- 自动创建和管理报价单
- 处理销售订单全流程
- 管理价格表和折扣策略
- 生成销售分析报告

### 1.2 触发器

**主要触发词**:
- "Odoo Sales"
- "创建报价"
- "销售订单"
- "价格表"
- "销售分析"
- "报价单"

### 1.3 适用场景

1. **CRM 机会转报价**: 从 CRM 机会自动生成报价单
2. **批量报价**: 为多个客户批量创建报价
3. **订单跟踪**: 实时监控订单状态和收款
4. **价格管理**: 动态应用价格表和折扣

---

## 2. 功能规格

### 2.1 P0 功能（MVP）

| ID | 功能 | 描述 | 优先级 | 工时估算 |
|----|------|------|--------|---------|
| F001 | 创建报价单 | 通过 API 创建销售报价单 | P0 | 4h |
| F002 | 查询报价单 | 搜索和读取报价单信息 | P0 | 3h |
| F003 | 更新报价单 | 更新报价单字段（产品、价格等） | P0 | 3h |
| F004 | 发送报价单 | 通过邮件发送报价单给客户 | P0 | 3h |
| F005 | 报价转订单 | 确认报价单，转换为销售订单 | P0 | 3h |
| F006 | 创建销售订单 | 直接创建销售订单 | P0 | 3h |
| F007 | 确认订单 | 确认销售订单（锁定价格和条款） | P0 | 2h |
| F008 | 配置管理 | Odoo 连接配置（URL, API Key, DB） | P0 | 2h |

**P0 总计**: 23h

### 2.2 P1 功能（增强）

| ID | 功能 | 描述 | 优先级 | 工时估算 |
|----|------|------|--------|---------|
| F101 | 报价单模板 | 应用预定义的报价单模板 | P1 | 4h |
| F102 | 价格表管理 | 查询和应用价格表 | P1 | 4h |
| F103 | 折扣计算 | 自动计算和应用折扣 | P1 | 3h |
| F104 | 产品查询 | 搜索产品信息和库存 | P1 | 3h |
| F105 | 订单状态跟踪 | 查询订单状态（确认/发货/开票） | P1 | 3h |
| F106 | 订单修改 | 修改已确认订单（需权限） | P1 | 3h |
| F107 | 客户价格表 | 设置和查询客户专属价格表 | P1 | 3h |

**P1 总计**: 23h

### 2.3 P2 功能（高级）

| ID | 功能 | 描述 | 优先级 | 工时估算 |
|----|------|------|--------|---------|
| F201 | 销售分析报告 | 生成销售绩效报告 | P2 | 6h |
| F202 | 收入分析 | 按产品/客户/时间段分析收入 | P2 | 5h |
| F203 | 产品性能分析 | 分析产品销售排名和趋势 | P2 | 5h |
| F204 | 在线报价单 | 生成在线报价单链接 | P2 | 6h |
| F205 | 电子签名 | 集成电子签名确认 | P2 | 8h |
| F206 | 在线支付 | 集成在线支付（预付款/全款） | P2 | 8h |
| F207 | 订阅管理 | 处理周期性销售订单 | P2 | 6h |

**P2 总计**: 44h

---

## 3. 技术设计

### 3.1 架构

```
┌─────────────────────────────────────────────────┐
│              OpenClaw Agent                     │
└─────────────────┬───────────────────────────────┘
                  │ 自然语言请求
┌─────────────────▼───────────────────────────────┐
│           odoo-sales-skill                      │
│  ┌─────────────────────────────────────────┐   │
│  │  Command Parser                         │   │
│  │  - 意图识别                             │   │
│  │  - 参数提取                             │   │
│  └─────────────────┬───────────────────────┘   │
│                    │                             │
│  ┌─────────────────▼───────────────────────┐   │
│  │  Business Logic Layer                   │   │
│  │  - create_quotation()                   │   │
│  │  - confirm_order()                      │   │
│  │  - apply_pricelist()                    │   │
│  │  - ...                                  │   │
│  └─────────────────┬───────────────────────┘   │
│                    │                             │
│  ┌─────────────────▼───────────────────────┐   │
│  │  Odoo API Client                        │   │
│  │  - JSON-2 API 封装                      │   │
│  │  - 认证管理                             │   │
│  │  - 错误处理                             │   │
│  │  - 重试机制                             │   │
│  └─────────────────┬───────────────────────┘   │
└────────────────────┼─────────────────────────────┘
                     │ HTTPS / JSON
┌────────────────────▼─────────────────────────────┐
│              Odoo Server                         │
│  - Sales Module (sale.order)                    │
│  - Product Module (product.product)             │
│  - Pricelist Module (product.pricelist)         │
│  - Partner Module (res.partner)                 │
└──────────────────────────────────────────────────┘
```

### 3.2 目录结构

```
odoo-sales-skill/
├── SKILL.md                    # Skill 定义（YAML + 指令）
├── README.md                   # 使用说明
├── requirements.txt            # Python 依赖
├── config.example.yaml         # 配置示例
├── src/
│   ├── __init__.py
│   ├── client.py               # Odoo API 客户端（与 CRM skill 共享）
│   ├── models.py               # 数据模型定义
│   ├── commands/               # 命令实现
│   │   ├── __init__.py
│   │   ├── quotation.py        # 报价单管理命令
│   │   ├── order.py            # 销售订单命令
│   │   ├── pricelist.py        # 价格表管理命令
│   │   └── product.py          # 产品查询命令
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── calculators.py      # 价格/折扣计算器
│   │   └── validators.py       # 数据验证
│   └── tests/                  # 单元测试
│       ├── __init__.py
│       ├── test_quotation.py
│       └── test_order.py
└── docs/
    ├── api_reference.md        # API 参考
    └── examples.md             # 使用示例
```

### 3.3 核心 API 设计

#### 3.3.1 报价单管理命令

```python
class QuotationCommands:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def create_quotation(
        self,
        partner_id: int,
        order_lines: list,
        pricelist_id: int = None,
        validity_days: int = 7,
        team_id: int = None,
        user_id: int = None,
        note: str = None
    ) -> dict:
        """
        创建销售报价单
        
        Args:
            partner_id: 客户 ID
            order_lines: 订单行列表 [
                {"product_id": 1, "quantity": 10, "price_unit": 100},
                ...
            ]
            pricelist_id: 价格表 ID
            validity_days: 报价有效期（天）
            team_id: 销售团队 ID
            user_id: 销售人员 ID
            note: 备注
        
        Returns:
            {"success": True, "quotation_id": 789, "amount_total": 1000}
        """
        from datetime import datetime, timedelta
        
        # 构建订单行
        order_line_data = []
        for line in order_lines:
            line_data = {
                "product_id": line["product_id"],
                "product_uom_qty": line["quantity"],
                "product_uom": line.get("uom_id", 1),
            }
            if "price_unit" in line:
                line_data["price_unit"] = line["price_unit"]
            if "discount" in line:
                line_data["discount"] = line["discount"]
            order_line_data.append((0, 0, line_data))
        
        # 计算有效期
        validity_date = (datetime.now() + timedelta(days=validity_days)).strftime("%Y-%m-%d")
        
        # 创建报价单
        quotation_data = {
            "partner_id": partner_id,
            "order_line": order_line_data,
            "state": "draft",
        }
        
        if pricelist_id:
            quotation_data["pricelist_id"] = pricelist_id
        if validity_date:
            quotation_data["validity_date"] = validity_date
        if team_id:
            quotation_data["team_id"] = team_id
        if user_id:
            quotation_data["user_id"] = user_id
        if note:
            quotation_data["note"] = note
        
        quotation_id = self.client.create("sale.order", quotation_data)
        
        # 读取总金额
        quotation = self.client.read(
            "sale.order",
            [quotation_id],
            ["amount_total", "amount_untaxed", "amount_tax", "currency_id"]
        )[0]
        
        return {
            "success": True,
            "quotation_id": quotation_id,
            "amount_total": quotation.get("amount_total", 0),
            "amount_untaxed": quotation.get("amount_untaxed", 0),
            "amount_tax": quotation.get("amount_tax", 0),
            "currency_id": quotation.get("currency_id", [1, "USD"])[1] if quotation.get("currency_id") else "USD"
        }
    
    def get_quotation(self, quotation_id: int) -> dict:
        """获取报价单详情"""
        quotations = self.client.read(
            "sale.order",
            [quotation_id],
            fields=[
                "name", "partner_id", "date_order", "validity_date",
                "state", "amount_total", "amount_untaxed", "amount_tax",
                "pricelist_id", "user_id", "team_id", "note",
                "order_line"
            ]
        )
        if not quotations:
            return {"success": False, "error": "报价单不存在"}
        
        quotation = quotations[0]
        
        # 读取订单行详情
        if quotation.get("order_line"):
            order_lines = self.client.read(
                "sale.order.line",
                [line[2] for line in quotation["order_line"] if isinstance(line, tuple) and line[0] == 0],
                fields=["product_id", "product_uom_qty", "price_unit", "discount", "price_subtotal"]
            )
            quotation["order_lines_detail"] = order_lines
        
        return {"success": True, "quotation": quotation}
    
    def send_quotation(self, quotation_id: int, email_to: str = None) -> dict:
        """发送报价单给客户"""
        try:
            # 使用 Odoo 内置的发送功能
            result = self.client.execute(
                "sale.order",
                "action_quotation_send",
                ids=[quotation_id],
                email_to=email_to
            )
            return {"success": True, "sent": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def confirm_quotation(self, quotation_id: int) -> dict:
        """确认报价单（转为销售订单）"""
        try:
            self.client.execute("sale.order", "action_confirm", ids=[quotation_id])
            
            # 读取确认后的订单信息
            order = self.client.read(
                "sale.order",
                [quotation_id],
                ["name", "state", "date_order", "amount_total"]
            )[0]
            
            return {
                "success": True,
                "order_name": order.get("name"),
                "state": order.get("state"),
                "amount_total": order.get("amount_total")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
```

#### 3.3.2 价格表管理命令

```python
class PricelistCommands:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def get_pricelists(self, active_only: bool = True) -> dict:
        """获取所有价格表"""
        domain = []
        if active_only:
            domain.append(("active", "=", True))
        
        pricelists = self.client.search_read(
            "product.pricelist",
            domain=domain,
            fields=["name", "currency_id", "company_id", "country_group_ids"]
        )
        
        return {
            "success": True,
            "pricelists": pricelists,
            "count": len(pricelists)
        }
    
    def apply_pricelist(self, quotation_id: int, pricelist_id: int) -> dict:
        """应用价格表到报价单"""
        try:
            # 更新价格表
            self.client.write("sale.order", [quotation_id], {
                "pricelist_id": pricelist_id
            })
            
            # 重新读取报价单（价格会自动重算）
            quotation = self.client.read(
                "sale.order",
                [quotation_id],
                ["amount_total", "amount_untaxed", "amount_tax"]
            )[0]
            
            return {
                "success": True,
                "amount_total": quotation.get("amount_total"),
                "amount_untaxed": quotation.get("amount_untaxed"),
                "amount_tax": quotation.get("amount_tax")
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_pricelist_rules(self, pricelist_id: int) -> dict:
        """获取价格表规则"""
        rules = self.client.search_read(
            "product.pricelist.item",
            domain=[("pricelist_id", "=", pricelist_id)],
            fields=[
                "name", "applied_on", "product_id", "product_tmpl_id",
                "product_category_id", "compute_price", "price",
                "percent_price", "base", "min_quantity", "date_start", "date_end"
            ]
        )
        
        return {
            "success": True,
            "rules": rules,
            "count": len(rules)
        }
```

#### 3.3.3 产品查询命令

```python
class ProductCommands:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def search_products(
        self,
        search_term: str = None,
        category_id: int = None,
        limit: int = 50
    ) -> dict:
        """搜索产品"""
        domain = [("sale_ok", "=", True), ("active", "=", True)]
        
        if search_term:
            domain.append("|")
            domain.append(("name", "ilike", search_term))
            domain.append(("default_code", "ilike", search_term))
        
        if category_id:
            domain.append(("categ_id", "=", category_id))
        
        products = self.client.search_read(
            "product.product",
            domain=domain,
            fields=[
                "name", "default_code", "list_price", "categ_id",
                "uom_id", "description_sale", "product_variant_count"
            ],
            limit=limit
        )
        
        return {
            "success": True,
            "products": products,
            "count": len(products)
        }
    
    def get_product(self, product_id: int) -> dict:
        """获取产品详情"""
        products = self.client.read(
            "product.product",
            [product_id],
            fields=[
                "name", "default_code", "list_price", "categ_id",
                "uom_id", "description_sale", "description_purchase",
                "type", "sale_ok", "purchase_ok", "active"
            ]
        )
        
        if not products:
            return {"success": False, "error": "产品不存在"}
        
        return {"success": True, "product": products[0]}
    
    def get_product_price(
        self,
        product_id: int,
        pricelist_id: int = None,
        quantity: int = 1
    ) -> dict:
        """获取产品价格（考虑价格表）"""
        # 读取产品基础价格
        product = self.client.read(
            "product.product",
            [product_id],
            ["name", "list_price", "uom_id"]
        )[0]
        
        base_price = product.get("list_price", 0)
        
        # 如果指定价格表，计算实际价格
        final_price = base_price
        discount = 0
        
        if pricelist_id:
            # 这里需要调用 Odoo 的价格计算逻辑
            # 简化处理：读取价格表规则
            rules = self.client.search_read(
                "product.pricelist.item",
                domain=[
                    ("pricelist_id", "=", pricelist_id),
                    "|",
                    ("product_id", "=", product_id),
                    ("applied_on", "=", "0_global")
                ],
                fields=["compute_price", "percent_price", "fixed_price", "min_quantity"]
            )
            
            for rule in rules:
                if rule.get("min_quantity", 1) <= quantity:
                    if rule.get("compute_price") == "percentage":
                        discount = rule.get("percent_price", 0)
                        final_price = base_price * (1 - discount / 100)
                    elif rule.get("compute_price") == "fixed":
                        final_price = rule.get("fixed_price", base_price)
                    break
        
        return {
            "success": True,
            "product_id": product_id,
            "product_name": product.get("name"),
            "base_price": base_price,
            "final_price": final_price,
            "discount": discount,
            "quantity": quantity,
            "total": final_price * quantity,
            "currency": "USD"  # 应从价格表或系统配置读取
        }
```

### 3.4 配置管理

```yaml
# config.example.yaml
odoo:
  url: "https://your-company.odoo.com"
  database: "your-database"
  api_key: "${ODOO_API_KEY}"  # 从环境变量读取
  timeout: 30
  retry:
    max_attempts: 3
    delay: 1  # 秒

sales:
  default_pricelist_id: 1
  default_validity_days: 7
  quotation_template_id: null
  auto_confirm: false  # 是否自动确认报价单
```

---

## 4. 开发计划

### 4.1 阶段 1: MVP 开发（2 周）

**Week 1**:
- [ ] Day 1-2: 项目初始化和基础架构
  - 创建目录结构
  - 复用 OdooClient（与 CRM skill 共享）
  - 配置管理
- [ ] Day 3-4: 报价单管理功能
  - create_quotation()
  - get_quotation()
  - update_quotation()
  - send_quotation()
- [ ] Day 5: 单元测试和文档
  - 编写测试用例
  - 编写 API 文档

**Week 2**:
- [ ] Day 1-2: 销售订单功能
  - confirm_quotation()
  - create_sale_order()
  - get_order_status()
- [ ] Day 3: 产品查询
  - search_products()
  - get_product_price()
- [ ] Day 4-5: 集成测试和优化
  - 端到端测试
  - 性能优化
  - 错误处理完善

### 4.2 阶段 2: 增强功能（2 周）

**Week 3**:
- [ ] Day 1-2: 价格表管理
  - get_pricelists()
  - apply_pricelist()
  - get_pricelist_rules()
- [ ] Day 3-4: 折扣计算
  - calculate_discount()
  - apply_discount()
- [ ] Day 5: 客户价格表
  - get_customer_pricelist()
  - set_customer_pricelist()

**Week 4**:
- [ ] Day 1-2: 报价单模板
  - apply_template()
  - create_template()
- [ ] Day 3-4: 订单修改
  - update_order_lines()
  - cancel_order()
- [ ] Day 5: 用户验收测试

### 4.3 阶段 3: 高级功能（3 周）

**Week 5**:
- [ ] Day 1-3: 销售分析报告
  - sales_analysis()
  - revenue_by_period()
- [ ] Day 4-5: 产品性能分析
  - product_performance()
  - top_selling_products()

**Week 6**:
- [ ] Day 1-3: 在线报价单
  - generate_online_link()
  - track_views()
- [ ] Day 4-5: 电子签名集成
  - request_signature()
  - verify_signature()

**Week 7**:
- [ ] Day 1-3: 在线支付集成
  - request_payment()
  - track_payment_status()
- [ ] Day 4-5: 最终测试和发布准备
  - 性能测试
  - 安全审计
  - 文档完善

---

## 5. 测试策略

### 5.1 单元测试

```python
# src/tests/test_quotation.py
import unittest
from unittest.mock import Mock, patch
from src.commands.quotation import QuotationCommands

class TestQuotationCommands(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.quotation_commands = QuotationCommands(self.mock_client)
    
    def test_create_quotation_success(self):
        """测试成功创建报价单"""
        self.mock_client.create.return_value = 789
        self.mock_client.read.return_value = [{
            "amount_total": 1000,
            "amount_untaxed": 900,
            "amount_tax": 100,
            "currency_id": [1, "USD"]
        }]
        
        result = self.quotation_commands.create_quotation(
            partner_id=1,
            order_lines=[{"product_id": 1, "quantity": 10, "price_unit": 100}]
        )
        
        self.assertTrue(result["success"])
        self.assertEqual(result["quotation_id"], 789)
        self.assertEqual(result["amount_total"], 1000)
    
    def test_confirm_quotation(self):
        """测试确认报价单"""
        self.mock_client.execute.return_value = True
        self.mock_client.read.return_value = [{
            "name": "S00123",
            "state": "sale",
            "amount_total": 1000
        }]
        
        result = self.quotation_commands.confirm_quotation(789)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["order_name"], "S00123")
        self.assertEqual(result["state"], "sale")
```

### 5.2 集成测试

```python
# tests/integration/test_sales_flow.py
def test_quotation_to_order_flow():
    """测试报价单到订单的完整流程"""
    # 1. 创建报价单
    quotation_result = skill.create_quotation(
        partner_id=1,
        order_lines=[
            {"product_id": 1, "quantity": 10, "price_unit": 100},
            {"product_id": 2, "quantity": 5, "price_unit": 200}
        ],
        validity_days=7
    )
    assert quotation_result["success"]
    quotation_id = quotation_result["quotation_id"]
    
    # 2. 查询报价单
    quotation = skill.get_quotation(quotation_id)
    assert quotation["success"]
    assert quotation["quotation"]["state"] == "draft"
    
    # 3. 应用价格表
    pricelist_result = skill.apply_pricelist(quotation_id, pricelist_id=2)
    assert pricelist_result["success"]
    
    # 4. 发送报价单
    send_result = skill.send_quotation(quotation_id)
    assert send_result["success"]
    
    # 5. 确认报价单
    order_result = skill.confirm_quotation(quotation_id)
    assert order_result["success"]
    assert order_result["state"] == "sale"
    
    # 6. 验证订单
    order = skill.get_quotation(quotation_id)
    assert order["quotation"]["state"] == "sale"
    assert order["quotation"]["name"].startswith("S")
```

### 5.3 性能测试

```python
# tests/performance/test_bulk_quotation.py
def test_bulk_quotation_creation():
    """测试批量创建报价单性能"""
    import time
    
    quotations_data = [
        {
            "partner_id": i % 10 + 1,
            "order_lines": [{"product_id": 1, "quantity": 10, "price_unit": 100}]
        }
        for i in range(50)
    ]
    
    start_time = time.time()
    results = skill.batch_create_quotations(quotations_data, batch_size=10)
    end_time = time.time()
    
    success_count = sum(1 for r in results if r["success"])
    duration = end_time - start_time
    
    print(f"创建 {success_count}/50 份报价单，耗时 {duration:.2f}秒")
    assert success_count >= 45  # 90% 成功率
    assert duration < 60  # 60 秒内完成
```

---

## 6. 验收标准

### 6.1 功能验收

- [ ] 能够成功创建、查询、发送报价单
- [ ] 报价单确认流程完整
- [ ] 价格表正确应用和计算
- [ ] 产品价格查询准确
- [ ] 批量创建 50 份报价单 < 60 秒

### 6.2 质量验收

- [ ] 单元测试覆盖率 > 80%
- [ ] 所有 P0 功能通过集成测试
- [ ] 无严重安全漏洞
- [ ] 文档完整（README, API 参考，示例）

### 6.3 性能验收

- [ ] 单次 API 调用响应时间 < 1 秒
- [ ] 并发 10 个请求无错误
- [ ] 内存占用 < 100MB

---

## 7. 风险与缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| 价格计算错误 | 高 | 中 | 单元测试覆盖所有价格场景 |
| API Key 管理不当 | 高 | 中 | 使用环境变量，定期轮换 |
| Odoo API 变更 | 高 | 低 | 关注官方文档，版本测试 |
| 订单状态同步延迟 | 中 | 中 | 实现状态轮询和 webhook |
| 并发修改冲突 | 中 | 低 | 乐观锁，版本检查 |

---

## 8. 依赖项

### 8.1 Python 依赖

```txt
# requirements.txt
requests>=2.28.0
pyyaml>=6.0
python-dotenv>=1.0.0
```

### 8.2 系统要求

- Python 3.8+
- Odoo 18.0+ (JSON-2 API 支持)
- 网络连接（HTTPS）

### 8.3 共享依赖

与 odoo-crm-skill 共享:
- OdooClient 类
- 配置管理模块
- 错误处理工具

---

## 9. 与 CRM Skill 的集成

### 9.1 数据流

```
CRM 机会 → 创建报价单 → 销售订单 → 发货 → 发票
```

### 9.2 集成点

1. **机会转报价**:
   ```python
   def create_quotation_from_opportunity(opportunity_id: int) -> dict:
       # 从 CRM 读取机会信息
       opp = crm_skill.get_opportunity(opportunity_id)
       
       # 创建报价单
       quotation = sales_skill.create_quotation(
           partner_id=opp["partner_id"],
           order_lines=opp["expected_products"],
           expected_revenue=opp["expected_revenue"]
       )
       
       return quotation
   ```

2. **订单状态回写**:
   ```python
   def update_opportunity_from_order(opportunity_id: int, order_id: int):
       # 读取订单状态
       order = sales_skill.get_order(order_id)
       
       # 更新机会
       crm_skill.update_opportunity(
           opportunity_id,
           state="quoted" if order["state"] == "sent" else "won"
       )
   ```

---

## 10. 后续改进

### 10.1 短期（3 个月）

- [ ] 支持多货币报价
- [ ] 添加 CLI 工具
- [ ] 支持 Odoo 17.0（XML-RPC 兼容）

### 10.2 中期（6 个月）

- [ ] 智能产品推荐
- [ ] 自动折扣优化
- [ ] 与库存系统集成

### 10.3 长期（1 年）

- [ ] AI 驱动的定价建议
- [ ] 销售预测模型
- [ ] 多渠道销售支持

---

**创建者**: Odoo Knowledge Base Skill 项目组  
**审核者**: [待填写]  
**批准日期**: [待填写]
