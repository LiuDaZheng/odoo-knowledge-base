# Odoo Knowledge Base Skill 项目

**版本**: 0.1.0  
**创建日期**: 2026-04-12  
**状态**: 调研完成，开发规划中

---

## 项目概述

本项目旨在为 OpenClaw 构建两个专业的 Odoo 集成 Skills：
1. **odoo-crm-skill**: Odoo CRM 模块操作能力
2. **odoo-sales-skill**: Odoo Sales 模块操作能力

通过这两个 Skills，OpenClaw 将能够与 Odoo ERP 系统无缝集成，实现销售流程的自动化管理。

---

## 项目目标

### 核心目标

1. **自动化线索管理**: 自动创建、分配、跟踪销售线索
2. **智能机会跟踪**: 实时更新机会状态，生成销售预测
3. **报价单自动化**: 从机会自动生成报价单，支持批量处理
4. **订单全流程管理**: 从报价到订单确认的完整流程
5. **数据驱动决策**: 生成销售分析报告，支持业务决策

### 成功指标

- [ ] 线索创建响应时间 < 1 秒
- [ ] 批量导入 100 条线索 < 30 秒
- [ ] 单元测试覆盖率 > 80%
- [ ] 用户满意度 > 90%

---

## 目录结构

```
odoo-knowledge-base/
├── README.md                       # 本文件
├── TODO.md                         # 项目任务清单
├── research/                       # 调研报告
│   └── odoo-crm-sales-research-report.md  # 完整调研报告 (26KB)
├── plans/                          # 开发计划
│   ├── odoo-crm-skill-plan.md      # CRM Skill 开发计划 (15KB)
│   └── odoo-sales-skill-plan.md    # Sales Skill 开发计划 (22KB)
├── src/                            # 源代码（开发中）
│   ├── odoo-crm-skill/
│   └── odoo-sales-skill/
├── tests/                          # 测试（开发中）
└── docs/                           # 文档（开发中）
```

---

## 快速开始

### 前置条件

- **Odoo 版本**: 18.0+ (推荐 19.0+)
- **Python 版本**: 3.8+
- **OpenClaw**: 最新版本

### 安装（开发完成后）

```bash
# 克隆项目
git clone https://github.com/your-org/odoo-knowledge-base.git
cd odoo-knowledge-base

# 安装依赖
pip install -r src/odoo-crm-skill/requirements.txt
pip install -r src/odoo-sales-skill/requirements.txt

# 配置 Odoo 连接
cp config.example.yaml config.yaml
# 编辑 config.yaml，填入 Odoo 连接信息
```

### 配置示例

```yaml
# config.yaml
odoo:
  url: "https://your-company.odoo.com"
  database: "your-database"
  api_key: "your-api-key"  # 建议使用环境变量
  timeout: 30

crm:
  default_team_id: 1
  default_user_id: 2

sales:
  default_pricelist_id: 1
  default_validity_days: 7
```

---

## 功能特性

### odoo-crm-skill

#### 线索管理
- ✅ 创建线索（自动去重）
- ✅ 查询线索详情
- ✅ 更新线索信息
- ✅ 线索批量导入
- ✅ 线索分配和跟踪

#### 机会管理
- ✅ 线索转机会
- ✅ 创建销售机会
- ✅ 更新机会阶段
- ✅ 设置预期收入和概率
- ✅ 赢/输处理

#### 管道管理
- ✅ 管道概览
- ✅ 按阶段/团队筛选
- ✅ 销售预测
- ✅ 转化率分析

#### 报告分析
- ✅ 预期收入报告
- ✅ 管道分析
- ✅ 营销归因
- ✅ 销售团队绩效

### odoo-sales-skill

#### 报价单管理
- ✅ 创建报价单
- ✅ 查询报价单
- ✅ 更新报价单
- ✅ 发送报价单（邮件）
- ✅ 报价单模板

#### 销售订单
- ✅ 报价转订单
- ✅ 创建销售订单
- ✅ 订单确认
- ✅ 订单状态跟踪
- ✅ 订单修改

#### 价格管理
- ✅ 价格表查询
- ✅ 应用价格表
- ✅ 折扣计算
- ✅ 客户专属价格
- ✅ 多货币支持

#### 产品管理
- ✅ 产品搜索
- ✅ 产品详情查询
- ✅ 价格查询（含折扣）
- ✅ 库存检查

#### 报告分析
- ✅ 销售分析
- ✅ 收入报告
- ✅ 产品性能分析
- ✅ 客户购买分析

---

## 使用示例

### 示例 1: 创建线索

```python
from odoo_crm_skill import OdooCRM

# 初始化
crm = OdooCRM(config_path="config.yaml")

# 创建线索
result = crm.create_lead(
    name="网站咨询 - ABC 公司",
    email="contact@abc.com",
    phone="+86 138 0000 0000",
    contact_name="张三",
    description="通过网站表单提交的咨询"
)

if result["success"]:
    print(f"线索创建成功，ID: {result['lead_id']}")
else:
    print(f"创建失败：{result['error']}")
```

### 示例 2: 线索转机会

```python
# 转换线索为机会
result = crm.convert_to_opportunity(
    lead_id=123,
    expected_revenue=50000,
    probability=50
)

if result["success"]:
    print(f"转换成功，机会 ID: {result['opportunity_id']}")
```

### 示例 3: 创建报价单

```python
from odoo_sales_skill import OdooSales

# 初始化
sales = OdooSales(config_path="config.yaml")

# 创建报价单
result = sales.create_quotation(
    partner_id=1,
    order_lines=[
        {"product_id": 1, "quantity": 10, "price_unit": 100},
        {"product_id": 2, "quantity": 5, "price_unit": 200}
    ],
    validity_days=7,
    pricelist_id=2
)

if result["success"]:
    print(f"报价单创建成功，ID: {result['quotation_id']}")
    print(f"总金额：{result['amount_total']} {result['currency']}")
```

### 示例 4: 完整销售流程

```python
# 1. 创建线索
lead = crm.create_lead(
    name="新客户咨询",
    email="new@customer.com"
)

# 2. 转换为机会
opportunity = crm.convert_to_opportunity(
    lead_id=lead["lead_id"],
    expected_revenue=100000,
    probability=60
)

# 3. 创建报价单
quotation = sales.create_quotation(
    partner_id=1,
    order_lines=[{"product_id": 1, "quantity": 100, "price_unit": 1000}]
)

# 4. 发送报价单
sales.send_quotation(quotation_id=quotation["quotation_id"])

# 5. 确认订单
order = sales.confirm_quotation(quotation_id=quotation["quotation_id"])

print(f"订单确认成功：{order['order_name']}")
```

---

## API 参考

详细 API 文档请参考：
- [odoo-crm-skill API 参考](src/odoo-crm-skill/docs/api_reference.md)
- [odoo-sales-skill API 参考](src/odoo-sales-skill/docs/api_reference.md)

### 核心 API 摘要

#### CRM Skill

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `create_lead()` | 创建线索 | name, email, phone, ... | {success, lead_id} |
| `get_lead()` | 查询线索 | lead_id | {success, lead} |
| `update_lead()` | 更新线索 | lead_id, **fields | {success} |
| `convert_to_opportunity()` | 线索转机会 | lead_id, revenue, probability | {success, opportunity_id} |
| `get_pipeline()` | 获取管道 | stage_ids, user_id, ... | {success, opportunities} |

#### Sales Skill

| 方法 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `create_quotation()` | 创建报价单 | partner_id, order_lines, ... | {success, quotation_id, amount_total} |
| `get_quotation()` | 查询报价单 | quotation_id | {success, quotation} |
| `send_quotation()` | 发送报价单 | quotation_id, email_to | {success, sent} |
| `confirm_quotation()` | 确认报价 | quotation_id | {success, order_name} |
| `apply_pricelist()` | 应用价格表 | quotation_id, pricelist_id | {success, amount_total} |

---

## 技术架构

### 架构图

```
┌─────────────────────────────────────────────────┐
│              OpenClaw Agent                     │
└─────────────────┬───────────────────────────────┘
                  │ 自然语言请求
┌─────────────────▼───────────────────────────────┐
│         odoo-crm-skill / odoo-sales-skill       │
│  ┌─────────────────────────────────────────┐   │
│  │  Command Parser                         │   │
│  └─────────────────┬───────────────────────┘   │
│                    │                             │
│  ┌─────────────────▼───────────────────────┐   │
│  │  Business Logic Layer                   │   │
│  └─────────────────┬───────────────────────┘   │
│                    │                             │
│  ┌─────────────────▼───────────────────────┐   │
│  │  Odoo API Client (JSON-2)               │   │
│  └─────────────────┬───────────────────────┘   │
└────────────────────┼─────────────────────────────┘
                     │ HTTPS / JSON
┌────────────────────▼─────────────────────────────┐
│              Odoo Server                         │
│  - CRM Module (crm.lead)                        │
│  - Sales Module (sale.order)                    │
│  - Product Module (product.product)             │
└──────────────────────────────────────────────────┘
```

### 技术栈

- **编程语言**: Python 3.8+
- **HTTP 客户端**: requests
- **配置管理**: PyYAML, python-dotenv
- **测试框架**: pytest
- **API 协议**: Odoo JSON-2 API (Odoo 19.0+)

### 设计原则

1. **模块化**: 功能独立，易于维护和扩展
2. **可测试性**: 高测试覆盖率，支持 Mock
3. **容错性**: 完善的错误处理和重试机制
4. **安全性**: API Key 安全管理，敏感数据加密
5. **性能**: 批量操作，缓存机制，分页查询

---

## 开发进度

### 当前状态

- ✅ **阶段 0: 调研与规划** (2026-04-12)
  - 完成 Odoo CRM 和 Sales 模块调研
  - 完成 API 技术调研
  - 创建详细开发计划

- 📋 **阶段 1: odoo-crm-skill 开发** (预计 2026-04-26)
  - 进行中

- 📋 **阶段 2: odoo-sales-skill 开发** (预计 2026-05-10)
  - 待开始

- 📋 **阶段 3: 增强功能** (预计 2026-05-31)
  - 待开始

- 📋 **阶段 4: 集成和优化** (预计 2026-06-07)
  - 待开始

详细进度请参考 [TODO.md](TODO.md)

---

## 贡献指南

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/your-org/odoo-knowledge-base.git
cd odoo-knowledge-base

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest tests/
```

### 代码规范

- 遵循 PEP 8 代码规范
- 所有函数添加类型注解
- 关键函数编写文档字符串
- 提交前运行 linting 和测试

### 提交流程

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 常见问题

### Q: 支持哪些 Odoo 版本？

**A**: 主要支持 Odoo 18.0+，推荐使用 Odoo 19.0+（支持 JSON-2 API）。Odoo 17.0 及以下版本可通过 XML-RPC 兼容模式支持（开发中）。

### Q: 如何获取 Odoo API Key？

**A**: 
1. 登录 Odoo
2. 进入用户设置
3. 选择目标用户
4. 点击"Create API Key"
5. 设置描述和有效期
6. **立即复制并安全存储**（只显示一次）

### Q: 支持 Odoo Online (SaaS) 吗？

**A**: 支持。需要 Custom 或 Enterprise 计划才能访问外部 API。One App Free 和 Standard 计划不支持外部 API 访问。

### Q: 如何处理大量数据导入？

**A**: 使用批量操作功能，建议每批 100 条记录，批次间添加短暂延迟以避免限流。

### Q: API 调用失败如何处理？

**A**: Skill 内置重试机制（默认 3 次，指数退避）。同时会返回详细错误信息，便于排查问题。

---

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 联系方式

- **项目主页**: https://github.com/your-org/odoo-knowledge-base
- **问题反馈**: https://github.com/your-org/odoo-knowledge-base/issues
- **邮箱**: [待填写]

---

## 致谢

感谢以下资源对本项目的帮助：

- [Odoo 官方文档](https://www.odoo.com/documentation/)
- [Odoo GitHub 仓库](https://github.com/odoo/odoo)
- [Odoo 社区论坛](https://www.odoo.com/forum/)

---

**最后更新**: 2026-04-12  
**维护者**: Odoo Knowledge Base Skill 项目组
