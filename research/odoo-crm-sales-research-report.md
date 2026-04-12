# Odoo CRM 和 Sales 模块调研报告

**调研日期**: 2026-04-12  
**调研目标**: 为 odoo-crm-skill 和 odoo-sales-skill 开发提供完整的技术参考  
**版本**: Odoo 19.0 (最新)

---

## 目录

1. [Odoo CRM 模块深度调研](#1-odoo-crm-模块深度调研)
2. [Odoo Sales 模块调研](#2-odoo-sales-模块调研)
3. [Odoo API 技术参考](#3-odoo-api-技术参考)
4. [Skill 开发计划](#4-skill-开发计划)
5. [最佳实践与常见问题](#5-最佳实践与常见问题)

---

## 1. Odoo CRM 模块深度调研

### 1.1 CRM 核心功能

#### 1.1.1 线索（Leads）管理

**定义**: 线索是未 qualificated 的潜在客户，通常来自网站表单、邮件别名或手动创建。

**核心字段** (`crm.lead` 模型):

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | Char | 线索/机会的名称或标题 |
| `contact_name` | Char | 联系人姓名 |
| `email_from` | Char | 主要邮箱地址（用于去重） |
| `phone` | Char | 主要电话号码 |
| `mobile` | Char | 手机号码 |
| `partner_id` | Many2one | 关联的客户/公司（转换后填充） |
| `user_id` | Many2one | 负责的销售人员 |
| `team_id` | Many2one | 销售团队 |
| `stage_id` | Many2one | 当前阶段（管道中的位置） |
| `type` | Selection | 类型：Lead（线索）或 Opportunity（机会） |
| `expected_revenue` | Float | 预期收入 |
| `probability` | Float | 成功概率（0-100%） |
| `date_deadline` | Date | 预计关闭日期 |
| `source_id` | Many2one | 线索来源（UTM Source） |
| `campaign_id` | Many2one | 营销活动（UTM Campaign） |
| `description` | Text | 描述和内部备注 |
| `active` | Boolean | 软删除标志 |

**线索生命周期**:
```
网站表单/邮件 → 线索创建 → 线索分配 → 线索 qualificated → 转换为机会 → 关闭（赢/输）
```

#### 1.1.2 机会（Opportunities）管理

**定义**: 机会是已 qualificated 的线索，具有明确的预期收入和成功概率。

**关键特性**:
- **管道（Pipeline）视图**: Kanban 视图展示各阶段的机会
- **阶段管理**: 可自定义销售阶段（新建、 qualificated、提案、谈判、赢/输）
- **收入预测**: 基于概率的加权收入计算
  ```
  加权收入 = 预期收入 × 成功概率
  ```
- **活动管理**: 安排电话、会议、任务等后续活动

#### 1.1.3 客户（Customers）管理

**客户模型**: `res.partner`

**与 CRM 的集成**:
- 线索转换时自动创建或关联客户
- 客户联系信息自动填充到线索
- 历史交互记录（邮件、电话、会议）统一展示

### 1.2 CRM API 和使用方法

#### 1.2.1 API 类型

Odoo 提供两种外部 API 访问方式:

1. **JSON-2 API** (Odoo 19.0 新推出，推荐)
   - 端点：`/json/2/<model>/<method>`
   - 认证：Bearer Token (API Key)
   - 格式：纯 JSON

2. **XML-RPC / JSON-RPC** (传统方式，Odoo 22.0 将废弃)
   - 端点：`/xmlrpc/2/object`, `/jsonrpc`
   - 认证：用户名 + 密码
   - 格式：XML-RPC 或 JSON-RPC 封装

#### 1.2.2 JSON-2 API 使用示例

**认证头**:
```http
Authorization: bearer <API_KEY>
X-Odoo-Database: <DATABASE_NAME>
Content-Type: application/json
```

**搜索线索**:
```python
import requests

BASE_URL = "https://mycompany.example.com/json/2"
API_KEY = "your_api_key"
headers = {
    "Authorization": f"bearer {API_KEY}",
    "X-Odoo-Database": "mycompany",
}

# 搜索线索
response = requests.post(
    f"{BASE_URL}/crm.lead/search",
    headers=headers,
    json={
        "context": {"lang": "en_US"},
        "domain": [
            ("type", "=", "lead"),
            ("email_from", "ilike", "%@example.com"),
        ],
    },
)
lead_ids = response.json()
```

**读取线索详情**:
```python
# 读取线索
response = requests.post(
    f"{BASE_URL}/crm.lead/read",
    headers=headers,
    json={
        "ids": lead_ids,
        "fields": ["name", "email_from", "phone", "expected_revenue"],
    },
)
leads = response.json()
```

**创建线索**:
```python
# 创建新线索
response = requests.post(
    f"{BASE_URL}/crm.lead/create",
    headers=headers,
    json={
        "name": "网站咨询 - ABC 公司",
        "contact_name": "张三",
        "email_from": "zhangsan@abc.com",
        "phone": "+86 138 0000 0000",
        "type": "lead",
        "team_id": 1,  # 销售团队 ID
        "user_id": 2,  # 销售人员 ID
        "description": "通过网站表单提交的咨询",
    },
)
lead_id = response.json()
```

**转换为机会**:
```python
# 转换线索为机会
response = requests.post(
    f"{BASE_URL}/crm.lead/action_convert",
    headers=headers,
    json={
        "ids": [lead_id],
        "to_opportunity": True,
        "expected_revenue": 50000,
        "probability": 50,
    },
)
```

#### 1.2.3 XML-RPC API 使用示例 (传统方式)

```python
from xmlrpc.client import ServerProxy

# 连接 Odoo
url = "https://mycompany.example.com"
db = "mycompany"
username = "admin"
password = "admin_password"

common = ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = ServerProxy(f'{url}/xmlrpc/2/object')

# 搜索线索
lead_ids = models.execute_kw(
    db, uid, password,
    'crm.lead', 'search',
    [[['type', '=', 'lead']]]
)

# 读取线索
leads = models.execute_kw(
    db, uid, password,
    'crm.lead', 'read',
    [lead_ids, {'fields': ['name', 'email_from']}]
)

# 创建线索
lead_id = models.execute_kw(
    db, uid, password,
    'crm.lead', 'create',
    [{
        'name': '新线索',
        'email_from': 'test@example.com',
        'type': 'lead',
    }]
)
```

### 1.3 CRM 最佳实践

#### 1.3.1 线索管理最佳实践

1. **去重策略**:
   - 使用 `email_from` 或 `email_normalized` 进行去重检查
   - 创建前搜索现有线索，避免重复

2. **自动分配**:
   - 配置销售团队进行轮询分配
   - 基于地域或行业自动分配

3. **线索评分**:
   - 使用显性因素（职位、公司规模）和隐性因素（页面浏览、互动）
   - 设置阈值自动转换为机会

#### 1.3.2 管道管理最佳实践

1. **阶段设计**:
   ```
   新建 → 已联系 → 需求分析 → 方案提案 → 谈判 → 赢/输
   ```
   
2. **自动化规则**:
   - 阶段变更时自动发送跟进邮件
   - 超时未跟进自动提醒

3. **活动计划**:
   - 为每个阶段定义标准活动序列
   - 设置活动截止日期提醒

#### 1.3.3 报告与分析

1. **关键指标**:
   - 线索数量 vs 机会数量
   - 转化率（线索→机会→赢单）
   - 销售周期长度
   - 加权管道价值

2. **标准报告**:
   - **管道分析**: 按阶段、销售人员、团队分组
   - **预期收入报告**: 月度/季度收入预测
   - **赢/输分析**: 失败原因统计
   - **营销归因**: 按来源和活动的线索数量

### 1.4 常见问题和解决方案

#### 问题 1: 创建重复线索

**原因**: 未进行去重检查

**解决方案**:
```python
# 创建前检查
existing = models.execute_kw(
    db, uid, password,
    'crm.lead', 'search',
    [[['email_from', '=', email]]]
)
if not existing:
    # 创建新线索
    ...
```

#### 问题 2: API 认证错误

**原因**: 
- API Key 过期或无效
- 用户权限不足

**解决方案**:
- 使用专用集成用户（bot user）
- 设置合适的 API Key 有效期（建议 1-30 天）
- 定期检查权限配置

#### 问题 3: 线索转换失败

**原因**: 
- 必填字段缺失
- 自定义字段约束

**解决方案**:
- 确保 `partner_id` 或客户信息完整
- 检查自定义字段的默认值
- 调用 `super()` 保留原有逻辑

#### 问题 4: 内部服务器错误 (500)

**原因**: 
- 缺少依赖模块
- 自定义模块异常

**解决方案**:
- 检查服务器日志 `/var/log/odoo/odoo-server.log`
- 验证所有依赖模块已安装
- 在沙箱环境测试 API 调用

---

## 2. Odoo Sales 模块调研

### 2.1 销售流程管理

#### 2.1.1 标准销售流程

```
报价单 (Quotation) → 销售订单 (Sales Order) → 发货 (Delivery) → 发票 (Invoice) → 收款 (Payment)
```

**关键节点**:
1. **报价单**: 发送给客户的提案，包含产品详情和价格
2. **销售订单**: 客户接受报价后自动创建，确认销售
3. **发货**: 产品发货或服务交付
4. **发票**: 基于销售订单或发货创建
5. **收款**: 客户支付发票，完成销售周期

#### 2.1.2 销售订单模型 (`sale.order`)

**核心字段**:

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | Char | 订单编号（确认后自动生成） |
| `partner_id` | Many2one | 客户 |
| `partner_invoice_id` | Many2one | 开票地址 |
| `partner_shipping_id` | Many2one | 发货地址 |
| `pricelist_id` | Many2one | 价格表 |
| `date_order` | Datetime | 订单日期 |
| `validity_date` | Date | 报价有效期 |
| `state` | Selection | 状态：draft, sent, sale, done, cancel |
| `amount_total` | Float | 总金额 |
| `amount_untaxed` | Float | 未税金额 |
| `amount_tax` | Float | 税额 |
| `currency_id` | Many2one | 货币 |
| `user_id` | Many2one | 销售人员 |
| `team_id` | Many2one | 销售团队 |
| `order_line` | One2many | 订单行 (`sale.order.line`) |

**订单行模型** (`sale.order.line`):

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `order_id` | Many2one | 关联的订单 |
| `product_id` | Many2one | 产品 |
| `product_uom_qty` | Float | 数量 |
| `product_uom` | Many2one | 单位 |
| `price_unit` | Float | 单价 |
| `discount` | Float | 折扣 (%) |
| `price_subtotal` | Float | 小计 |
| `price_total` | Float | 总计 |

### 2.2 报价单、销售订单

#### 2.2.1 创建报价单

**手动创建**:
1. 进入 Sales App → Orders → Quotations
2. 点击 New 创建新报价单
3. 选择客户，添加产品行
4. 设置价格表和折扣
5. 发送给客户

**从 CRM 转换**:
- 在机会页面点击"创建报价"
- 自动填充客户信息和预期产品

#### 2.2.2 报价单模板

**功能**: 预定义的报价单模板，包含标准条款、产品和价格

**配置**:
```
Sales → Configuration → Quotation Templates
```

**使用场景**:
- 标准服务套餐
- 常见产品组合
- 标准合同条款

#### 2.2.3 在线确认

**特性**:
- 发送在线报价单链接给客户
- 客户可在线查看、接受、签名
- 支持在线支付（预付款或全款）
- 接受后自动转换为销售订单

### 2.3 价格表和折扣策略

#### 2.3.1 价格表配置

**启用价格表**:
```
Sales → Configuration → Settings → Pricelists
```

**价格表结构**:

1. **基本信息**:
   - 名称
   - 货币
   - 适用公司（多公司环境）
   - 适用国家组

2. **价格规则** (Price Rules):
   - **适用对象**: 所有产品 / 产品类别 / 特定产品 / 产品变体
   - **价格类型**:
     - **折扣 (Discount)**: 百分比折扣（客户可见）
     - **公式 (Formula)**: 基于公式计算（客户不可见折扣）
       - 基础价格
       - 折扣百分比
       - 舍入方法
       - 额外费用
     - **固定价格 (Fixed Price)**: 直接设定价格
   - **最小数量**: 触发价格规则的最低数量
   - **有效期**: 规则的起止日期

**价格规则示例**:

```
规则 1: 批发折扣
- 适用：所有产品
- 类型：折扣
- 折扣：20%
- 最小数量：100

规则 2: 促销定价
- 适用：产品类别 "电子产品"
- 类型：公式
- 基础价格：销售价格
- 折扣：-10% (实际是加价 10%)
- 舍入：10
- 额外费用：-0.01 (使价格以 .99 结尾)

规则 3: VIP 客户固定价
- 适用：特定产品
- 类型：固定价格
- 价格：99.99
- 有效期：2026-01-01 至 2026-12-31
```

#### 2.3.2 折扣策略

**配置折扣**:
```
Sales → Configuration → Settings → Quotations & Sales → Discounts
```

**折扣类型**:

1. **行项目折扣**:
   - 在报价单行直接输入折扣百分比
   - 自动计算折后价格

2. **价格表折扣**:
   - 通过价格表自动应用
   - 可设置可见或隐藏

3. **促销折扣**:
   - 基于时间和条件的自动折扣
   - 可与价格表组合使用

**折扣计算公式**:
```
折后单价 = 原价 × (1 - 折扣%)
行小计 = 折后单价 × 数量
```

#### 2.3.3 客户价格表

**设置**:
- 在客户联系表单的 Sales & Purchase 标签页
- 设置默认价格表
- 自动应用到该客户的所有报价单

### 2.4 销售分析和报表

#### 2.4.1 标准报告

1. **销售分析 (Sales Analysis)**:
   - 按产品、客户、销售人员、团队分组
   - 销售额、数量、利润分析
   - 支持钻取明细

2. **销售订单报告**:
   - 订单状态统计
   - 订单金额分布
   - 订单趋势分析

3. **发票分析**:
   - 已开票 vs 未开票
   - 收款状态
   - 账龄分析

#### 2.4.2 CRM 预测报告

**访问路径**: `CRM → Reporting → Forecast`

**功能**:
- 按预期关闭日期分组机会
- 显示加权收入（预期收入 × 概率）
- 支持拖拽调整关闭日期
- 多种视图：看板、图表、透视表、列表

**计算公式**:
```
加权收入 = 预期收入 × 成功概率%
```

**示例**:
- 机会 A: 预期收入 $10,000, 概率 80% → 加权收入 $8,000
- 机会 B: 预期收入 $50,000, 概率 30% → 加权收入 $15,000
- 月度总加权收入：$23,000

#### 2.4.3 预期收入报告

**访问路径**: `CRM → Reporting → Pipeline`

**功能**:
- 按销售人员、团队、阶段分组
- 显示预期收入和加权收入
- 支持按月、季度、年度筛选

**关键指标**:
- 管道总价值
- 加权管道价值
- 平均交易规模
- 转化率

---

## 3. Odoo API 技术参考

### 3.1 JSON-2 API (推荐)

#### 3.1.1 端点格式

```
POST /json/2/<model>/<method>
```

#### 3.1.2 请求头

```http
Host: <hostname>
Authorization: bearer <API_KEY>
Content-Type: application/json; charset=utf-8
X-Odoo-Database: <database_name> (可选，多数据库时需要)
User-Agent: <your_software_name> (推荐)
```

#### 3.1.3 请求体

```json
{
  "ids": [1, 2, 3],           // 记录 ID 数组（@api.model 方法可省略）
  "context": {"lang": "en_US"}, // 可选上下文
  "domain": [["field", "=", "value"]], // 搜索条件
  "fields": ["name", "email"],  // 返回字段
  "param1": "value1",           // 方法参数
  "param2": "value2"
}
```

#### 3.1.4 响应格式

**成功响应** (200 OK):
```json
[
  {"id": 1, "name": "ABC Company", "email": "info@abc.com"}
]
```

**错误响应** (4xx/5xx):
```json
{
  "name": "werkzeug.exceptions.Unauthorized",
  "message": "Invalid apikey",
  "arguments": ["Invalid apikey", 401],
  "context": {},
  "debug": "Traceback..."
}
```

### 3.2 常用 ORM 方法

#### 3.2.1 搜索和读取

```python
# 搜索
POST /json/2/crm.lead/search
{
  "domain": [["type", "=", "lead"], ["active", "=", true]]
}

# 读取
POST /json/2/crm.lead/read
{
  "ids": [1, 2, 3],
  "fields": ["name", "email_from", "phone"]
}

# 搜索并读取（原子操作，推荐）
POST /json/2/crm.lead/search_read
{
  "domain": [["type", "=", "lead"]],
  "fields": ["name", "email_from"]
}
```

#### 3.2.2 创建、写入、删除

```python
# 创建
POST /json/2/crm.lead/create
{
  "name": "新线索",
  "email_from": "test@example.com",
  "type": "lead"
}

# 写入
POST /json/2/crm.lead/write
{
  "ids": [1],
  "phone": "+86 138 0000 0000",
  "expected_revenue": 50000
}

# 删除
POST /json/2/crm.lead/unlink
{
  "ids": [1, 2, 3]
}
```

#### 3.2.3 业务方法

```python
# 转换线索为机会
POST /json/2/crm.lead/action_convert
{
  "ids": [1],
  "to_opportunity": true,
  "expected_revenue": 50000,
  "probability": 50
}

# 确认销售订单
POST /json/2/sale.order/action_confirm
{
  "ids": [1]
}

# 发送报价单
POST /json/2/sale.order.action_quotation_send
{
  "ids": [1]
}
```

### 3.3 API Key 管理

#### 3.3.1 创建 API Key

1. 进入用户设置
2. 选择目标用户
3. 点击"Create API Key"
4. 设置描述和有效期（最长 3 个月）
5. **立即复制并安全存储**（只显示一次）

#### 3.3.2 最佳实践

- **专用集成用户**: 创建 bot 用户，设置最小权限
- **短有效期**: 交互式使用建议 1 天，自动化建议 7-30 天
- **定期轮换**: 至少每 3 个月轮换一次
- **安全存储**: 使用密码管理器或密钥管理服务

### 3.4 事务处理

**重要**: 每个 JSON-2 API 调用在独立的事务中执行。

**影响**:
- 无法在单个事务中执行多个操作
- 并发修改可能导致数据不一致

**解决方案**:
- 使用原子方法（如 `search_read`）
- 创建自定义方法封装相关业务逻辑
- 使用 `action_*` 前缀的方法（如 `action_confirm`）

---

## 4. Skill 开发计划

### 4.1 odoo-crm-skill 开发计划

#### 4.1.1 Skill 概述

**名称**: odoo-crm-skill  
**目标**: 提供 Odoo CRM 模块的完整操作能力  
**触发器**: "Odoo CRM", "创建线索", "管理机会", "CRM 管道"

#### 4.1.2 功能清单

| 功能类别 | 具体功能 | 优先级 |
|---------|---------|--------|
| **线索管理** | 创建线索 | P0 |
| | 搜索/查询线索 | P0 |
| | 更新线索信息 | P0 |
| | 线索去重检查 | P0 |
| | 批量导入线索 | P1 |
| **机会管理** | 线索转机会 | P0 |
| | 创建机会 | P0 |
| | 更新机会阶段 | P0 |
| | 设置预期收入和概率 | P0 |
| | 赢/输处理 | P1 |
| **管道管理** | 查看管道概览 | P1 |
| | 按阶段筛选 | P1 |
| | 管道分析报告 | P2 |
| **活动管理** | 安排跟进活动 | P1 |
| | 查看活动计划 | P1 |
| | 活动提醒 | P2 |
| **报告分析** | 预期收入报告 | P2 |
| | 转化率分析 | P2 |
| | 销售预测 | P2 |

#### 4.1.3 示例代码

**创建线索**:
```python
def create_lead(
    name: str,
    email: str,
    phone: str = None,
    contact_name: str = None,
    description: str = None,
    team_id: int = None,
    user_id: int = None
) -> dict:
    """
    创建新的 CRM 线索
    
    Args:
        name: 线索名称
        email: 邮箱地址
        phone: 电话号码
        contact_name: 联系人姓名
        description: 描述
        team_id: 销售团队 ID
        user_id: 销售人员 ID
    
    Returns:
        {"success": True, "lead_id": 123}
    """
    # 去重检查
    existing = odoo.search('crm.lead', [['email_from', '=', email]])
    if existing:
        return {"success": False, "error": "线索已存在", "lead_id": existing[0]}
    
    # 创建线索
    lead_data = {
        "name": name,
        "email_from": email,
        "type": "lead",
    }
    if phone:
        lead_data["phone"] = phone
    if contact_name:
        lead_data["contact_name"] = contact_name
    if description:
        lead_data["description"] = description
    if team_id:
        lead_data["team_id"] = team_id
    if user_id:
        lead_data["user_id"] = user_id
    
    lead_id = odoo.create('crm.lead', lead_data)
    return {"success": True, "lead_id": lead_id}
```

**线索转机会**:
```python
def convert_to_opportunity(
    lead_id: int,
    expected_revenue: float = None,
    probability: float = 50
) -> dict:
    """
    将线索转换为机会
    
    Args:
        lead_id: 线索 ID
        expected_revenue: 预期收入
        probability: 成功概率 (0-100)
    
    Returns:
        {"success": True, "opportunity_id": 456}
    """
    result = odoo.execute(
        'crm.lead',
        'action_convert',
        ids=[lead_id],
        to_opportunity=True,
        expected_revenue=expected_revenue,
        probability=probability
    )
    return {"success": True, "opportunity_id": lead_id}
```

**查询管道**:
```python
def get_pipeline(
    stage_ids: list = None,
    user_id: int = None,
    team_id: int = None,
    limit: int = 50
) -> dict:
    """
    获取 CRM 管道概览
    
    Args:
        stage_ids: 阶段 ID 列表
        user_id: 销售人员 ID
        team_id: 团队 ID
        limit: 返回数量限制
    
    Returns:
        {"success": True, "opportunities": [...], "total_revenue": 100000}
    """
    domain = [["type", "=", "opportunity"], ["active", "=", True]]
    
    if stage_ids:
        domain.append(["stage_id", "in", stage_ids])
    if user_id:
        domain.append(["user_id", "=", user_id])
    if team_id:
        domain.append(["team_id", "=", team_id])
    
    opportunities = odoo.search_read(
        'crm.lead',
        domain=domain,
        fields=["name", "partner_id", "expected_revenue", "probability", "stage_id"],
        limit=limit
    )
    
    total_revenue = sum(
        opp.get('expected_revenue', 0) * opp.get('probability', 0) / 100
        for opp in opportunities
    )
    
    return {
        "success": True,
        "opportunities": opportunities,
        "total_revenue": total_revenue,
        "count": len(opportunities)
    }
```

#### 4.1.4 使用场景

**场景 1: 网站表单自动创建线索**
```
用户提交网站联系表单
→ Skill 自动创建 CRM 线索
→ 分配给对应销售团队
→ 发送确认邮件
→ 安排首次跟进活动
```

**场景 2: 线索批量导入**
```
上传 CSV 文件（包含潜在客户列表）
→ Skill 验证数据格式
→ 执行去重检查
→ 批量创建线索
→ 生成导入报告（成功/失败统计）
```

**场景 3: 销售预测**
```
查询本月预期关闭的机会
→ 计算加权收入
→ 按销售人员分组
→ 生成预测报告
→ 与目标对比分析
```

### 4.2 odoo-sales-skill 开发计划

#### 4.2.1 Skill 概述

**名称**: odoo-sales-skill  
**目标**: 提供 Odoo Sales 模块的完整操作能力  
**触发器**: "Odoo Sales", "创建报价", "销售订单", "价格表"

#### 4.2.2 功能清单

| 功能类别 | 具体功能 | 优先级 |
|---------|---------|--------|
| **报价单管理** | 创建报价单 | P0 |
| | 查询报价单 | P0 |
| | 更新报价单 | P0 |
| | 发送报价单 | P0 |
| | 报价单模板应用 | P1 |
| | 在线报价单生成 | P1 |
| **销售订单** | 报价转订单 | P0 |
| | 创建销售订单 | P0 |
| | 确认订单 | P0 |
| | 订单状态跟踪 | P1 |
| | 订单修改 | P1 |
| **价格管理** | 价格表查询 | P1 |
| | 价格表应用 | P1 |
| | 折扣计算 | P1 |
| | 多货币支持 | P2 |
| **产品管理** | 产品查询 | P1 |
| | 产品变体选择 | P1 |
| | 库存检查 | P2 |
| **报告分析** | 销售分析 | P2 |
| | 收入报告 | P2 |
| | 产品性能分析 | P2 |

#### 4.2.3 示例代码

**创建报价单**:
```python
def create_quotation(
    partner_id: int,
    order_lines: list,
    pricelist_id: int = None,
    validity_days: int = 7,
    team_id: int = None,
    user_id: int = None
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
    
    Returns:
        {"success": True, "quotation_id": 789, "amount_total": 1000}
    """
    # 构建订单行
    order_line_data = []
    for line in order_lines:
        order_line_data.append((0, 0, {
            "product_id": line["product_id"],
            "product_uom_qty": line["quantity"],
            "product_uom": line.get("uom_id", 1),
            "price_unit": line.get("price_unit", 0),
            "discount": line.get("discount", 0),
        }))
    
    # 计算有效期
    from datetime import datetime, timedelta
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
    
    quotation_id = odoo.create('sale.order', quotation_data)
    
    # 读取总金额
    quotation = odoo.read('sale.order', [quotation_id], ["amount_total"])[0]
    
    return {
        "success": True,
        "quotation_id": quotation_id,
        "amount_total": quotation.get("amount_total", 0)
    }
```

**确认销售订单**:
```python
def confirm_sale_order(order_id: int) -> dict:
    """
    确认销售订单（报价转订单）
    
    Args:
        order_id: 订单 ID
    
    Returns:
        {"success": True, "order_name": "S00123"}
    """
    # 执行确认操作
    odoo.execute('sale.order', 'action_confirm', ids=[order_id])
    
    # 读取订单信息
    order = odoo.read('sale.order', [order_id], ["name", "state"])[0]
    
    return {
        "success": True,
        "order_name": order.get("name"),
        "state": order.get("state")
    }
```

**应用价格表**:
```python
def apply_pricelist(
    quotation_id: int,
    pricelist_id: int
) -> dict:
    """
    应用价格表到报价单
    
    Args:
        quotation_id: 报价单 ID
        pricelist_id: 价格表 ID
    
    Returns:
        {"success": True, "amount_total": 950}
    """
    # 更新价格表
    odoo.write('sale.order', [quotation_id], {
        "pricelist_id": pricelist_id
    })
    
    # 重新计算价格（可能需要触发重算）
    quotation = odoo.read('sale.order', [quotation_id], [
        "amount_total", "amount_untaxed", "amount_tax"
    ])[0]
    
    return {
        "success": True,
        "amount_total": quotation.get("amount_total"),
        "amount_untaxed": quotation.get("amount_untaxed"),
        "amount_tax": quotation.get("amount_tax")
    }
```

**查询销售分析**:
```python
def get_sales_analysis(
    date_from: str,
    date_to: str,
    group_by: str = "product",
    user_id: int = None
) -> dict:
    """
    获取销售分析报告
    
    Args:
        date_from: 开始日期 (YYYY-MM-DD)
        date_to: 结束日期 (YYYY-MM-DD)
        group_by: 分组维度 (product, customer, salesperson, team)
        user_id: 销售人员 ID
    
    Returns:
        {"success": True, "data": [...], "total_revenue": 100000}
    """
    domain = [
        ["state", "in", ["sale", "done"]],
        ["date_order", ">=", date_from],
        ["date_order", "<=", date_to]
    ]
    
    if user_id:
        domain.append(["user_id", "=", user_id])
    
    # 使用 Odoo 的内置报告功能
    analysis = odoo.search_read(
        'sale.report',
        domain=domain,
        fields=["product_id", "partner_id", "user_id", "price_total"],
        groupby=[group_by]
    )
    
    total_revenue = sum(item.get("price_total", 0) for item in analysis)
    
    return {
        "success": True,
        "data": analysis,
        "total_revenue": total_revenue,
        "count": len(analysis)
    }
```

#### 4.2.4 使用场景

**场景 1: 从机会创建报价单**
```
CRM 机会进入"提案"阶段
→ Skill 自动创建报价单
→ 填充预期产品
→ 应用客户价格表
→ 发送给客户审批
```

**场景 2: 批量报价**
```
上传产品清单和客户需求
→ Skill 批量创建报价单
→ 应用统一折扣策略
→ 生成报价汇总报告
→ 批量发送邮件
```

**场景 3: 销售订单跟踪**
```
查询指定时间段的所有订单
→ 按状态分组（草稿/已确认/已完成）
→ 计算总金额和收款情况
→ 生成订单跟踪报告
→ 标记异常订单（超时未确认）
```

---

## 5. 最佳实践与常见问题

### 5.1 API 集成最佳实践

#### 5.1.1 认证安全

1. **使用专用集成用户**:
   - 创建 bot 用户（如 `api_integration`）
   - 设置最小权限（仅需要的模型访问权）
   - 禁用密码登录，仅使用 API Key

2. **API Key 管理**:
   - 设置合理有效期（7-30 天）
   - 定期轮换（至少每 3 个月）
   - 使用密钥管理服务存储

3. **网络传输**:
   - 始终使用 HTTPS
   - 验证 SSL 证书
   - 不记录敏感信息到日志

#### 5.1.2 错误处理

```python
def safe_api_call(func, *args, **kwargs):
    """安全的 API 调用包装器"""
    try:
        return func(*args, **kwargs)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            log_error("认证失败，检查 API Key")
        elif e.response.status_code == 403:
            log_error("权限不足，检查用户权限")
        elif e.response.status_code == 404:
            log_error("资源不存在")
        elif e.response.status_code >= 500:
            log_error(f"服务器错误：{e.response.status_code}")
        raise
    except requests.exceptions.Timeout:
        log_error("请求超时")
        raise
    except Exception as e:
        log_error(f"未知错误：{str(e)}")
        raise
```

#### 5.1.3 重试机制

```python
import time
from functools import wraps

def retry_on_failure(max_attempts=3, delay=1):
    """失败重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.Timeout, 
                        requests.exceptions.ConnectionError) as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (attempt + 1))  # 指数退避
            return None
        return wrapper
    return decorator
```

#### 5.1.4 批量操作

```python
def batch_create(model, records, batch_size=100):
    """批量创建记录"""
    results = []
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_results = []
        for record in batch:
            try:
                result = odoo.create(model, record)
                batch_results.append({"success": True, "id": result})
            except Exception as e:
                batch_results.append({"success": False, "error": str(e)})
        results.extend(batch_results)
        time.sleep(0.1)  # 避免限流
    return results
```

### 5.2 常见问题排查

#### 问题 1: 认证失败 (401 Unauthorized)

**症状**: API 返回 401 错误

**可能原因**:
- API Key 过期或无效
- API Key 格式错误
- 数据库名称不匹配

**排查步骤**:
1. 检查 API Key 是否在有效期内
2. 确认 Authorization 头格式：`Bearer <API_KEY>`
3. 验证 X-Odoo-Database 头是否正确
4. 尝试重新生成 API Key

#### 问题 2: 权限不足 (403 Forbidden)

**症状**: API 返回 403 错误

**可能原因**:
- 用户没有模型访问权限
- 记录规则限制
- 字段级权限限制

**排查步骤**:
1. 检查用户权限配置
2. 验证访问控制列表 (ACL)
3. 检查记录规则
4. 使用管理员账户测试

#### 问题 3: 数据验证错误

**症状**: 创建/更新记录失败

**可能原因**:
- 必填字段缺失
- 字段格式不正确
- 业务约束违反

**排查步骤**:
1. 检查错误消息中的字段提示
2. 验证必填字段完整
3. 确认字段格式（日期、邮箱等）
4. 检查业务逻辑约束

#### 问题 4: 性能问题

**症状**: API 响应缓慢

**可能原因**:
- 查询数据量过大
- 缺少索引
- 服务器负载高

**优化建议**:
1. 使用 `fields` 参数限制返回字段
2. 使用 `limit` 和 `offset` 分页
3. 优化搜索条件（使用索引字段）
4. 避免 N+1 查询（使用 `search_read`）

### 5.3 开发建议

#### 5.3.1 本地开发环境

1. **使用沙箱数据库**:
   - 永远不要在生产环境直接测试
   - 创建测试数据库用于开发
   - 定期从生产备份恢复测试数据

2. **日志记录**:
   ```python
   import logging
   
   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger('odoo_integration')
   ```

3. **配置管理**:
   ```python
   # config.py
   ODOO_CONFIG = {
       "url": "https://mycompany.odoo.com",
       "database": "mycompany",
       "api_key": os.getenv("ODOO_API_KEY"),
       "timeout": 30,
   }
   ```

#### 5.3.2 测试策略

1. **单元测试**:
   - 测试每个 API 函数
   - Mock Odoo API 响应
   - 覆盖正常和异常场景

2. **集成测试**:
   - 在测试数据库验证完整流程
   - 测试数据创建、读取、更新、删除
   - 验证业务逻辑正确性

3. **性能测试**:
   - 批量操作性能
   - 并发请求测试
   - 响应时间监控

---

## 附录

### A. 参考资源

- **Odoo 官方文档**: https://www.odoo.com/documentation/
- **CRM 文档**: https://www.odoo.com/documentation/19.0/applications/sales/crm.html
- **Sales 文档**: https://www.odoo.com/documentation/19.0/applications/sales/sales.html
- **JSON-2 API**: https://www.odoo.com/documentation/19.0/developer/reference/external_api.html
- **GitHub 示例**: https://github.com/odoo/odoo

### B. 模型字段参考

#### crm.lead 核心字段
```yaml
name: Char - 线索/机会名称
contact_name: Char - 联系人姓名
email_from: Char - 邮箱
phone: Char - 电话
mobile: Char - 手机
partner_id: Many2one(res.partner) - 关联客户
user_id: Many2one(res.users) - 销售人员
team_id: Many2one(crm.team) - 销售团队
stage_id: Many2one(crm.stage) - 阶段
type: Selection - 类型 (lead/opportunity)
expected_revenue: Float - 预期收入
probability: Float - 成功概率
date_deadline: Date - 预计关闭日期
source_id: Many2one(utm.source) - 来源
campaign_id: Many2one(utm.campaign) - 营销活动
```

#### sale.order 核心字段
```yaml
name: Char - 订单编号
partner_id: Many2one(res.partner) - 客户
partner_invoice_id: Many2one(res.partner) - 开票地址
partner_shipping_id: Many2one(res.partner) - 发货地址
pricelist_id: Many2one(product.pricelist) - 价格表
date_order: Datetime - 订单日期
validity_date: Date - 报价有效期
state: Selection - 状态 (draft/sent/sale/done/cancel)
amount_total: Float - 总金额
amount_untaxed: Float - 未税金额
amount_tax: Float - 税额
currency_id: Many2one(res.currency) - 货币
user_id: Many2one(res.users) - 销售人员
team_id: Many2one(crm.team) - 销售团队
order_line: One2many(sale.order.line) - 订单行
```

### C. 错误代码参考

| HTTP 状态码 | 含义 | 处理建议 |
|-----------|------|---------|
| 200 | 成功 | 处理响应数据 |
| 400 | 请求错误 | 检查请求格式和参数 |
| 401 | 未授权 | 检查 API Key |
| 403 | 禁止访问 | 检查用户权限 |
| 404 | 资源不存在 | 验证记录 ID |
| 429 | 请求过多 | 实现限流和重试 |
| 500 | 服务器错误 | 检查服务器日志 |
| 503 | 服务不可用 | 稍后重试 |

---

**报告版本**: 1.0  
**最后更新**: 2026-04-12  
**维护者**: Odoo Knowledge Base Skill 项目组
