# Odoo Knowledge Base - 全面修复 TODO List

**生成日期**: 2026-04-13  
**来源**: 深度审查报告（Agent 使用视角 + Skill 规范标准）  
**执行方式**: 多 Sub-agent 并行

---

## 🔴 Critical（必须立即修复 - Agent 执行会报错）

### C1: 删除 website-skill 的虚假 CLI 命令
- [ ] 删除 `odoo-website create-page` / `odoo-website edit-page` / `odoo-website optimize-seo` 等不存在的 CLI 调用
- [ ] 改为真实的 Odoo XML-RPC Python API 代码
- [ ] 确保所有示例代码可真实运行

### C2: 删除 ecommerce-skill 的虚假 CLI 命令
- [ ] 删除 `odoo-ecom create-product` / `odoo-ecom list-orders` / `odoo-ecom ship-order` 等不存在 CLI 调用
- [ ] 改为真实的 Odoo XML-RPC Python API 代码

### C3: 修复 website-skill 的断裂脚本引用
- [ ] 删除对 `scripts/batch_create_pages.py` 的引用（文件不存在）
- [ ] 删除对 `scripts/seo_audit.py` 的引用（文件不存在）
- [ ] 选择：要么创建这些脚本，要么删除引用

### C4: 修复 ecommerce-skill 的断裂脚本引用
- [ ] 删除对 `scripts/import_products.py` 的引用（文件不存在）
- [ ] 删除对 `scripts/export_orders.py` 的引用（文件不存在）
- [ ] 选择：要么创建这些脚本，要么删除引用

### C5: 清理 5 个 Skill 的 Frontmatter 违规字段
- [ ] `odoo-crm-skill`: 删除 `tags`, `platforms`, `metadata` 字段
- [ ] `odoo-sales-skill`: 删除 `tags`, `platforms`, `metadata` 字段
- [ ] `odoo-inventory-skill`: 删除 `tags`, `platforms`, `metadata` 字段
- [ ] `odoo-purchase-skill`: 删除 `tags`, `platforms`, `metadata` 字段
- [ ] `odoo-development-skill`: 删除 `version`, `author`, `license`, `metadata`, `triggers` 字段
- [ ] 所有 Skill frontmatter 只保留 `name` 和 `description`

---

## 🟠 High（影响 Agent 可用性）

### H1: 重构 odoo-development-skill（842行 → 渐进式）
- [x] SKILL.md 精简至 200 行以内，只保留导航和核心流程 ✅
- [x] 创建 `references/scaffolding.md`：模块脚手架、目录结构、__manifest__.py ✅
- [x] 创建 `references/testing.md`：单元测试、集成测试、测试运行器 ✅
- [x] 创建 `references/docker.md`：Docker Compose 部署、环境变量、卷挂载 ✅
- [x] 创建 `references/debugging.md`：日志调试、Python 断点、数据库调试 ✅
- [x] 删除空的 `src/` 目录 ✅ (已不存在)

### H2: 清理非规范文件
- [ ] 删除 `odoo-crm-skill/_meta.json`
- [ ] 删除 `odoo-crm-skill/.clawhub/`
- [ ] 删除 `odoo-sales-skill/_meta.json`
- [ ] 删除 `odoo-sales-skill/.clawhub/`
- [ ] 删除 `odoo-inventory-skill/_meta.json`
- [ ] 删除 `odoo-inventory-skill/.clawhub/`
- [ ] 删除 `odoo-purchase-skill/_meta.json`
- [ ] 删除 `odoo-purchase-skill/.clawhub/`

### H3: 为 sales/inventory/purchase/hr 补充 References 文档
- [ ] `odoo-sales-skill/references/order-workflow.md`：报价→订单→发货→开票状态机
- [ ] `odoo-sales-skill/references/pricelist.md`：价格表规则、货币、折扣配置
- [ ] `odoo-sales-skill/references/best-practices.md`：销售最佳实践
- [ ] `odoo-inventory-skill/references/stock-moves.md`：库存移动类型、双条目规则
- [ ] `odoo-inventory-skill/references/warehouse-config.md`：多仓库、路由、提货策略
- [ ] `odoo-inventory-skill/references/best-practices.md`：库存操作最佳实践
- [ ] `odoo-purchase-skill/references/po-workflow.md`：采购申请→询价→订单→收货→对账
- [ ] `odoo-purchase-skill/references/vendor-management.md`：供应商、价格表、交货期
- [ ] `odoo-purchase-skill/references/best-practices.md`：采购最佳实践
- [ ] `odoo-hr-skill/references/employee-lifecycle.md`：员工入职→在职→离职流程
- [ ] `odoo-hr-skill/references/attendance-rules.md`：考勤规则、打卡、异常处理
- [ ] `odoo-hr-skill/references/leave-policy.md`：假期类型、申请审批、余额计算

---

## 📊 NEW: 数据模型 ER 图（每个模块必须）

### D1: odoo-crm-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - Mermaid ER 图：`crm.lead` / `res.partner` / `crm.stage` / `mail.activity` 关系
  - 核心字段说明：lead 字段、机会字段、商务字段
  - 业务对应：每个字段对应 UI 中哪个位置/功能

### D2: odoo-sales-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - Mermaid ER 图：`sale.order` / `sale.order.line` / `res.partner` / `product.pricelist` 关系
  - 核心字段说明：订单头、订单行、状态流转
  - 业务对应：报价单 → 销售订单 → 发货单 → 发票的数据流

### D3: odoo-inventory-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - Mermaid ER 图：`stock.picking` / `stock.move` / `stock.quant` / `stock.location` / `product.product` 关系
  - 核心字段说明：移动类型、库位编码、批次/序列号
  - 业务对应：入库单/出库单/调拨单 与数据表的映射

### D4: odoo-purchase-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - Mermaid ER 图：`purchase.order` / `purchase.order.line` / `res.partner` / `account.move` 关系
  - 核心字段说明：采购订单状态、供应商价格表、三单匹配
  - 业务对应：PO → 收货 → 供应商账单 三单匹配流程

### D5: odoo-accounting-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - Mermaid ER 图：`account.move` / `account.move.line` / `account.account` / `account.journal` / `res.partner` 关系
  - 核心字段说明：借贷记账、科目分类、凭证状态
  - 业务对应：客户发票/供应商账单/日记账分录与数据表映射

### D6: odoo-mrp-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - Mermaid ER 图：`mrp.production` / `mrp.bom` / `mrp.bom.line` / `mrp.workcenter` / `stock.move` 关系
  - 核心字段说明：BOM 版本、工单状态、工时/物料消耗
  - 业务对应：生产订单 → BOM展开 → 物料领用 → 完工入库

### D7: odoo-hr-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - Mermaid ER 图：`hr.employee` / `hr.department` / `hr.job` / `hr.attendance` / `hr.leave` 关系
  - 核心字段说明：员工档案字段、考勤记录字段、假期申请字段
  - 业务对应：员工档案 → 组织架构 → 考勤打卡 → 假期申请审批

### D8: odoo-website-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - Mermaid ER 图：`website` / `ir.ui.view` / `website.menu` / `website.page` 关系
  - 核心字段说明：QWeb 视图 key、页面 URL、SEO meta 字段
  - 业务对应：CMS 页面管理 → 菜单树 → 主题视图继承

### D9: odoo-ecommerce-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - Mermaid ER 图：`product.template` / `product.product` / `sale.order`(购物车) / `payment.transaction` 关系
  - 核心字段说明：电商产品字段、购物车→订单状态、支付流水
  - 业务对应：商品上架 → 加购 → 结账 → 支付 → 履单 完整数据流

### D10: odoo-api-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - 通用 API 数据结构：`fields_get` 返回格式、`search_read` 结果结构、错误码
  - XML-RPC 与 JSON-RPC 响应格式对比
  - 常用模型 API 端点速查

### D11: odoo-architecture-skill 数据模型
- [ ] 创建 `references/data-model.md`
  - `ir.model` / `ir.model.fields` 元模型 ER 图
  - ORM 继承关系图（classical / delegation / prototype）
  - 模块依赖图示意

### D12: odoo-introduction-skill 数据模型（概览）
- [ ] 创建 `references/data-model.md`
  - 各核心模块数据关系总览图（高层次）
  - 模块间数据流动示意

---

## 🟡 Medium（规范性和一致性）

### M1: 统一所有 Skill 的 Progressive Disclosure 设计
- [ ] `odoo-accounting-skill`：整理 SKILL.md，抽离详细内容到 references/
- [ ] `odoo-mrp-skill`：整理 SKILL.md，抽离详细内容到 references/
- [ ] `odoo-hr-skill`：整理 SKILL.md，抽离详细内容到 references/
- [ ] 确保所有 Skill 的 SKILL.md 有导航表指向 references/ 文件

### M2: 去除 SKILL.md 中的元数据脚注
- [ ] `odoo-website-skill`：删除 `*Skill 版本：1.0.0*` `*最后更新：2026-04-12*`
- [ ] `odoo-ecommerce-skill`：删除相同脚注
- [ ] 全局检查其他 Skill 是否有类似内容

### M3: 统一 description 语言策略
- [ ] 所有 Skill description 采用：**中文场景描述 + 英文触发关键词**
- [ ] `odoo-introduction-skill`：补充英文 Use when 触发场景
- [ ] `odoo-architecture-skill`：补充英文触发场景
- [ ] `odoo-development-skill`：重写 description，加入有效触发关键词

---

## 🟢 Low（清洁性）

### L1: 删除空目录
- [ ] 删除 `odoo-development-skill/src/`（空目录，不符合规范）

### L2: 更新 TODO.md
- [ ] 将 TODO.md 从只记录 4 个 Skill 更新为反映全部 13 个 Skill 的真实状态
- [ ] 加入数据模型任务追踪

---

## 📋 任务分配（Sub-agent 并行执行）

| Sub-agent | 负责任务 | 优先级 |
|-----------|---------|-------|
| **Agent-Alpha** | C1~C5 Critical 修复 + H2 清理 + M2/L1 清洁 | P0 |
| **Agent-Beta** | H1 development-skill 重构 + M1 统一渐进式设计 | P0 |
| **Agent-Gamma** | D1~D6 数据模型 ER 图（CRM/Sales/Inventory/Purchase/Accounting/MRP） | P1 |
| **Agent-Delta** | D7~D12 数据模型 ER 图（HR/Website/Ecommerce/API/Architecture/Introduction）+ H3 部分 references | P1 |

---

*生成时间：2026-04-13*  
*总任务数：~60 项*
