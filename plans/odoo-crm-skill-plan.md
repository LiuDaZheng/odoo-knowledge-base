# odoo-crm-skill 开发计划

**项目**: Odoo Knowledge Base Skill  
**Skill 名称**: odoo-crm-skill  
**版本**: 1.0.0  
**创建日期**: 2026-04-12  
**状态**: 规划中

---

## 1. Skill 概述

### 1.1 目标

提供 Odoo CRM 模块的完整操作能力，使 OpenClaw 能够：
- 自动创建和管理线索
- 跟踪机会 pipeline
- 生成销售预测报告
- 与 Odoo CRM 无缝集成

### 1.2 触发器

**主要触发词**:
- "Odoo CRM"
- "创建线索"
- "管理机会"
- "CRM 管道"
- "销售预测"
- "线索转化"

### 1.3 适用场景

1. **市场活动线索导入**: 批量导入展会、网络研讨会收集的线索
2. **网站表单集成**: 自动创建网站提交的线索
3. **销售管道管理**: 定期更新机会状态和预测
4. **销售报告生成**: 自动生成周/月度销售报告

---

## 2. 功能规格

### 2.1 P0 功能（MVP）

| ID | 功能 | 描述 | 优先级 | 工时估算 |
|----|------|------|--------|---------|
| F001 | 创建线索 | 通过 API 创建新的 CRM 线索 | P0 | 4h |
| F002 | 查询线索 | 搜索和读取线索信息 | P0 | 3h |
| F003 | 更新线索 | 更新线索字段（状态、收入等） | P0 | 3h |
| F004 | 线索去重 | 基于邮箱/电话检查重复线索 | P0 | 2h |
| F005 | 线索转机会 | 将 qualificated 线索转换为机会 | P0 | 3h |
| F006 | 创建机会 | 直接创建销售机会 | P0 | 3h |
| F007 | 更新机会阶段 | 移动机会到不同管道阶段 | P0 | 2h |
| F008 | 配置管理 | Odoo 连接配置（URL, API Key, DB） | P0 | 2h |

**P0 总计**: 22h

### 2.2 P1 功能（增强）

| ID | 功能 | 描述 | 优先级 | 工时估算 |
|----|------|------|--------|---------|
| F101 | 批量导入线索 | CSV/Excel 批量导入线索 | P1 | 6h |
| F102 | 机会赢/输处理 | 标记机会为赢或输，记录原因 | P1 | 3h |
| F103 | 管道概览 | 查看当前 pipeline 状态 | P1 | 4h |
| F104 | 活动管理 | 创建和查询跟进活动 | P1 | 4h |
| F105 | 销售团队管理 | 按团队分配和查询线索 | P1 | 3h |
| F106 | 客户关联 | 关联线索到现有客户 | P1 | 3h |

**P1 总计**: 23h

### 2.3 P2 功能（高级）

| ID | 功能 | 描述 | 优先级 | 工时估算 |
|----|------|------|--------|---------|
| F201 | 销售预测报告 | 生成月度/季度销售预测 | P2 | 6h |
| F202 | 转化率分析 | 分析线索→机会→赢单转化率 | P2 | 5h |
| F203 | 营销归因 | 按来源和活動分析线索数量 | P2 | 4h |
| F204 | 自动化规则 | 基于条件的自动分配和跟进 | P2 | 8h |
| F205 | 邮件集成 | 发送跟进邮件和通知 | P2 | 6h |

**P2 总计**: 29h

---

## 3. 技术设计

### 3.1 架构

```
┌─────────────────────────────────────────────────┐
│              OpenClaw Agent                     │
└─────────────────┬───────────────────────────────┘
                  │ 自然语言请求
┌─────────────────▼───────────────────────────────┐
│            odoo-crm-skill                       │
│  ┌─────────────────────────────────────────┐   │
│  │  Command Parser                         │   │
│  │  - 意图识别                             │   │
│  │  - 参数提取                             │   │
│  └─────────────────┬───────────────────────┘   │
│                    │                             │
│  ┌─────────────────▼───────────────────────┐   │
│  │  Business Logic Layer                   │   │
│  │  - create_lead()                        │   │
│  │  - convert_to_opportunity()             │   │
│  │  - get_pipeline()                       │   │
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
│  - CRM Module (crm.lead)                        │
│  - Sales Module (sale.order)                    │
│  - Partner Model (res.partner)                  │
└──────────────────────────────────────────────────┘
```

### 3.2 目录结构

```
odoo-crm-skill/
├── SKILL.md                    # Skill 定义（YAML + 指令）
├── README.md                   # 使用说明
├── requirements.txt            # Python 依赖
├── config.example.yaml         # 配置示例
├── src/
│   ├── __init__.py
│   ├── client.py               # Odoo API 客户端
│   ├── models.py               # 数据模型定义
│   ├── commands/               # 命令实现
│   │   ├── __init__.py
│   │   ├── lead.py             # 线索管理命令
│   │   ├── opportunity.py      # 机会管理命令
│   │   └── pipeline.py         # 管道管理命令
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── deduplication.py    # 去重工具
│   │   └── validators.py       # 数据验证
│   └── tests/                  # 单元测试
│       ├── __init__.py
│       ├── test_lead.py
│       └── test_opportunity.py
└── docs/
    ├── api_reference.md        # API 参考
    └── examples.md             # 使用示例
```

### 3.3 核心 API 设计

#### 3.3.1 Odoo 客户端

```python
class OdooClient:
    def __init__(self, config: dict):
        self.url = config["url"]
        self.database = config["database"]
        self.api_key = config["api_key"]
        self.timeout = config.get("timeout", 30)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"bearer {self.api_key}",
            "X-Odoo-Database": self.database,
            "Content-Type": "application/json",
        })
    
    def search(self, model: str, domain: list, limit: int = 80) -> list:
        """搜索记录"""
        endpoint = f"/json/2/{model}/search"
        payload = {"domain": domain, "limit": limit}
        response = self.session.post(
            f"{self.url}{endpoint}",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def read(self, model: str, ids: list, fields: list = None) -> list:
        """读取记录"""
        endpoint = f"/json/2/{model}/read"
        payload = {"ids": ids}
        if fields:
            payload["fields"] = fields
        response = self.session.post(
            f"{self.url}{endpoint}",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def search_read(self, model: str, domain: list, fields: list = None, limit: int = 80) -> list:
        """搜索并读取（原子操作）"""
        endpoint = f"/json/2/{model}/search_read"
        payload = {"domain": domain, "limit": limit}
        if fields:
            payload["fields"] = fields
        response = self.session.post(
            f"{self.url}{endpoint}",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def create(self, model: str, values: dict) -> int:
        """创建记录"""
        endpoint = f"/json/2/{model}/create"
        response = self.session.post(
            f"{self.url}{endpoint}",
            json=values,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def write(self, model: str, ids: list, values: dict) -> bool:
        """更新记录"""
        endpoint = f"/json/2/{model}/write"
        payload = {"ids": ids, **values}
        response = self.session.post(
            f"{self.url}{endpoint}",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def execute(self, model: str, method: str, ids: list = None, **kwargs) -> any:
        """执行方法"""
        endpoint = f"/json/2/{model}/{method}"
        payload = kwargs
        if ids:
            payload["ids"] = ids
        response = self.session.post(
            f"{self.url}{endpoint}",
            json=payload,
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
```

#### 3.3.2 线索管理命令

```python
class LeadCommands:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def create_lead(self, **kwargs) -> dict:
        """创建线索"""
        # 去重检查
        email = kwargs.get("email_from")
        if email:
            existing = self.client.search(
                "crm.lead",
                [["email_from", "=", email], ("type", "=", "lead")]
            )
            if existing:
                return {
                    "success": False,
                    "error": "线索已存在",
                    "lead_id": existing[0]
                }
        
        # 创建线索
        lead_data = {
            "name": kwargs.get("name", "新线索"),
            "email_from": email,
            "type": "lead",
            "contact_name": kwargs.get("contact_name"),
            "phone": kwargs.get("phone"),
            "mobile": kwargs.get("mobile"),
            "description": kwargs.get("description"),
            "team_id": kwargs.get("team_id"),
            "user_id": kwargs.get("user_id"),
        }
        
        # 过滤 None 值
        lead_data = {k: v for k, v in lead_data.items() if v is not None}
        
        lead_id = self.client.create("crm.lead", lead_data)
        return {"success": True, "lead_id": lead_id}
    
    def get_lead(self, lead_id: int) -> dict:
        """获取线索详情"""
        leads = self.client.read(
            "crm.lead",
            [lead_id],
            fields=[
                "name", "contact_name", "email_from", "phone",
                "type", "stage_id", "user_id", "team_id",
                "expected_revenue", "probability", "description"
            ]
        )
        if not leads:
            return {"success": False, "error": "线索不存在"}
        return {"success": True, "lead": leads[0]}
    
    def convert_to_opportunity(
        self,
        lead_id: int,
        expected_revenue: float = None,
        probability: float = 50
    ) -> dict:
        """转换线索为机会"""
        try:
            result = self.client.execute(
                "crm.lead",
                "action_convert",
                ids=[lead_id],
                to_opportunity=True,
                expected_revenue=expected_revenue,
                probability=probability
            )
            return {"success": True, "opportunity_id": lead_id}
        except Exception as e:
            return {"success": False, "error": str(e)}
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

crm:
  default_team_id: 1
  default_user_id: 2
  lead_scoring:
    enabled: true
    threshold: 70
```

---

## 4. 开发计划

### 4.1 阶段 1: MVP 开发（2 周）

**Week 1**:
- [ ] Day 1-2: 项目初始化和基础架构
  - 创建目录结构
  - 实现 OdooClient 基础类
  - 配置管理
- [ ] Day 3-4: 线索管理功能
  - create_lead()
  - get_lead()
  - update_lead()
  - 去重检查
- [ ] Day 5: 单元测试和文档
  - 编写测试用例
  - 编写 API 文档

**Week 2**:
- [ ] Day 1-2: 机会管理功能
  - convert_to_opportunity()
  - create_opportunity()
  - update_stage()
- [ ] Day 3: 管道管理
  - get_pipeline()
  - 按阶段/团队筛选
- [ ] Day 4-5: 集成测试和优化
  - 端到端测试
  - 性能优化
  - 错误处理完善

### 4.2 阶段 2: 增强功能（2 周）

**Week 3**:
- [ ] Day 1-2: 批量操作
  - batch_create_leads()
  - CSV 导入支持
- [ ] Day 3-4: 活动管理
  - create_activity()
  - get_activities()
- [ ] Day 5: 客户关联
  - link_to_partner()

**Week 4**:
- [ ] Day 1-2: 销售团队管理
  - assign_to_team()
  - get_team_leads()
- [ ] Day 3-4: 赢/输处理
  - mark_as_won()
  - mark_as_lost()
- [ ] Day 5: 用户验收测试

### 4.3 阶段 3: 高级功能（2 周）

**Week 5**:
- [ ] Day 1-3: 报告功能
  - sales_forecast()
  - conversion_analysis()
- [ ] Day 4-5: 营销归因
  - attribution_report()

**Week 6**:
- [ ] Day 1-3: 自动化规则
  - auto_assignment()
  - follow_up_reminders()
- [ ] Day 4-5: 最终测试和发布准备
  - 性能测试
  - 安全审计
  - 文档完善

---

## 5. 测试策略

### 5.1 单元测试

```python
# src/tests/test_lead.py
import unittest
from unittest.mock import Mock, patch
from src.commands.lead import LeadCommands

class TestLeadCommands(unittest.TestCase):
    def setUp(self):
        self.mock_client = Mock()
        self.lead_commands = LeadCommands(self.mock_client)
    
    @patch('src.commands.lead.LeadCommands.create_lead')
    def test_create_lead_success(self, mock_create):
        """测试成功创建线索"""
        mock_create.return_value = {"success": True, "lead_id": 123}
        result = self.lead_commands.create_lead(
            name="测试线索",
            email_from="test@example.com"
        )
        self.assertTrue(result["success"])
        self.assertEqual(result["lead_id"], 123)
    
    def test_create_lead_duplicate(self):
        """测试重复线索检测"""
        self.mock_client.search.return_value = [456]
        result = self.lead_commands.create_lead(
            name="测试线索",
            email_from="test@example.com"
        )
        self.assertFalse(result["success"])
        self.assertEqual(result["lead_id"], 456)
```

### 5.2 集成测试

```python
# tests/integration/test_crm_flow.py
def test_lead_to_opportunity_flow():
    """测试线索到机会的完整流程"""
    # 1. 创建线索
    lead_result = skill.create_lead(
        name="集成测试线索",
        email_from="integration@test.com",
        phone="+86 138 0000 0000"
    )
    assert lead_result["success"]
    lead_id = lead_result["lead_id"]
    
    # 2. 查询线索
    lead = skill.get_lead(lead_id)
    assert lead["success"]
    assert lead["lead"]["type"] == "lead"
    
    # 3. 转换为机会
    opp_result = skill.convert_to_opportunity(
        lead_id=lead_id,
        expected_revenue=50000,
        probability=50
    )
    assert opp_result["success"]
    
    # 4. 验证机会
    opportunity = skill.get_lead(lead_id)
    assert opportunity["lead"]["type"] == "opportunity"
    assert opportunity["lead"]["expected_revenue"] == 50000
```

### 5.3 性能测试

```python
# tests/performance/test_bulk_import.py
def test_bulk_lead_creation():
    """测试批量创建线索性能"""
    import time
    
    leads_data = [
        {"name": f"线索{i}", "email_from": f"lead{i}@test.com"}
        for i in range(100)
    ]
    
    start_time = time.time()
    results = skill.batch_create_leads(leads_data, batch_size=20)
    end_time = time.time()
    
    success_count = sum(1 for r in results if r["success"])
    duration = end_time - start_time
    
    print(f"创建 {success_count}/100 条线索，耗时 {duration:.2f}秒")
    assert success_count >= 95  # 95% 成功率
    assert duration < 30  # 30 秒内完成
```

---

## 6. 验收标准

### 6.1 功能验收

- [ ] 能够成功创建、查询、更新线索
- [ ] 线索去重准确率 100%
- [ ] 线索转机会流程完整
- [ ] 管道查询响应时间 < 2 秒
- [ ] 批量导入 100 条线索 < 30 秒

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
| API Key 管理不当 | 高 | 中 | 使用环境变量，定期轮换 |
| Odoo API 变更 | 高 | 低 | 关注官方文档，版本测试 |
| 数据同步冲突 | 中 | 中 | 实现乐观锁，冲突检测 |
| 性能瓶颈 | 中 | 低 | 批量操作，分页查询 |
| 网络不稳定 | 低 | 中 | 重试机制，超时处理 |

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

---

## 9. 后续改进

### 9.1 短期（3 个月）

- [ ] 支持 webhook 实时同步
- [ ] 添加 CLI 工具
- [ ] 支持 Odoo 17.0（XML-RPC 兼容）

### 9.2 中期（6 个月）

- [ ] 机器学习线索评分
- [ ] 智能推荐下一步活动
- [ ] 与营销自动化集成

### 9.3 长期（1 年）

- [ ] 多 Odoo 实例支持
- [ ] 离线模式
- [ ] 高级分析仪表板

---

**创建者**: Odoo Knowledge Base Skill 项目组  
**审核者**: [待填写]  
**批准日期**: [待填写]
