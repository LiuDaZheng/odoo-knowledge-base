# API 模块数据结构参考

## XML-RPC 请求/响应结构

### 连接认证

```xml
POST /xmlrpc/2/common HTTP/1.1
Content-Type: text/xml

<?xml version="1.0"?>
<methodCall>
  <methodName>authenticate</methodName>
  <params>
    <param><value><string>database</string></value></param>
    <param><value><string>username</string></value></param>
    <param><value><string>password</string></value></param>
    <param><value><string>{}</string></value></param>
  </params>
</methodCall>

Response:
<methodResponse>
  <params>
    <param><value><int>5</int></value></param>  <!-- uid, False if failed -->
  </params>
</methodResponse>
```

### search()

```xml
<?xml version="1.0"?>
<methodCall>
  <methodName>execute_kw</methodName>
  <params>
    <param><value><string>database</string></value></param>
    <param><value><int>5</int></value></param>           <!-- uid -->
    <param><value><string>password</string></value></param>
    <param><value><string>res.partner</string></value></param>
    <param><value><string>search</string></value></param>
    <params>
      <param>
        <value>
          <array>
            <data>
              <value><array>
                <value><string>customer</string></value>
                <value><string>=</string></value>
                <value><boolean>1</boolean></value>
              </array></value>
            </data>
          </array>
        </value>
      </param>
    </params>
  </params>
</methodCall>

Response: [1, 2, 3, 5, 6, ...]  <!-- IDs array -->
```

### fields_get()

```xml
<?xml version="1.0"?>
<methodCall>
  <methodName>execute_kw</methodName>
  <params>
    <param><value><string>database</string></value></param>
    <param><value><int>5</int></value></param>
    <param><value><string>password</string></value></param>
    <param><value><string>res.partner</string></value></param>
    <param><value><string>fields_get</string></value></param>
    <params>
      <param><value><array><data></data></array></value></param>  <!-- all fields -->
      <param><value><struct>
        <member><name>attributes</name><value><array>
          <data>
            <value><string>type</string></value>
            <value><string>string</string></value>
            <value><string>help</string></value>
            <value><string>required</string></value>
          </data>
        </array></value></member>
      </struct></value></param>
    </params>
  </params>
</methodCall>

Response:
{
  "name": {"type": "char", "string": "Name", "help": false, "required": false},
  "email": {"type": "char", "string": "Email", "help": false, "required": false},
  "customer": {"type": "boolean", "string": "Customer", "help": false, "required": false},
  "date": {"type": "date", "string": "Date", "help": false, "required": false},
  "active": {"type": "boolean", "string": "Active", "help": false, "required": false}
}
```

### search_read()

```xml
<?xml version="1.0"?>
<methodCall>
  <methodName>execute_kw</methodName>
  <params>
    <param>...</param>  <!-- db, uid, pass -->
    <param><value><string>res.partner</string></value></param>
    <param><value><string>search_read</string></value></param>
    <params>
      <param><value><array><data>
        <value><array>
          <value><string>customer</string></value>
          <value><string>=</string></value>
          <value><boolean>1</boolean></value>
        </array></value>
      </data></array></value></param>
      <param><value><array><data>
        <value><string>name</string></value>
        <value><string>email</string></value>
        <value><string>phone</string></value>
      </data></array></value></param>
      <param><value><int>5</int></value></param>  <!-- limit -->
    </params>
  </params>
</methodCall>

Response:
[
  {"id": 1, "name": "Azure Interior", "email": "contact@azure.com", "phone": "+1 (555) 555-5555"},
  {"id": 2, "name": "Lumber Inc",     "email": "info@lumber.com",    "phone": false},
  ...
]
```

## JSON-RPC 请求/响应结构

### 标准格式

```json
// Request (POST /jsonrpc)
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "object",
    "method": "execute_kw",
    "args": ["database", 5, "password", "res.partner", "search_read",
             [[["customer", "=", true]]],
             {"fields": ["name", "email"], "limit": 5}]
  },
  "id": 12345
}

// Response
{
  "jsonrpc": "2.0",
  "result": [
    {"id": 1, "name": "Azure Interior", "email": "contact@azure.com"},
    {"id": 2, "name": "Lumber Inc",     "email": "info@lumber.com"}
  ],
  "id": 12345
}
```

### 认证调用

```json
// Request
{
  "jsonrpc": "2.0",
  "method": "call",
  "params": {
    "service": "common",
    "method": "authenticate",
    "args": ["database", "admin", "admin", "{}"]
  },
  "id": 1
}

// Response: 5 (uid) or false
```

## Domain 过滤器语法

### 基础操作符

| 操作符 | 示例 | 说明 |
|--------|------|------|
| `=` | `["field", "=", "value"]` | 等于 |
| `!=` | `["field", "!=", "value"]` | 不等于 |
| `>` `<` `>=` `<=` | `["amount", ">", 100]` | 比较 |
| `like` | `["name", "like", "test"]` | 模糊匹配（SQL LIKE %value%） |
| `ilike` | `["name", "ilike", "test"]` | 大小写不敏感模糊匹配 |
| `in` | `["id", "in", [1,2,3]]` | 在列表中 |
| `not in` | `["state", "not in", ["done","cancel"]]` | 不在列表中 |
| `child_of` | `["partner_id", "child_of", 5]` | 属于某合作伙伴的子级 |
| `parent_of` | `["category_id", "parent_of", 1]` | 父级分类 |
| `=|` | `["country_id", "=", "Belgium"]` | rec_name 搜索 |

### 组合逻辑

| 逻辑 | 示例 | 说明 |
|------|------|------|
| AND | `["&", condition1, condition2]` | 默认隐含 AND |
| OR | `["|", condition1, condition2]` | 至少满足一个 |
| NOT | `["!", condition]` | 取反 |

### 示例

```python
# 客户 AND 来自 Belgium 且激活
[["customer", "=", True], ["country_id.name", "=", "Belgium"], ["active", "=", True]]

# 订单状态为 draft 或 sent 且金额 > 1000
[["|", ["state", "=", "draft"], ["state", "=", "sent"]], ["amount_total", ">", 1000]]

# 分类是 "用品" 或其子分类
[["categ_id", "child_of", category_id]]
```

## Context 参数结构

```python
context = {
    "lang": "zh_CN",           # 语言设置，影响字段的 string 分翻译
    "tz": "Asia/Shanghai",     # 时区，影响日期时间显示和计算
    "uid": 5,                  # 当前用户 ID
    "allowed_company_ids": [1, 2],  # 多公司模式下允许访问的公司
    "force_company": 1,       # 强制使用某公司
    "no_convert_address": False,   # 地址是否转换
    "bin_size": True,         # 二进制字段返回 bin_size 而非实际数据
}
```

## 常见错误码和响应结构

### 错误响应

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 100,
    "message": "Odoo Server Error",
    "data": {
      "name": "odoo.exceptions.AccessError",
      "debug": "Traceback (most recent call last)...\nAccessError: ..."
    }
  },
  "id": null
}
```

### 错误码对照

| code | 说明 | 常见原因 |
|------|------|---------|
| 100 | RPC 内部错误 | 服务器执行异常 |
| 200 | 认证失败 | 用户名/密码错误 |
| 404 | 模型不存在 | 拼写错误 |
| 404 | 记录不存在 | search 返回空 |
| 300 | 重定向 | 不应该出现在 JSON-RPC |
| 400 | 客户端错误 | 参数格式错误 |

### 认证错误

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": 200,
    "message": "AccessError",
    "data": {
      "name": "odoo.exceptions.AccessError",
      "debug": "AccessError: Access Denied"
    }
  },
  "id": null
}
```

### ORM API 方法对照

| XML-RPC/JSON-RPC | Python ORM | 说明 |
|------------------|------------|------|
| `search(domain)` | `Model.search()` | 搜索返回 IDs |
| `search_count(domain)` | `Model.search_count()` | 计数 |
| `read(ids, fields)` | `Model.read(fields)` | 读取记录 |
| `search_read(...)` | `Model.search_read()` | 搜索+读取合并 |
| `name_search(name, ...)` | `Model.name_search()` | 名称模糊搜索 |
| `create(vals)` | `Model.create()` | 创建记录 |
| `write(ids, vals)` | `Model.write()` | 更新记录 |
| `unlink(ids)` | `Model.unlink()` | 删除记录 |
| `fields_get()` | `Model.fields_get()` | 获取字段元数据 |
| `default_get(fields)` | `Model.default_get()` | 获取默认值 |
| `copy(id, vals)` | `Model.copy()` | 复制记录 |
