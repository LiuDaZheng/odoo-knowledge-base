# Odoo ERP 与生产模块调研报告

**版本**: 1.0  
**调研日期**: 2026-04-12  
**Odoo 版本**: 19.0 (最新)  
**调研人**: OpenClaw Agent

---

## 执行摘要

本报告对 Odoo ERP 系统的核心模块进行了全面调研，包括库存管理、采购管理、财务管理、人力资源以及生产制造模块。调研涵盖了各模块的功能清单、API 参考、示例代码和最佳实践，为后续 Skill 开发提供技术基础。

### 关键发现

1. **API 架构**: Odoo 19.0 引入了新的 JSON-2 API (`/json/2` 端点)，替代旧的 XML-RPC/JSON-RPC（计划于 Odoo 22 移除）
2. **认证方式**: 使用 Bearer Token (API Key) 进行认证，支持数据库级隔离
3. **模块独立性**: 各模块通过独立的模型 (Model) 暴露 API，遵循统一的 ORM 接口
4. **事务处理**: 每个 API 调用在独立 SQL 事务中执行，复杂操作需封装为单一方法

---

## 1. Odoo ERP 核心模块调研

### 1.1 库存管理模块 (Stock/Inventory)

#### 功能清单

| 功能类别 | 具体功能 | 说明 |
|---------|---------|------|
| **产品管理** | 产品类型配置 | 支持可库存、可消耗、服务三种类型 |
| | 计量单位 (UoM) | 支持单位转换和分组 |
| | 包装管理 | 支持多层包装 (Pack-in-Pack) |
| | 产品追踪 | 序列号、批次号、有效期管理 |
| **仓库与存储** | 多仓库管理 | 支持虚拟位置、内部位置、库存位置 |
| | 位置管理 | 仓库、收货区、质检区、包装区 |
| | 库存调整 | 周期盘点、 scrap 报废 |
| **补货管理** | 补货规则 | 最小/最大库存规则 |
| | MTO (Make to Order) | 按订单补货 |
| | 准时制 (JIT) | 按需补货逻辑 |
| | 跨仓库补货 | 仓库间调拨 |
| **收发管理** | 入库/出库流程 | 支持一步、两步、三步收货/发货 |
| | 路线规则 | Push/Pull 规则、直运 (Dropshipping) |
| | 拣货方法 | 批量拣货、集群拣货、波次转移 |
| | 移除策略 | FIFO、LIFO、FEFO、最近位置 |
| **库存估值** | 估值方法 | 标准价格、平均成本 (AVCO)、FIFO |
| | 附加成本 |  landed costs 分摊 |
| **报表** | 预测报表 | 实时库存预测 |
| | 库存报表 | 当前库存状态 |
| | 移动历史 | 产品移动追踪 |

#### API 参考

**核心模型**:

| 模型名称 | 说明 | 主要字段 |
|---------|------|---------|
| `stock.picking` | 库存调拨单 | `picking_type_id`, `origin`, `state`, `scheduled_date`, `move_lines` |
| `stock.move` | 库存移动 | `product_id`, `product_uom_qty`, `product_uom`, `picking_id`, `state` |
| `stock.move.line` | 库存移动明细 | `move_id`, `product_id`, `qty_done`, `location_id`, `location_dest_id` |
| `product.product` | 产品 | `name`, `type`, `uom_id`, `categ_id`, `list_price` |
| `stock.location` | 库位 | `name`, `usage`, `location_id` (父级) |
| `stock.picking.type` | 调拨类型 | `name`, `code` (incoming/outgoing/internal) |
| `stock.quant` | 库存数量 | `product_id`, `location_id`, `quantity`, `reserved_quantity` |

**主要 API 方法**:

```python
# 搜索与读取
POST /json/2/stock.picking/search_read
{
  "domain": [["state", "=", "assigned"]],
  "fields": ["name", "origin", "scheduled_date"],
  "context": {"lang": "en_US"}
}

# 创建调拨单
POST /json/2/stock.picking/create
{
  "picking_type_id": 1,
  "origin": "SO001",
  "scheduled_date": "2026-04-15",
  "move_lines": [
    [0, 0, {
      "product_id": 10,
      "product_uom_qty": 5,
      "product_uom": 1,
      "name": "Product A"
    }]
  ]
}

# 验证调拨
POST /json/2/stock.picking/apply
{
  "ids": [1],
  "context": {}
}

# 库存调整
POST /json/2/stock.quant/create
{
  "product_id": 10,
  "location_id": 1,
  "quantity": 100,
  "inventory_quantity": 95
}
```

#### 示例代码

```python
import requests

BASE_URL = "https://mycompany.odoo.com/json/2"
API_KEY = "your_api_key"
DB_NAME = "mycompany"

headers = {
    "Authorization": f"bearer {API_KEY}",
    "X-Odoo-Database": DB_NAME,
    "Content-Type": "application/json",
    "User-Agent": "odoo-skill/1.0"
}

# 查询可用库存
def get_available_stock(product_id):
    response = requests.post(
        f"{BASE_URL}/stock.quant/search_read",
        headers=headers,
        json={
            "domain": [["product_id", "=", product_id]],
            "fields": ["product_id", "location_id", "quantity", "reserved_quantity"]
        }
    )
    return response.json()

# 创建出库单
def create_delivery(order_name, product_lines):
    move_lines = []
    for line in product_lines:
        move_lines.append([0, 0, {
            "product_id": line["product_id"],
            "product_uom_qty": line["qty"],
            "product_uom": line.get("uom_id", 1),
            "name": line.get("name", "")
        }])
    
    response = requests.post(
        f"{BASE_URL}/stock.picking/create",
        headers=headers,
        json={
            "picking_type_id": 2,  # 出库类型 ID
            "origin": order_name,
            "move_lines": move_lines
        }
    )
    return response.json()

# 验证出库
def validate_delivery(picking_id):
    response = requests.post(
        f"{BASE_URL}/stock.picking/button_validate",
        headers=headers,
        json={"ids": [picking_id]}
    )
    return response.json()
```

#### 最佳实践

1. **库位设计**: 使用虚拟位置组织仓库结构，实际库存只存放在内部位置
2. **批次管理**: 对食品、药品等启用批次/序列号追踪
3. **补货策略**: 结合 MTO 和补货规则，避免库存积压
4. **定期盘点**: 设置周期盘点计划，确保账实相符
5. **API 调用**: 使用 `search_read` 而非分离的 `search` + `read`，保证事务一致性

---

### 1.2 采购管理模块 (Purchase)

#### 功能清单

| 功能类别 | 具体功能 | 说明 |
|---------|---------|------|
| **产品管理** | 供应商价格表 | 多供应商价格、最小起订量 |
| | 补货规则 | 自动补货建议 |
| | 临时补货规则 | 短期补货需求 |
| **交易管理** | 询价单 (RFQ) | 询价、比价 |
| | 采购订单 | 正式采购合同 |
| | 框架协议 (Blanket Order) | 长期采购协议 |
| | 招标 (Call for Tenders) | 公开招标流程 |
| | 采购模板 | 标准化采购条款 |
| **账单管理** | 控制策略 | 按收货/按订单开票 |
| | 供应商账单 | 账单匹配与审批 |
| **高级功能** | 历史需求分析 | 基于历史数据建议采购量 |
| | 采购分析报表 | 采购趋势、供应商绩效 |
| | 供应商成本报表 | 成本分析 |
| | EDI 集成 | 采购 - 销售订单自动导入 |

#### API 参考

**核心模型**:

| 模型名称 | 说明 | 主要字段 |
|---------|------|---------|
| `purchase.order` | 采购订单 | `partner_id`, `order_line`, `state`, `date_order`, `date_approve` |
| `purchase.order.line` | 采购订单明细 | `order_id`, `product_id`, `product_qty`, `price_unit`, `taxes_id` |
| `product.supplierinfo` | 供应商信息 | `name` (供应商), `product_id`, `price`, `min_qty`, `delay` |
| `stock.rule` | 补货规则 | `name`, `action`, `picking_type_id`, `location_src_id` |

**主要 API 方法**:

```python
# 创建询价单
POST /json/2/purchase.order/create
{
  "partner_id": 5,
  "order_line": [
    [0, 0, {
      "product_id": 10,
      "product_qty": 100,
      "price_unit": 25.50,
      "product_uom": 1,
      "date_planned": "2026-04-20"
    }]
  ],
  "date_order": "2026-04-12"
}

# 确认订单
POST /json/2/purchase.order/button_confirm
{
  "ids": [1]
}

# 创建供应商账单
POST /json/2/account.move/create
{
  "move_type": "in_invoice",
  "partner_id": 5,
  "invoice_line_ids": [
    [0, 0, {
      "product_id": 10,
      "quantity": 100,
      "price_unit": 25.50
    }]
  ],
  "purchase_id": 1  # 关联采购订单
}
```

#### 示例代码

```python
# 创建采购订单
def create_purchase_order(supplier_id, order_lines):
    lines = []
    for line in order_lines:
        lines.append([0, 0, {
            "product_id": line["product_id"],
            "product_qty": line["qty"],
            "price_unit": line["price"],
            "product_uom": line.get("uom_id", 1),
            "date_planned": line.get("delivery_date", "2026-04-20")
        }])
    
    response = requests.post(
        f"{BASE_URL}/purchase.order/create",
        headers=headers,
        json={
            "partner_id": supplier_id,
            "order_line": lines,
            "date_order": datetime.now().isoformat()
        }
    )
    return response.json()

# 获取供应商价格表
def get_supplier_pricelist(supplier_id, product_ids=None):
    domain = [["name", "=", supplier_id]]
    if product_ids:
        domain.append(["product_id", "in", product_ids])
    
    response = requests.post(
        f"{BASE_URL}/product.supplierinfo/search_read",
        headers=headers,
        json={"domain": domain, "fields": ["product_id", "price", "min_qty", "delay"]}
    )
    return response.json()

# 自动补货建议
def get_replenishment_suggestions():
    response = requests.post(
        f"{BASE_URL}/stock.warehouse.orderpoint/search_read",
        headers=headers,
        json={
            "domain": [],
            "fields": ["product_id", "product_min_qty", "product_max_qty", "qty_multiple"]
        }
    )
    return response.json()
```

#### 最佳实践

1. **供应商管理**: 维护多供应商价格表，设置最小起订量和交货周期
2. **采购策略**: 对常规物料使用补货规则，对项目物料使用 MTO
3. **价格控制**: 使用框架协议锁定长期价格，减少价格波动风险
4. **三单匹配**: 启用采购订单 - 收货单 - 账单三单匹配，防止错误付款
5. **审批流程**: 设置采购金额审批阈值，大额采购需多级审批

---

### 1.3 财务管理模块 (Accounting)

#### 功能清单

| 功能类别 | 具体功能 | 说明 |
|---------|---------|------|
| **基础概念** | 复式记账 | 自动创建借贷分录 |
| | 权责发生制/收付实现制 | 两种会计基础支持 |
| | 多公司 | 同一数据库管理多公司 |
| | 多币种 | 自动汇率更新 |
| **客户发票** | 发票创建 | 支持多种发票类型 |
| | 付款条款 | 分期收款设置 |
| | 电子发票 | 各国电子发票格式 |
| **供应商账单** | 账单录入 | 手工/OCR 自动识别 |
| | 资产管理 | 固定资产折旧 |
| **付款管理** | 在线付款 | 集成支付网关 |
| | 批量付款 | 供应商批量付款 |
| | 发票跟进 | 逾期提醒 |
| **银行账户** | 银行同步 | 自动导入银行流水 |
| | 银行对账 | 自动/手动对账 |
| | 现金登记 | 现金日记账 |
| **报表** | 财务报表 | 资产负债表、利润表、现金流量表 |
| | 税务报表 | VAT 申报表 |
| | 分类账 | 总账、明细账、试算平衡表 |
| | 管理报表 | 预算、分析、审计追踪 |

#### API 参考

**核心模型**:

| 模型名称 | 说明 | 主要字段 |
|---------|------|---------|
| `account.move` | 会计凭证/发票 | `move_type`, `partner_id`, `invoice_line_ids`, `state`, `date` |
| `account.move.line` | 分录明细 | `move_id`, `account_id`, `debit`, `credit`, `product_id` |
| `account.journal` | 日记账 | `name`, `type` (sale/purchase/bank/cash), `code` |
| `account.account` | 会计科目 | `code`, `name`, `user_type_id` |
| `account.payment` | 付款单 | `partner_id`, `amount`, `payment_date`, `payment_type` |
| `account.tax` | 税种 | `name`, `amount`, `type_tax_use`, `account_id` |
| `res.partner` | 合作伙伴 | `name`, `property_account_receivable_id`, `property_account_payable_id` |

**主要 API 方法**:

```python
# 创建客户发票
POST /json/2/account.move/create
{
  "move_type": "out_invoice",
  "partner_id": 10,
  "invoice_line_ids": [
    [0, 0, {
      "product_id": 5,
      "quantity": 2,
      "price_unit": 100.00,
      "tax_ids": [[6, 0, [1]]]  # 关联税 ID
    }]
  ],
  "invoice_date": "2026-04-12",
  "invoice_payment_term_id": 1
}

# 确认发票
POST /json/2/account.move/action_post
{
  "ids": [1]
}

# 创建付款
POST /json/2/account.payment/create
{
  "partner_id": 10,
  "amount": 230.00,
  "payment_date": "2026-04-15",
  "payment_type": "inbound",  # inbound=收款，outbound=付款
  "journal_id": 1
}

# 银行对账
POST /json/2/account.bank.statement.line/create
{
  "statement_id": 1,
  "amount": 500.00,
  "date": "2026-04-12",
  "partner_id": 10,
  "narration": "Payment received"
}
```

#### 示例代码

```python
# 创建发票
def create_invoice(partner_id, invoice_lines, invoice_type="out_invoice"):
    lines = []
    for line in invoice_lines:
        lines.append([0, 0, {
            "product_id": line["product_id"],
            "quantity": line["qty"],
            "price_unit": line["price"],
            "tax_ids": [[6, 0, line.get("tax_ids", [])]]
        }])
    
    response = requests.post(
        f"{BASE_URL}/account.move/create",
        headers=headers,
        json={
            "move_type": invoice_type,
            "partner_id": partner_id,
            "invoice_line_ids": lines,
            "invoice_date": datetime.now().date().isoformat()
        }
    )
    return response.json()

# 获取应收账款
def get_receivable_balance(partner_id=None):
    domain = [["account_id.user_type_id.type", "=", "receivable"]]
    if partner_id:
        domain.append(["partner_id", "=", partner_id])
    
    response = requests.post(
        f"{BASE_URL}/account.move.line/search_read",
        headers=headers,
        json={
            "domain": domain,
            "fields": ["partner_id", "debit", "credit", "balance", "date_maturity"]
        }
    )
    return response.json()

# 银行对账
def reconcile_bank(statement_line_id, move_line_ids):
    response = requests.post(
        f"{BASE_URL}/account.bank.statement.line/process_reconciliation",
        headers=headers,
        json={
            "ids": [statement_line_id],
            "move_line_ids": move_line_ids
        }
    )
    return response.json()

# 获取财务报表
def get_financial_report(report_type):
    # report_type: balance_sheet, profit_loss, cash_flow
    response = requests.post(
        f"{BASE_URL}/account.report/generate",
        headers=headers,
        json={"report_name": report_type, "date": "2026-04-12"}
    )
    return response.json()
```

#### 最佳实践

1. **科目设置**: 根据所在国家使用预置的会计科目表，确保合规
2. **自动化**: 启用银行同步，减少手工录入
3. **对账频率**: 每日/每周进行银行对账，及时发现差异
4. **发票流程**: 使用 OCR 自动识别供应商账单，提高效率
5. **权限控制**: 严格分离制单、审核、过账权限
6. **备份策略**: 定期导出会计数据，确保数据安全

---

### 1.4 人力资源模块 (HR)

#### 功能清单

| 功能类别 | 具体功能 | 说明 |
|---------|---------|------|
| **考勤管理** | 打卡签到 | 支持 PIN、RFID、二维码 |
| | 加班管理 | 加班规则、审批 |
| | 考勤报表 | 出勤率、缺勤分析 |
| | 前台接待 | 访客管理 |
| **员工管理** | 员工档案 | 个人信息、工作信息、技能 |
| | 组织结构 | 部门、汇报关系 |
| | 入职/离职 | onboarding/offboarding 流程 |
| | 设备管理 | 员工设备分配 |
| **绩效管理** | 绩效评估 | 自评、经理评估、360 度反馈 |
| | 目标管理 | 个人目标设定与追踪 |
| | 技能发展 | 技能评估与培训 |
| **招聘管理** | 职位发布 | 招聘需求管理 |
| | 申请追踪 | 候选人管理 |
| | 面试安排 | 面试日程 |
| **培训管理** | 在线课程 | eLearning |
| | 现场培训 | 线下培训管理 |
| | 证书管理 | 证书追踪与到期提醒 |
| **薪酬管理** | 合同管理 | 劳动合同 |
| | 工资计算 | 薪资核算 (需本地化模块) |
| | 成本分析 | 人力成本分析 |
| **车队管理** | 车辆管理 | 车辆档案、保险、维修 |
| | 事故管理 | 事故记录 |
| | 成本分析 | 车辆使用成本 |

#### API 参考

**核心模型**:

| 模型名称 | 说明 | 主要字段 |
|---------|------|---------|
| `hr.employee` | 员工 | `name`, `department_id`, `job_id`, `user_id`, `skills` |
| `hr.department` | 部门 | `name`, `manager_id`, `parent_id` |
| `hr.attendance` | 考勤记录 | `employee_id`, `check_in`, `check_out`, `worked_hours` |
| `hr.contract` | 劳动合同 | `employee_id`, `wage`, `date_start`, `date_end` |
| `hr.appraisal` | 绩效评估 | `employee_id`, `appraisal_date`, `state`, `goals` |
| `hr.job` | 职位 | `name`, `department_id`, `no_of_employee` |
| `hr.leave` | 请假 | `employee_id`, `date_from`, `date_to`, `holiday_status_id` |

**主要 API 方法**:

```python
# 创建员工
POST /json/2/hr.employee/create
{
  "name": "张三",
  "department_id": 3,
  "job_id": 5,
  "work_email": "zhangsan@company.com",
  "skills": [[6, 0, [1, 2]]]
}

# 打卡签到
POST /json/2/hr.attendance/create
{
  "employee_id": 10,
  "check_in": "2026-04-12T09:00:00"
}

# 创建绩效评估
POST /json/2/hr.appraisal/create
{
  "employee_id": 10,
  "appraisal_date": "2026-06-30",
  "goal_ids": [[6, 0, [1, 2, 3]]]
}

# 请假申请
POST /json/2/hr.leave/create
{
  "employee_id": 10,
  "holiday_status_id": 1,  # 年假
  "date_from": "2026-05-01",
  "date_to": "2026-05-05",
  "request_date": "2026-04-12"
}
```

#### 示例代码

```python
# 创建员工
def create_employee(name, department_id, job_id, email):
    response = requests.post(
        f"{BASE_URL}/hr.employee/create",
        headers=headers,
        json={
            "name": name,
            "department_id": department_id,
            "job_id": job_id,
            "work_email": email
        }
    )
    return response.json()

# 获取考勤记录
def get_attendance(employee_id, date_from, date_to):
    response = requests.post(
        f"{BASE_URL}/hr.attendance/search_read",
        headers=headers,
        json={
            "domain": [
                ["employee_id", "=", employee_id],
                ["check_in", ">=", date_from],
                ["check_in", "<=", date_to]
            ],
            "fields": ["employee_id", "check_in", "check_out", "worked_hours"]
        }
    )
    return response.json()

# 创建绩效评估
def create_appraisal(employee_id, appraisal_date, goals):
    response = requests.post(
        f"{BASE_URL}/hr.appraisal/create",
        headers=headers,
        json={
            "employee_id": employee_id,
            "appraisal_date": appraisal_date,
            "goal_ids": [[6, 0, goals]]
        }
    )
    return response.json()

# 获取部门员工列表
def get_department_employees(department_id):
    response = requests.post(
        f"{BASE_URL}/hr.employee/search_read",
        headers=headers,
        json={
            "domain": [["department_id", "=", department_id]],
            "fields": ["name", "job_id", "work_email"]
        }
    )
    return response.json()
```

#### 最佳实践

1. **数据隐私**: 严格保护员工个人信息，设置访问权限
2. **考勤规则**: 明确加班计算规则，避免劳动纠纷
3. **绩效周期**: 设定固定的绩效评估周期 (季度/年度)
4. **培训计划**: 根据技能评估制定个性化培训计划
5. **合规性**: 遵守当地劳动法规，特别是薪酬和休假政策

---

## 2. 生产制造模块调研 (MRP)

### 2.1 MRP 物料需求计划

#### 功能清单

| 功能类别 | 具体功能 | 说明 |
|---------|---------|------|
| **主生产计划** | MPS | 基于需求预测制定生产计划 |
| | 需求预测 | 销售预测导入 |
| | 产能规划 | 工作中心产能评估 |
| **物料计划** | MRP 运算 | 根据 BOM 和需求计算物料需求 |
| | 采购建议 | 自动生成采购申请 |
| | 生产建议 | 自动生成制造订单 |
| **库存集成** | 可用量计算 | 考虑在途、预留库存 |
| | 安全库存 | 最小库存水平 |
| | 提前期 | 采购/生产提前期 |

#### API 参考

**核心模型**:

| 模型名称 | 说明 | 主要字段 |
|---------|------|---------|
| `mrp.production` | 制造订单 | `product_id`, `product_qty`, `bom_id`, `state`, `date_start` |
| `mrp.workorder` | 工单 | `production_id`, `workcenter_id`, `operation_id`, `state` |
| `stock.warehouse.orderpoint` | 补货规则 | `product_id`, `product_min_qty`, `product_max_qty` |
| `mrp.planned_order` | 计划订单 | `product_id`, `qty`, `due_date` |

**主要 API 方法**:

```python
# 创建制造订单
POST /json/2/mrp.production/create
{
  "product_id": 10,
  "product_qty": 100,
  "bom_id": 5,
  "date_start": "2026-04-15",
  "origin": "MPS001"
}

# 确认生产
POST /json/2/mrp.production/button_confirm
{
  "ids": [1]
}

# 获取 MRP 建议
POST /json/2/mrp.production/get_production_proposal
{
  "product_ids": [10, 20],
  "date_range": ["2026-04-01", "2026-04-30"]
}
```

---

### 2.2 工单管理 (Work Order)

#### 功能清单

| 功能类别 | 具体功能 | 说明 |
|---------|---------|------|
| **工单执行** | 工单派发 | 分配给工作中心 |
| | 进度追踪 | 实时进度更新 |
| | 时间记录 | 实际工时记录 |
| **车间控制** | 控制面板 | 车间平板终端 |
| | 质量检查 | 工序质检 |
| | 维护请求 | 设备维护触发 |
| **依赖管理** | 工序顺序 | 前后置工序依赖 |
| | 并行工序 | 多工序同时执行 |

#### API 参考

**核心模型**:

| 模型名称 | 说明 | 主要字段 |
|---------|------|---------|
| `mrp.workorder` | 工单 | `production_id`, `workcenter_id`, `operation_id`, `state` |
| `mrp.workcenter` | 工作中心 | `name`, `capacity`, `costs_hour`, `time_efficiency` |
| `mrp.routing.operation` | 工序 | `name`, `routing_id`, `workcenter_id`, `time_cycle` |

**主要 API 方法**:

```python
# 开始工单
POST /json/2/mrp.workorder/button_start
{
  "ids": [1]
}

# 完成工单
POST /json/2/mrp.workorder/button_finish
{
  "ids": [1]
}

# 记录工时
POST /json/2/mrp.workcenter.time.sheet/create
{
  "workcenter_id": 3,
  "date": "2026-04-12",
  "hours": 8,
  "employee_id": 10
}
```

---

### 2.3 BOM 物料清单

#### 功能清单

| 功能类别 | 具体功能 | 说明 |
|---------|---------|------|
| **BOM 类型** | 制造 BOM | 标准生产用 BOM |
| | 套件 BOM | 销售套件 (不生产) |
| | 分包 BOM | 外包生产 BOM |
| **BOM 结构** | 多层 BOM | 支持子装配件 |
| | 替代料 | 替代物料配置 |
| | 损耗率 | 材料损耗设置 |
| **版本管理** | BOM 版本 | 版本历史追踪 |
| | 生效日期 | 有效期管理 |
| **变体管理** | 产品变体 | 多规格 BOM 配置 |

#### API 参考

**核心模型**:

| 模型名称 | 说明 | 主要字段 |
|---------|------|---------|
| `mrp.bom` | BOM 主表 | `product_id`, `bom_type`, `bom_line_ids`, `routing_id` |
| `mrp.bom.line` | BOM 明细 | `bom_id`, `product_id`, `product_qty`, `product_uom_id` |
| `product.template` | 产品模板 | `name`, `type`, `bom_ids` |

**主要 API 方法**:

```python
# 创建 BOM
POST /json/2/mrp.bom/create
{
  "product_id": 10,
  "bom_type": "normal",
  "bom_line_ids": [
    [0, 0, {
      "product_id": 20,
      "product_qty": 2,
      "product_uom_id": 1
    }],
    [0, 0, {
      "product_id": 30,
      "product_qty": 1,
      "product_uom_id": 1
    }]
  ],
  "product_tmpl_id": 5
}

# 获取 BOM 明细
POST /json/2/mrp.bom/explode
{
  "ids": [1],
  "product_qty": 100
}
```

#### 示例代码

```python
# 创建 BOM
def create_bom(product_id, bom_lines, bom_type="normal"):
    lines = []
    for line in bom_lines:
        lines.append([0, 0, {
            "product_id": line["component_id"],
            "product_qty": line["qty"],
            "product_uom_id": line.get("uom_id", 1)
        }])
    
    response = requests.post(
        f"{BASE_URL}/mrp.bom/create",
        headers=headers,
        json={
            "product_id": product_id,
            "bom_type": bom_type,
            "bom_line_ids": lines
        }
    )
    return response.json()

# 展开 BOM (获取所有层级组件)
def explode_bom(bom_id, quantity):
    response = requests.post(
        f"{BASE_URL}/mrp.bom/explode",
        headers=headers,
        json={"ids": [bom_id], "product_qty": quantity}
    )
    return response.json()

# 获取产品 BOM 列表
def get_product_boms(product_id):
    response = requests.post(
        f"{BASE_URL}/mrp.bom/search_read",
        headers=headers,
        json={
            "domain": [["product_id", "=", product_id]],
            "fields": ["product_id", "bom_type", "bom_line_ids"]
        }
    )
    return response.json()
```

---

### 2.4 工艺路线 (Routing)

#### 功能清单

| 功能类别 | 具体功能 | 说明 |
|---------|---------|------|
| **工序定义** | 工序顺序 | 生产步骤顺序 |
| | 工作中心分配 | 每工序指定工作中心 |
| | 标准工时 | 每工序标准时间 |
| **依赖配置** | 前后置关系 | 工序间依赖 |
| | 并行工序 | 可同时执行的工序 |
| **成本计算** | 人工成本 | 基于工时计算 |
| | 机器成本 | 基于机器使用时间 |

#### API 参考

**核心模型**:

| 模型名称 | 说明 | 主要字段 |
|---------|------|---------|
| `mrp.routing` | 工艺路线 | `name`, `operation_ids`, `company_id` |
| `mrp.routing.operation` | 工序 | `name`, `routing_id`, `workcenter_id`, `time_cycle` |
| `mrp.workcenter` | 工作中心 | `name`, `resource_id`, `costs_hour` |

**主要 API 方法**:

```python
# 创建工艺路线
POST /json/2/mrp.routing/create
{
  "name": "Assembly Routing",
  "operation_ids": [
    [0, 0, {
      "name": "Cutting",
      "workcenter_id": 1,
      "time_cycle": 30
    }],
    [0, 0, {
      "name": "Assembly",
      "workcenter_id": 2,
      "time_cycle": 60
    }]
  ]
}

# 关联 BOM 与工艺路线
PATCH /json/2/mrp.bom/write
{
  "ids": [1],
  "routing_id": 5
}
```

#### 最佳实践 (生产模块)

1. **BOM 准确性**: 定期审核 BOM，确保物料用量准确
2. **工艺优化**: 持续改进工艺路线，减少生产时间
3. **产能平衡**: 避免工作中心瓶颈，均衡生产负荷
4. **质量追溯**: 启用批次追踪，实现全流程追溯
5. **数据集成**: 与库存、采购模块紧密集成，确保数据一致性

---

## 3. Skill 开发计划

### 3.1 Skill 架构设计

```
~/.openclaw/skills/
├── odoo-inventory-skill/      # 库存管理 Skill
│   ├── SKILL.md
│   ├── src/
│   │   ├── inventory_client.py
│   │   └── operations/
│   │       ├── stock_query.py
│   │       ├── stock_transfer.py
│   │       └── inventory_adjust.py
│   └── tests/
│
├── odoo-purchase-skill/       # 采购管理 Skill
│   ├── SKILL.md
│   ├── src/
│   │   ├── purchase_client.py
│   │   └── operations/
│   │       ├── rfq_create.py
│   │       ├── order_confirm.py
│   │       └── supplier_mgmt.py
│   └── tests/
│
├── odoo-accounting-skill/     # 财务管理 Skill
│   ├── SKILL.md
│   ├── src/
│   │   ├── accounting_client.py
│   │   └── operations/
│   │       ├── invoice_create.py
│   │       ├── payment_process.py
│   │       └── report_generate.py
│   └── tests/
│
└── odoo-mrp-skill/            # 生产制造 Skill
    ├── SKILL.md
    ├── src/
    │   ├── mrp_client.py
    │   └── operations/
    │       ├── production_create.py
    │       ├── workorder_mgmt.py
    │       └── bom_routing.py
    └── tests/
```

### 3.2 开发优先级

| 优先级 | Skill | 复杂度 | 预计工时 | 依赖 |
|-------|-------|-------|---------|------|
| P0 | odoo-inventory-skill | 中 | 8h | 无 |
| P1 | odoo-purchase-skill | 中 | 6h | inventory |
| P2 | odoo-mrp-skill | 高 | 12h | inventory, purchase |
| P3 | odoo-accounting-skill | 高 | 10h | purchase |

### 3.3 通用组件设计

```python
# odoo_client.py - 通用客户端基类
class OdooClient:
    def __init__(self, base_url, api_key, database):
        self.base_url = base_url
        self.api_key = api_key
        self.database = database
        self.headers = {
            "Authorization": f"bearer {api_key}",
            "X-Odoo-Database": database,
            "Content-Type": "application/json"
        }
    
    def call(self, model, method, params=None):
        url = f"{self.base_url}/json/2/{model}/{method}"
        response = requests.post(url, headers=self.headers, json=params or {})
        response.raise_for_status()
        return response.json()
    
    def search_read(self, model, domain, fields=None):
        return self.call(model, "search_read", {
            "domain": domain,
            "fields": fields or []
        })
    
    def create(self, model, values):
        return self.call(model, "create", values)
    
    def write(self, model, ids, values):
        return self.call(model, "write", {"ids": ids, **values})
    
    def unlink(self, model, ids):
        return self.call(model, "unlink", {"ids": ids})
```

---

## 4. API 参考汇总

### 4.1 认证与配置

| 项目 | 说明 |
|-----|------|
| **API 端点** | `/json/2/<model>/<method>` |
| **认证方式** | Bearer Token (API Key) |
| **数据库指定** | `X-Odoo-Database` Header |
| **API Key 创建** | 用户设置 → API Keys → 生成新密钥 |
| **Key 有效期** | 最长 3 个月，建议定期轮换 |

### 4.2 通用 ORM 方法

| 方法 | 说明 | 参数 |
|-----|------|------|
| `search` | 搜索记录 ID | `domain`, `context` |
| `search_read` | 搜索并读取 | `domain`, `fields`, `context` |
| `read` | 读取记录 | `ids`, `fields`, `context` |
| `create` | 创建记录 | 模型字段值 |
| `write` | 更新记录 | `ids`, 字段值 |
| `unlink` | 删除记录 | `ids` |
| `copy` | 复制记录 | `ids`, `default` (覆盖值) |

### 4.3 模块特定方法

| 模块 | 方法 | 说明 |
|-----|------|------|
| **库存** | `button_validate` | 验证调拨单 |
| | `action_assign` | 分配库存 |
| **采购** | `button_confirm` | 确认采购订单 |
| | `action_rfq_send` | 发送询价单 |
| **财务** | `action_post` | 过账发票 |
| | `action_register_payment` | 登记付款 |
| **生产** | `button_confirm` | 确认生产订单 |
| | `button_mark_done` | 标记完成 |

---

## 5. 示例代码汇总

### 5.1 完整工作流示例

```python
"""
完整采购到付款工作流示例
"""
from datetime import datetime, timedelta

# 1. 创建采购订单
po_id = client.create("purchase.order", {
    "partner_id": supplier_id,
    "order_line": [
        [0, 0, {
            "product_id": product_id,
            "product_qty": 100,
            "price_unit": 25.50,
            "date_planned": (datetime.now() + timedelta(days=7)).isoformat()
        }]
    ]
})

# 2. 确认订单
client.call("purchase.order", "button_confirm", {"ids": [po_id]})

# 3. 创建入库单 (自动创建，可通过采购订单关联查询)
pickings = client.search_read("stock.picking", [
    ["origin", "=", f"PO{po_id}"]
], fields=["id", "state"])

# 4. 验证入库
for picking in pickings:
    client.call("stock.picking", "button_validate", {"ids": [picking["id"]]})

# 5. 创建供应商账单
bill_id = client.create("account.move", {
    "move_type": "in_invoice",
    "partner_id": supplier_id,
    "purchase_id": po_id,  # 关联采购订单
    "invoice_line_ids": [
        [0, 0, {
            "product_id": product_id,
            "quantity": 100,
            "price_unit": 25.50
        }]
    ]
})

# 6. 确认账单
client.call("account.move", "action_post", {"ids": [bill_id]})

# 7. 创建付款
payment_id = client.create("account.payment", {
    "partner_id": supplier_id,
    "amount": 2550.00,
    "payment_date": datetime.now().date().isoformat(),
    "payment_type": "outbound",
    "journal_id": 1
})

# 8. 过账付款
client.call("account.payment", "action_post", {"ids": [payment_id]})
```

### 5.2 生产订单工作流

```python
"""
完整生产订单工作流示例
"""

# 1. 创建制造订单
mo_id = client.create("mrp.production", {
    "product_id": product_id,
    "product_qty": 50,
    "bom_id": bom_id,
    "date_start": (datetime.now() + timedelta(days=1)).isoformat()
})

# 2. 确认生产
client.call("mrp.production", "button_confirm", {"ids": [mo_id]})

# 3. 分配物料
client.call("mrp.production", "action_assign", {"ids": [mo_id]})

# 4. 开始生产
client.call("mrp.production", "button_start", {"ids": [mo_id]})

# 5. 记录产成品
client.write("mrp.production", [mo_id], {
    "qty_produced": 50
})

# 6. 完成生产
client.call("mrp.production", "button_mark_done", {"ids": [mo_id]})
```

---

## 6. 最佳实践总结

### 6.1 API 使用最佳实践

1. **事务一致性**: 使用单一方法完成关联操作，避免多调用导致的数据不一致
2. **错误处理**: 捕获并记录 API 错误，实现重试机制
3. **速率限制**: 控制 API 调用频率，避免触发服务器限制
4. **认证安全**: API Key 安全存储，定期轮换，使用专用 Bot 用户
5. **日志记录**: 记录所有 API 调用，便于审计和故障排查

### 6.2 数据管理最佳实践

1. **数据验证**: 在创建/更新前验证数据完整性
2. **批量操作**: 使用批量 API 减少网络往返
3. **增量同步**: 使用 `write_date` 字段实现增量数据同步
4. **数据备份**: 定期导出关键业务数据

### 6.3 模块集成最佳实践

1. **库存 - 采购**: 采购收货自动更新库存
2. **采购 - 财务**: 三单匹配确保付款准确
3. **生产 - 库存**: 生产领料/入库自动过账
4. **生产 - 采购**: MRP 自动生成采购建议

---

## 7. 参考资料

### 7.1 官方文档

- [Odoo 19.0 官方文档](https://www.odoo.com/documentation/19.0/)
- [External JSON-2 API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Inventory Module](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory.html)
- [Purchase Module](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/purchase.html)
- [Accounting Module](https://www.odoo.com/documentation/19.0/applications/finance/accounting.html)
- [HR Module](https://www.odoo.com/documentation/19.0/applications/hr.html)
- [Manufacturing Module](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing.html)

### 7.2 社区资源

- [Odoo GitHub](https://github.com/odoo/odoo)
- [Odoo 论坛](https://www.odoo.com/forum/help-1)
- [Stack Overflow - Odoo 标签](https://stackoverflow.com/questions/tagged/odoo)

---

## 8. 附录

### 8.1 模型字段速查

#### 库存模块
```
stock.picking: id, name, picking_type_id, origin, state, scheduled_date, move_lines
stock.move: id, product_id, product_uom_qty, product_uom, picking_id, state
product.product: id, name, type, uom_id, categ_id, list_price, standard_price
```

#### 采购模块
```
purchase.order: id, name, partner_id, order_line, state, date_order, date_approve
purchase.order.line: id, order_id, product_id, product_qty, price_unit, product_uom
```

#### 财务模块
```
account.move: id, name, move_type, partner_id, invoice_line_ids, state, date, amount_total
account.move.line: id, move_id, account_id, debit, credit, balance, product_id
```

#### 生产模块
```
mrp.production: id, name, product_id, product_qty, bom_id, state, date_start, date_finished
mrp.bom: id, product_id, bom_type, bom_line_ids, routing_id
mrp.workorder: id, production_id, workcenter_id, operation_id, state
```

### 8.2 常见状态码

| 状态 | 采购订单 | 制造订单 | 库存调拨 | 发票 |
|-----|---------|---------|---------|------|
| 草稿 | draft | draft | draft | draft |
| 已确认 | purchase | confirmed | assigned | posted |
| 进行中 | - | progress | done | - |
| 已完成 | done | done | done | paid |
| 已取消 | cancel | cancel | cancel | cancel |

---

**报告结束**

*最后更新：2026-04-12*
