# Odoo CRM API Reference

Odoo CRM 模块 API 接口参考文档。

## 认证方式

### API Key 认证

```bash
curl -X POST https://your-company.odoo.com/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "common",
      "method": "authenticate",
      "args": ["database", "username", "api_key"]
    },
    "id": 1
  }'
```

### Session 认证

```bash
# 1. 登录获取 session
curl -X POST https://your-company.odoo.com/web/session/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "db": "database",
      "login": "username",
      "password": "password"
    },
    "id": 1
  }'

# 2. 使用 session cookie 进行后续请求
```

## 线索 (Leads) API

### 创建线索

```bash
POST /jsonrpc
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "database",
      "user_id",
      "password",
      "crm.lead",
      "create",
      [[{
        "name": "潜在客户 - 某某公司",
        "contact_name": "张三",
        "email_from": "zhangsan@example.com",
        "phone": "+86 138 0000 0000",
        "partner_name": "某某科技有限公司",
        "revenue": 500000,
        "priority": "3",
        "tag_ids": [[6, 0, [1, 2]]]
      }]]
    ]
  },
  "id": 1
}
```

**字段说明**:
| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| name | char | ✅ | 线索名称 |
| contact_name | char | ❌ | 联系人姓名 |
| email_from | char | ❌ | 联系邮箱 |
| phone | char | ❌ | 联系电话 |
| partner_name | char | ❌ | 公司名称 |
| revenue | float | ❌ | 预计收入 |
| priority | selection | ❌ | 优先级 (0-3) |
| tag_ids | many2many | ❌ | 标签 ID 列表 |

### 读取线索

```bash
# 读取单个线索
POST /jsonrpc
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "database",
      "user_id",
      "password",
      "crm.lead",
      "read",
      [[lead_id], {
        "fields": ["name", "contact_name", "email_from", "phone", "stage_id"]
      }]
    ]
  },
  "id": 1
}

# 搜索并读取
POST /jsonrpc
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "database",
      "user_id",
      "password",
      "crm.lead",
      "search_read",
      [
        [["stage_id", "=", "new"]],
        {"fields": ["name", "contact_name", "email_from"], "limit": 20}
      ]
    ]
  },
  "id": 1
}
```

### 更新线索

```bash
POST /jsonrpc
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "database",
      "user_id",
      "password",
      "crm.lead",
      "write",
      [
        [lead_id],
        {
          "name": "更新后的名称",
          "priority": "3",
          "stage_id": 5
        }
      ]
    ]
  },
  "id": 1
}
```

### 删除线索

```bash
POST /jsonrpc
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "database",
      "user_id",
      "password",
      "crm.lead",
      "unlink",
      [[lead_id]]
    ]
  },
  "id": 1
}
```

### 转化线索

```bash
# 转化为机会
POST /jsonrpc
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "database",
      "user_id",
      "password",
      "crm.lead",
      "convert_to_opportunity",
      [[lead_id], {
        "opportunity_name": "某某公司 - ERP 项目",
        "expected_revenue": 500000,
        "probability": 60
      }]
    ]
  },
  "id": 1
}
```

## 机会 (Opportunities) API

### 创建机会

```bash
POST /jsonrpc
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "database",
      "user_id",
      "password",
      "crm.lead",
      "create",
      [[{
        "name": "某某公司 - CRM 系统项目",
        "partner_id": 123,
        "expected_revenue": 300000,
        "probability": 50,
        "stage_id": 5,
        "user_id": 5,
        "date_deadline": "2026-05-30",
        "tag_ids": [[6, 0, [1, 2]]]
      }]]
    ]
  },
  "id": 1
}
```

**字段说明**:
| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| name | char | ✅ | 机会名称 |
| partner_id | many2one | ✅ | 客户 ID |
| expected_revenue | float | ❌ | 预计收入 |
| probability | integer | ❌ | 成功概率 (0-100) |
| stage_id | many2one | ❌ | 管道阶段 ID |
| user_id | many2one | ❌ | 销售负责人 ID |
| date_deadline | date | ❌ | 预计成交日期 |
| tag_ids | many2many | ❌ | 标签 ID 列表 |

### 管道阶段

标准管道阶段（可自定义）:
1. New (新线索)
2. Qualified (已确认)
3. Proposition (方案中)
4. Proposal/Quotation (报价中)
5. Won (赢单)
6. Lost (输单)

## 客户 (Partners) API

### 创建客户

```bash
POST /jsonrpc
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": [
      "database",
      "user_id",
      "password",
      "res.partner",
      "create",
      [[{
        "name": "某某科技有限公司",
        "company_type": "company",
        "email": "info@example.com",
        "phone": "+86 10 8888 8888",
        "website": "https://www.example.com",
        "street": "北京市朝阳区某某路 1 号",
        "city": "北京",
        "zip": "100000",
        "country_id": 82,
        "industry": "制造业",
        "category_id": [[6, 0, [1, 2]]]
      }]]
    ]
  },
  "id": 1
}
```

**字段说明**:
| 字段 | 类型 | 必需 | 描述 |
|------|------|------|------|
| name | char | ✅ | 客户名称 |
| company_type | selection | ❌ | 类型 (company/individual) |
| email | char | ❌ | 邮箱 |
| phone | char | ❌ | 电话 |
| website | char | ❌ | 网站 |
| street | char | ❌ | 街道 |
| city | char | ❌ | 城市 |
| zip | char | ❌ | 邮编 |
| country_id | many2one | ❌ | 国家 ID |
| industry | char | ❌ | 行业 |
| category_id | many2many | ❌ | 标签 ID 列表 |

## 常用筛选条件

### 线索筛选

```python
# 按阶段筛选
[["stage_id", "=", "new"]]

# 按优先级筛选
[["priority", "=", "3"]]

# 按创建日期筛选
[["create_date", ">=", "2026-04-01"]]

# 按负责人筛选
[["user_id", "=", 5]]

# 组合筛选
[["stage_id", "=", "new"], ["priority", "=", "3"], ["user_id", "=", 5]]
```

### 机会筛选

```python
# 按阶段筛选
[["stage_id", "=", 5]]

# 按概率筛选
[["probability", ">=", 70]]

# 按预计收入筛选
[["expected_revenue", ">=", 100000]]

# 按截止日期筛选
[["date_deadline", "<=", "2026-05-31"]]
```

## 错误处理

### 常见错误码

| 错误码 | 描述 | 解决方案 |
|--------|------|---------|
| 401 | 认证失败 | 检查 API Key 或用户名密码 |
| 403 | 权限不足 | 检查用户权限配置 |
| 404 | 记录不存在 | 检查 ID 是否正确 |
| 500 | 服务器错误 | 联系系统管理员 |

### 错误响应示例

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 401,
    "message": "Odoo Server Error",
    "data": {
      "message": "Access denied",
      "debug": "Invalid credentials"
    }
  },
  "id": 1
}
```

---

*最后更新：2026-04-12*
*Odoo 版本：16.0+*
