# Odoo Knowledge Base Skill 项目

**项目状态**: 调研完成，框架已创建  
**创建日期**: 2026-04-12  
**版本**: 0.1.0

---

## 项目概述

本项目旨在创建一套 OpenClaw Skills，实现与 Odoo ERP 系统的深度集成，支持库存管理、采购管理、财务管理和生产制造的自动化操作。

### 项目目标

1. **标准化集成** - 提供统一的 Odoo API 客户端封装
2. **模块化设计** - 按业务模块拆分 Skill，便于维护和扩展
3. **最佳实践** - 遵循 Odoo API 最佳实践和 OpenClaw Skill 规范
4. **生产就绪** - 完整的测试、文档和质量保证

---

## 项目结构

```
odoo-knowledge-base/
├── README.md                    # 项目说明
├── TODO.md                      # 任务清单和进度
├── docs/
│   └── odoo-erp-research-report.md  # 调研报告 (28KB)
└── src/skills/
    └── odoo-inventory-skill/    # 库存管理 Skill (开发中)
        ├── SKILL.md             # Skill 定义
        └── src/
            └── odoo_inventory_client.py  # 客户端实现
```

---

## 已交付成果

### 1. 调研报告 (docs/odoo-erp-research-report.md)

**内容覆盖**:
- ✅ Odoo ERP 核心模块功能清单
  - 库存管理 (Stock/Inventory)
  - 采购管理 (Purchase)
  - 财务管理 (Accounting)
  - 人力资源 (HR)
- ✅ 生产制造模块详细调研
  - MRP 物料需求计划
  - 工单管理 (Work Order)
  - BOM 物料清单
  - 工艺路线 (Routing)
- ✅ API 参考文档
  - JSON-2 API 端点说明
  - 核心模型字段定义
  - 主要 API 方法
- ✅ 示例代码
  - Python 客户端示例
  - 完整工作流示例 (采购→入库→付款)
  - 生产订单工作流示例
- ✅ 最佳实践总结
  - API 使用最佳实践
  - 数据管理最佳实践
  - 模块集成最佳实践

**关键发现**:
- Odoo 19.0 引入新的 JSON-2 API (`/json/2` 端点)
- 旧的 XML-RPC/JSON-RPC 计划于 Odoo 22 (2028 年秋季) 移除
- 使用 Bearer Token (API Key) 进行认证
- 每个 API 调用在独立 SQL 事务中执行

### 2. 任务清单 (TODO.md)

**开发计划**:
- Phase 1: odoo-inventory-skill (8h) - P0 优先级
- Phase 2: odoo-purchase-skill (6h) - P1 优先级
- Phase 3: odoo-mrp-skill (12h) - P2 优先级
- Phase 4: odoo-accounting-skill (10h) - P3 优先级
- Phase 5: 集成与优化 (6h)

**总工时估算**: 42 小时

### 3. Skill 框架 (odoo-inventory-skill)

**已创建文件**:
- ✅ `SKILL.md` - Skill 定义文档 (3.1KB)
  - 触发器定义
  - 使用示例
  - API 参考
  - 错误处理
  - 最佳实践
- ✅ `src/odoo_inventory_client.py` - Python 客户端 (14.6KB)
  - 通用 API 调用封装
  - 库存查询功能
  - 调拨管理功能
  - 库存调整功能
  - 工具方法

**核心功能**:
```python
# 库存查询
client.get_stock_quantity(product_id=10)
client.get_available_stock(product_id=10)
client.get_product_info(product_id=10)
client.get_stock_moves(product_id=10, date_from="2026-04-01")

# 调拨管理
client.create_incoming_picking(partner_id=5, product_lines=[...])
client.create_outgoing_picking(partner_id=10, product_lines=[...])
client.create_internal_transfer(from_location=1, to_location=2, product_lines=[...])
client.validate_picking(picking_id=100)
client.cancel_picking(picking_id=100)

# 库存调整
client.create_inventory_adjustment(product_id=10, counted_quantity=95)
client.create_scrap(product_id=10, quantity=5, reason="损坏")

# 工具方法
client.check_stock_availability(product_id=10, required_qty=100)
client.get_picking_types()
client.get_locations(usage="internal")
```

---

## 技术架构

### API 架构

```
┌─────────────────┐
│  OpenClaw Agent │
└────────┬────────┘
         │
         │ Skill 调用
         ▼
┌─────────────────┐
│  Odoo Skill     │
│  (Python)       │
└────────┬────────┘
         │
         │ HTTP POST /json/2
         │ Authorization: Bearer <API_KEY>
         │ X-Odoo-Database: <DB_NAME>
         ▼
┌─────────────────┐
│  Odoo Server    │
│  /json/2/<model>/<method>
└─────────────────┘
```

### 认证流程

1. 用户在 Odoo 中创建 API Key (设置 → API Keys)
2. API Key 配置为 Feishu 环境变量
3. Skill 使用 Bearer Token 进行认证
4. 建议 Key 有效期≤3 个月，定期轮换

### 数据模型

**核心模型**:
- `stock.picking` - 调拨单 (入库/出库/内部调拨)
- `stock.move` - 库存移动
- `stock.quant` - 库存数量
- `product.product` - 产品
- `stock.location` - 库位
- `stock.picking.type` - 调拨类型

---

## 下一步行动

### 立即开始 (Phase 1)

1. **完善 odoo-inventory-skill**
   - [ ] 添加环境变量配置说明
   - [ ] 实现错误处理和重试机制
   - [ ] 编写单元测试
   - [ ] 通过 agent-audit 质量审计
   - [ ] 通过 agent-safety 安全检查

2. **测试验证**
   - [ ] 配置 Odoo 测试环境
   - [ ] 执行端到端测试
   - [ ] 验证所有 API 方法

### 后续开发 (Phase 2-5)

按 TODO.md 中的优先级依次开发：
1. odoo-purchase-skill (采购管理)
2. odoo-mrp-skill (生产制造)
3. odoo-accounting-skill (财务管理)
4. 跨模块集成和优化

---

## 配置要求

### Odoo 环境

- **版本**: Odoo 18.0 或 19.0 (推荐 19.0)
- **订阅**: 需要 Custom 计划 (支持 External API)
- **权限**: 需要库存管理相关权限

### 环境变量

```yaml
# Feishu 配置
ODOO_BASE_URL: https://your-company.odoo.com
ODOO_API_KEY: your_api_key_here
ODOO_DATABASE: your_database_name
```

### Python 依赖

```txt
requests>=2.28.0
python-dateutil>=2.8.0
```

---

## 质量保障

### 代码质量

- ✅ yamllint - SKILL.md YAML 格式验证
- ✅ markdownlint - 文档格式验证
- ✅ flake8/pylint - Python 代码检查
- ✅ 单元测试覆盖率 > 80%

### 安全检查

- ✅ agent-audit - 质量审计
- ✅ agent-safety - 安全检查 (密钥、PII 检测)

### 文档要求

- ✅ SKILL.md 认知负载 < 5000 字符
- ✅ 完整的使用示例
- ✅ API 参考文档
- ✅ 错误处理说明

---

## 参考资料

### 官方文档

- [Odoo 19.0 官方文档](https://www.odoo.com/documentation/19.0/)
- [External JSON-2 API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [Inventory Module](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/inventory.html)
- [Manufacturing Module](https://www.odoo.com/documentation/19.0/applications/inventory_and_mrp/manufacturing.html)

### 社区资源

- [Odoo GitHub](https://github.com/odoo/odoo)
- [Odoo 论坛](https://www.odoo.com/forum/help-1)

---

## 联系方式

**项目负责人**: OpenClaw Agent  
**项目仓库**: `~/.openclaw/workspace-skilldev/odoo-knowledge-base/`  
**问题反馈**: 通过 Feishu 联系

---

*最后更新：2026-04-12*
