---
name: odoo-crm-skill
description: >
  Odoo CRM 核心功能 Skill。管理线索、机会、客户和销售管道。
  支持线索转化、机会跟进、客户分类、管道阶段管理等核心 CRM 操作。
  Use when: (1) 创建或管理销售线索，(2) 跟进商机机会，(3) 管理客户信息，
  (4) 查看销售管道，(5) 转化线索为客户，(6) 分析 CRM 数据。
---

# Odoo CRM Skill

管理 Odoo CRM 核心业务：线索、机会、客户和销售管道。

## 📖 功能概览

| 功能模块 | 描述 | API 端点 |
|---------|------|---------|
| **线索管理** | 创建、更新、转化销售线索 | `/crm/leads` |
| **机会管理** | 跟踪商机、更新阶段、预测金额 | `/crm/opportunities` |
| **客户管理** | 客户信息、分类、联系记录 | `/res/partners` |
| **销售管道** | 管道阶段、转化率、漏斗分析 | `/crm/pipeline` |

## 🚀 快速开始

### 前置条件

1. **Odoo 实例**: 确保有可访问的 Odoo 实例（v16.0+）
2. **API 访问**: 配置 API Key 或 OAuth 认证
3. **权限**: 用户需有 CRM 模块访问权限

### 配置认证

```bash
# 设置 Odoo 连接信息
export ODOO_URL="https://your-company.odoo.com"
export ODOO_DB="your_database"
export ODOO_API_KEY="your_api_key"
```

或使用配置文件 `~/.openclaw/odoo-config.json`:
```json
{
  "url": "https://your-company.odoo.com",
  "database": "your_database",
  "api_key": "your_api_key",
  "timeout": 30
}
```

## 📋 核心功能

### 1. 线索管理 (Leads)

#### 创建线索

```bash
python3 {baseDir}/scripts/crm.py lead create \
  --name "潜在客户 - 某某公司" \
  --contact_name "张三" \
  --email "zhangsan@example.com" \
  --phone "+86 138 0000 0000" \
  --company "某某科技有限公司" \
  --revenue 500000 \
  --priority high \
  --tags "制造业,华东区"
```

**参数说明**:
- `--name`: 线索名称（必需）
- `--contact_name`: 联系人姓名
- `--email`: 联系邮箱
- `--phone`: 联系电话
- `--company`: 公司名称
- `--revenue`: 预计收入
- `--priority`: 优先级 (low/medium/high)
- `--tags`: 标签（逗号分隔）

#### 查看线索列表

```bash
# 查看所有线索
python3 {baseDir}/scripts/crm.py lead list

# 按状态筛选
python3 {baseDir}/scripts/crm.py lead list --stage new

# 按优先级筛选
python3 {baseDir}/scripts/crm.py lead list --priority high

# 按负责人筛选
python3 {baseDir}/scripts/crm.py lead list --user_id 5

# 分页查看
python3 {baseDir}/scripts/crm.py lead list --limit 20 --offset 0
```

#### 更新线索

```bash
# 更新线索信息
python3 {baseDir}/scripts/crm.py lead update <lead_id> \
  --name "更新后的线索名称" \
  --priority high \
  --stage qualified

# 添加备注
python3 {baseDir}/scripts/crm.py lead update <lead_id> \
  --description "客户对产品价格比较敏感，需要进一步沟通"
```

#### 转化线索

```bash
# 转化线索为机会
python3 {baseDir}/scripts/crm.py lead convert <lead_id> \
  --opportunity_name "某某公司 - ERP 项目" \
  --expected_revenue 500000 \
  --probability 60

# 转化线索为客户
python3 {baseDir}/scripts/crm.py lead convert <lead_id> \
  --create_customer true \
  --create_opportunity true
```

#### 删除线索

```bash
# 软删除（移动到回收站）
python3 {baseDir}/scripts/crm.py lead delete <lead_id>

# 强制删除（不可恢复）
python3 {baseDir}/scripts/crm.py lead delete <lead_id> --force
```

### 2. 机会管理 (Opportunities)

#### 创建机会

```bash
python3 {baseDir}/scripts/crm.py opportunity create \
  --name "某某公司 - CRM 系统项目" \
  --customer_id 123 \
  --expected_revenue 300000 \
  --probability 50 \
  --stage "Proposal/Quotation" \
  --salesperson_id 5 \
  --deadline "2026-05-30" \
  --tags "CRM,软件实施"
```

**参数说明**:
- `--name`: 机会名称（必需）
- `--customer_id`: 客户 ID（必需）
- `--expected_revenue`: 预计收入
- `--probability`: 成功概率 (0-100)
- `--stage`: 管道阶段
- `--salesperson_id`: 销售负责人 ID
- `--deadline`: 预计成交日期
- `--tags`: 标签

#### 查看机会

```bash
# 查看所有机会
python3 {baseDir}/scripts/crm.py opportunity list

# 按阶段筛选
python3 {baseDir}/scripts/crm.py opportunity list --stage "Proposal/Quotation"

# 按概率筛选
python3 {baseDir}/scripts/crm.py opportunity list --min_probability 70

# 按预计收入筛选
python3 {baseDir}/scripts/crm.py opportunity list --min_revenue 100000

# 查看我的机会
python3 {baseDir}/scripts/crm.py opportunity list --my
```

#### 更新机会阶段

```bash
# 推进到下一阶段
python3 {baseDir}/scripts/crm.py opportunity update <opportunity_id> \
  --stage "Proposal/Quotation" \
  --probability 60

# 更新预计收入
python3 {baseDir}/scripts/crm.py opportunity update <opportunity_id> \
  --expected_revenue 450000

# 添加活动记录
python3 {baseDir}/scripts/crm.py opportunity update <opportunity_id> \
  --activity "电话跟进" \
  --activity_note "客户确认预算已获批，下周安排演示"
```

#### 机会分析

```bash
# 查看管道漏斗
python3 {baseDir}/scripts/crm.py opportunity pipeline

# 查看预测收入
python3 {baseDir}/scripts/crm.py opportunity forecast

# 查看转化率
python3 {baseDir}/scripts/crm.py opportunity conversion
```

### 3. 客户管理 (Customers)

#### 创建客户

```bash
python3 {baseDir}/scripts/crm.py customer create \
  --name "某某科技有限公司" \
  --type company \
  --email "info@example.com" \
  --phone "+86 10 8888 8888" \
  --website "https://www.example.com" \
  --street "北京市朝阳区某某路 1 号" \
  --city "北京" \
  --zip "100000" \
  --country "中国" \
  --industry "制造业" \
  --tags "VIP,华东区"
```

**参数说明**:
- `--name`: 客户名称（必需）
- `--type`: 类型 (company/individual)
- `--email`: 邮箱
- `--phone`: 电话
- `--website`: 网站
- `--street`: 街道地址
- `--city`: 城市
- `--zip`: 邮编
- `--country`: 国家
- `--industry`: 行业
- `--tags`: 标签

#### 查看客户

```bash
# 查看所有客户
python3 {baseDir}/scripts/crm.py customer list

# 搜索客户
python3 {baseDir}/scripts/crm.py customer search --query "某某科技"

# 按行业筛选
python3 {baseDir}/scripts/crm.py customer list --industry "制造业"

# 按标签筛选
python3 {baseDir}/scripts/crm.py customer list --tags "VIP"

# 查看客户详情
python3 {baseDir}/scripts/crm.py customer get <customer_id>
```

#### 更新客户

```bash
# 更新客户信息
python3 {baseDir}/scripts/crm.py customer update <customer_id> \
  --phone "+86 10 9999 9999" \
  --tags "VIP,战略合作"

# 添加联系人
python3 {baseDir}/scripts/crm.py customer add-contact <customer_id> \
  --name "李四" \
  --email "lisi@example.com" \
  --phone "+86 139 0000 0000" \
  --position "采购经理"
```

#### 客户关联

```bash
# 查看客户的所有机会
python3 {baseDir}/scripts/crm.py customer opportunities <customer_id>

# 查看客户的所有线索
python3 {baseDir}/scripts/crm.py customer leads <customer_id>

# 查看客户的销售订单
python3 {baseDir}/scripts/crm.py customer orders <customer_id>
```

### 4. 销售管道 (Pipeline)

#### 查看管道

```bash
# 查看完整管道
python3 {baseDir}/scripts/crm.py pipeline view

# 查看指定阶段的機會
python3 {baseDir}/scripts/crm.py pipeline stage "Proposal/Quotation"

# 按销售人员查看
python3 {baseDir}/scripts/crm.py pipeline by-salesperson
```

#### 管道分析

```bash
# 漏斗分析
python3 {baseDir}/scripts/crm.py pipeline funnel

# 转化率分析
python3 {baseDir}/scripts/crm.py pipeline conversion

# 平均成交周期
python3 {baseDir}/scripts/crm.py pipeline cycle-time
```

#### 管道配置

```bash
# 查看管道阶段配置
python3 {baseDir}/scripts/crm.py pipeline stages

# 添加自定义阶段
python3 {baseDir}/scripts/crm.py pipeline add-stage \
  --name "技术评估" \
  --sequence 3
```

## 📊 报表与分析

### CRM 仪表板

```bash
# 生成 CRM 日报
python3 {baseDir}/scripts/crm.py report daily \
  --date "2026-04-12" \
  --output markdown

# 生成周报
python3 {baseDir}/scripts/crm.py report weekly \
  --week 15 \
  --year 2026 \
  --output markdown

# 生成月报
python3 {baseDir}/scripts/crm.py report monthly \
  --month 4 \
  --year 2026 \
  --output markdown
```

### 销售预测

```bash
# 本月预测
python3 {baseDir}/scripts/crm.py report forecast --period month

# 本季度预测
python3 {baseDir}/scripts/crm.py report forecast --period quarter

# 本年度预测
python3 {baseDir}/scripts/crm.py report forecast --period year
```

### 团队绩效

```bash
# 销售团队排名
python3 {baseDir}/scripts/crm.py report team-ranking

# 个人绩效
python3 {baseDir}/scripts/crm.py report performance --user_id 5

# 线索转化率
python3 {baseDir}/scripts/crm.py report conversion-rate
```

## 🔧 脚本说明

### crm.py

主脚本文件，提供所有 CRM 功能。

**位置**: `{baseDir}/scripts/crm.py`

**用法**:
```bash
python3 crm.py <module> <action> [options]
```

**模块**:
- `lead`: 线索管理
- `opportunity`: 机会管理
- `customer`: 客户管理
- `pipeline`: 管道管理
- `report`: 报表分析

**全局选项**:
- `--config`: 配置文件路径（默认：~/.openclaw/odoo-config.json）
- `--verbose`: 详细输出
- `--json`: JSON 格式输出
- `--dry-run`: 模拟执行

## 📁 目录结构

```
odoo-crm-skill/
├── SKILL.md              # 本文件
├── _meta.json            # 元数据
├── .clawhub/
│   └── origin.json       # Clawhub 配置
├── references/
│   ├── api-reference.md  # API 参考
│   ├── stages.md         # 管道阶段说明
│   └── best-practices.md # 最佳实践
└── scripts/
    ├── crm.py            # 主脚本
    ├── odoo_client.py    # Odoo API 客户端
    └── utils.py          # 工具函数
```

## 🎯 最佳实践

### 线索管理

1. **及时跟进**: 新线索应在 24 小时内联系
2. **信息完整**: 确保线索信息完整（联系方式、需求描述）
3. **合理分类**: 使用标签和优先级进行分类
4. **定期清理**: 每月清理无效线索

### 机会管理

1. **准确预测**: 定期更新成功概率和预计收入
2. **阶段推进**: 及时更新机会阶段
3. **活动记录**: 记录所有客户互动
4. **关闭处理**: 赢单/输单后及时关闭

### 客户管理

1. **信息准确**: 保持客户信息最新
2. **完整联系人**: 记录所有关键联系人
3. **标签分类**: 使用标签进行客户细分
4. **互动历史**: 维护完整的互动记录

### 管道管理

1. **可视化**: 定期查看管道漏斗
2. **瓶颈识别**: 识别转化瓶颈阶段
3. **团队平衡**: 合理分配线索给团队成员
4. **目标设定**: 设定明确的转化目标

## ⚠️ 注意事项

1. **权限控制**: 确保用户有适当的 CRM 访问权限
2. **数据备份**: 定期备份 CRM 数据
3. **API 限制**: 注意 Odoo API 调用频率限制
4. **敏感信息**: 不要存储敏感客户信息在日志中

## 🔗 相关资源

- [Odoo CRM 官方文档](https://www.odoo.com/documentation/16.0/applications/sales/crm.html)
- [Odoo API 文档](https://www.odoo.com/documentation/16.0/developer/api/odoo_api.html)
- [references/api-reference.md](references/api-reference.md) - 详细 API 参考
- [references/stages.md](references/stages.md) - 管道阶段配置
- [references/best-practices.md](references/best-practices.md) - 最佳实践

## 📝 更新日志

### v0.1.0 (2026-04-12)
- 初始版本
- 线索管理功能
- 机会管理功能
- 客户管理功能
- 销售管道功能
- 基础报表功能

---

*Skill 版本：v0.1.0*
*Odoo 兼容版本：16.0+*
*最后更新：2026-04-12*
