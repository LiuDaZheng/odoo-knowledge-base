# Odoo 技术架构与 API 调研报告

**版本**: 1.0  
**调研日期**: 2026-04-12  
**调研范围**: Odoo 17/18/19  
**目标**: 为 Odoo Knowledge Base Skill 项目提供技术基础

---

## 执行摘要

Odoo 是一个基于 Python 和 PostgreSQL 的开源 ERP/CRM 系统，采用三层架构设计：
- **表现层**: HTML5 + JavaScript/CSS + OWL 框架（v15+）
- **逻辑层**: 100% Python，包含 ORM 和业务逻辑
- **数据层**: PostgreSQL（唯一支持的 RDBMS）

Odoo 提供三种外部 API 协议：
1. **XML-RPC** - 传统协议，Odoo 22 将被废弃
2. **JSON-RPC** - 当前推荐，Odoo 22 将被废弃
3. **JSON-2 API** - Odoo 19+ 新引入，推荐用于新集成

**关键发现**: XML-RPC 和 JSON-RPC 将在 Odoo 22（2028 年秋季）被移除，新集成应使用 JSON-2 API。

---

## 1. 技术架构

### 1.1 三层架构

```
┌─────────────────────────────────────────────────────────┐
│                  Presentation Tier                       │
│            HTML5 + JavaScript + CSS + OWL               │
│                  (Web Client/Website)                    │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/JSON-RPC
┌─────────────────────────────────────────────────────────┐
│                    Logic Tier                            │
│              Python + ORM + Business Logic               │
│                 (Odoo Server Core)                       │
└─────────────────────────────────────────────────────────┘
                          ↕ SQL
┌─────────────────────────────────────────────────────────┐
│                     Data Tier                            │
│                  PostgreSQL RDBMS                        │
│              (Tables + Filestore)                        │
└─────────────────────────────────────────────────────────┘
```

### 1.2 模块化架构

**核心概念**:
- 所有功能都打包为**模块**（Modules/Addons）
- 模块是 Python 包，包含 `__manifest__.py` 声明文件
- 模块可以添加新业务逻辑或扩展现有逻辑
- 模块目录通过 `--addons-path` 参数指定

**标准模块结构**:
```
my_module/
├── __init__.py              # 模块初始化
├── __manifest__.py          # 模块清单（必需）
├── models/                  # 业务对象（Python 类）
│   ├── __init__.py
│   ├── model1.py
│   └── model2.py
├── views/                   # UI 视图定义（XML）
│   ├── views.xml
│   └── menu.xml
├── security/                # 安全规则
│   └── ir.model.access.csv
├── data/                    # 数据文件（XML/CSV）
│   └── master_data.xml
├── demo/                    # 演示数据
│   └── demo_data.xml
├── controllers/             # Web 控制器
│   ├── __init__.py
│   └── controllers.py
├── static/                  # 静态资源
│   ├── src/
│   │   ├── css/
│   │   └── js/
│   └── description/
│       └── icon.png
└── tests/                   # 测试用例
    ├── __init__.py
    ├── test_model1.py
    └── test_model2.py
```

### 1.3 ORM 系统

**核心特性**:
- **自动映射**: Python 类字段自动映射到数据库列
- **关系字段**: Many2one, One2many, Many2many
- **计算字段**: `@api.depends` 装饰器定义
- **约束**: Python 约束和 SQL 约束
- **继承**: 原型继承（`_inherit`）和委托继承（`_inherits`）

**示例**:
```python
from odoo import models, fields, api

class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    name = fields.Char(required=True)
    email = fields.Char()
    is_company = fields.Boolean()
    country_id = fields.Many2one('res.country')
    
    @api.depends('name', 'email')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.name} ({record.email})"
```

### 1.4 数据库设计

**关键表**:
- `ir.model` - 模型元数据
- `ir.model.fields` - 字段元数据
- `ir.ui.view` - 视图定义
- `res.users` - 用户账户
- `ir.model.access` - 访问权限

**文件存储**:
- 数据库存储结构化数据
- 文件存储（filestore）存储附件、报告、会话数据
- 位置：`/var/lib/odoo/filestore/<database>/`

---

## 2. API 参考

### 2.1 API 协议对比

| 协议 | 状态 | 最佳用途 | 认证方式 |
|------|------|---------|---------|
| **XML-RPC** | ⚠️ 已废弃 (Odoo 22) | 遗留系统集成 | 用户名 + 密码/API Key |
| **JSON-RPC** | ⚠️ 已废弃 (Odoo 22) | JavaScript 应用 | Session Cookie / API Key |
| **JSON-2 API** | ✅ 推荐 (Odoo 19+) | 新集成 | Bearer Token (API Key) |

### 2.2 JSON-2 API（推荐）

**端点**: `POST /json/2/<model>/<method>`

**请求头**:
```
Host: mycompany.example.com
Authorization: bearer <api-key>
X-Odoo-Database: mycompany
Content-Type: application/json; charset=utf-8
User-Agent: mysoftware/1.0
```

**请求体**:
```json
{
  "context": {"lang": "en_US"},
  "domain": [["name", "ilike", "%deco%"]],
  "fields": ["name", "email"]
}
```

**Python 示例**:
```python
import requests

BASE_URL = "https://mycompany.example.com/json/2"
API_KEY = "your-api-key"
headers = {
    "Authorization": f"bearer {API_KEY}",
    "X-Odoo-Database": "mycompany",
    "User-Agent": "mysoftware/1.0",
}

# 搜索记录
response = requests.post(
    f"{BASE_URL}/res.partner/search",
    headers=headers,
    json={
        "context": {"lang": "en_US"},
        "domain": [("is_company", "=", True)],
    },
)
ids = response.json()

# 读取记录
response = requests.post(
    f"{BASE_URL}/res.partner/read",
    headers=headers,
    json={
        "ids": ids,
        "fields": ["name", "email"],
    },
)
records = response.json()
```

### 2.3 XML-RPC / JSON-RPC（遗留）

**端点**:
- XML-RPC: `/xmlrpc/2/common` (认证), `/xmlrpc/2/object` (数据)
- JSON-RPC: `/jsonrpc`

**Python 示例 (XML-RPC)**:
```python
import xmlrpc.client

url = "https://mycompany.odoo.com"
db = "mycompany"
username = "admin"
password = "api-key-or-password"

# 认证
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, username, password, {})

# 调用方法
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

# 搜索
ids = models.execute_kw(
    db, uid, password,
    'res.partner', 'search',
    [[['is_company', '=', True]]]
)

# 读取
records = models.execute_kw(
    db, uid, password,
    'res.partner', 'read',
    [ids],
    {'fields': ['name', 'email']}
)

# 创建
new_id = models.execute_kw(
    db, uid, password,
    'res.partner', 'create',
    [{'name': 'New Partner', 'email': 'test@example.com'}]
)

# 更新
models.execute_kw(
    db, uid, password,
    'res.partner', 'write',
    [[new_id], {'phone': '+1-555-0100'}]
)

# 删除
models.execute_kw(
    db, uid, password,
    'res.partner', 'unlink',
    [[new_id]]
)
```

### 2.4 常用 ORM 方法

| 方法 | 描述 | 示例 |
|------|------|------|
| `search(domain)` | 搜索记录，返回 ID 列表 | `[['is_company', '=', True]]` |
| `search_read(domain, fields)` | 搜索并读取，一步完成 | `[['active', '=', True]], ['name', 'email']` |
| `search_count(domain)` | 计数匹配记录 | `[['state', '=', 'sale']]` |
| `read(ids, fields)` | 读取指定字段 | `[1, 2, 3], ['name', 'country_id']` |
| `create(values)` | 创建记录 | `{'name': 'New', 'email': 'test@...'}` |
| `write(ids, values)` | 更新记录 | `[[1, 2], {'active': False}]` |
| `unlink(ids)` | 删除记录 | `[[1, 2, 3]]` |
| `fields_get()` | 获取字段元数据 | `[], ['string', 'type', 'help']` |

### 2.5 关系字段处理

**Many2one**:
```python
# 读取：返回 [id, display_name]
# [{'id': 42, 'country_id': [233, 'United States']}]

# 写入：传递 ID
{'country_id': 38}  # 38 = Canada
```

**One2many / Many2many 命令语法**:
```python
# 命令格式：(command, id, values)
order_lines = [
    (0, 0, {'product_id': 1, 'quantity': 5}),  # 创建新记录
    (1, 2, {'quantity': 10}),                   # 更新现有记录
    (2, 3, 0),                                  # 删除并移除链接
    (3, 4, 0),                                  # 仅移除链接
    (4, 5, 0),                                  # 链接现有记录
    (5, 0, 0),                                  # 移除所有链接
    (6, 0, [1, 2, 3]),                         # 替换所有链接
]
```

### 2.6 域过滤器（Domain Filters）

**操作符**:
| 操作符 | 描述 | 示例 |
|--------|------|------|
| `=` | 等于 | `('state', '=', 'sale')` |
| `!=` | 不等于 | `('state', '!=', 'cancel')` |
| `>`, `<`, `>=`, `<=` | 比较 | `('amount', '>', 1000)` |
| `in` | 在列表中 | `('state', 'in', ['sale', 'done'])` |
| `like` | 模式匹配（区分大小写） | `('name', 'like', 'Acme%')` |
| `ilike` | 模式匹配（不区分大小写） | `('email', 'ilike', '%@gmail.com')` |
| `child_of` | 层级关系 | `('category_id', 'child_of', 1)` |

**逻辑运算符**:
```python
# AND (默认)
[('is_company', '=', True), ('customer_rank', '>', 0)]

# OR (使用 '|')
['|', ('country_id.code', '=', 'US'), ('country_id.code', '=', 'CA')]

# 复杂逻辑
['|', '&', ('active', '=', True), ('vip', '=', True), ('premium', '=', True)]
```

---

## 3. 模块开发

### 3.1 模块清单（__manifest__.py）

```python
{
    'name': "My Module",
    'version': '1.0.0',
    'summary': "Brief description",
    'description': """
        Detailed description in reStructuredText
        ========================================
        - Feature 1
        - Feature 2
    """,
    'author': "Author Name",
    'website': "https://www.example.com",
    'license': 'LGPL-3',  # GPL-2, AGPL-3, OEEL-1, OPL-1, etc.
    'category': 'Sales/Sales',
    'depends': ['base', 'sale'],  # 必须包含 base
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/menu.xml',
        'data/data.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'external_dependencies': {
        'python': ['requests', 'pandas'],
        'bin': ['wkhtmltopdf'],
    },
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/css/style.css',
        ],
    },
}
```

### 3.2 开发工作流

**1. 环境准备**:
```bash
# 使用 Docker Compose（推荐）
git clone https://github.com/odoo/docker-compose
cd docker-compose
docker compose up -d

# 或使用官方镜像
docker run -v /path/to/addons:/mnt/extra-addons \
           -p 8069:8069 \
           --name odoo \
           -d odoo:19.0
```

**2. 创建模块**:
```bash
cd /path/to/custom-addons
mkdir -p my_module/{models,views,security,data,demo,tests,static/src}
touch my_module/__init__.py
touch my_module/__manifest__.py
```

**3. 启用开发者模式**:
- 方法 1: Settings → General Settings → Activate Developer Mode
- 方法 2: 在 URL 添加 `?debug=1`
- 方法 3: 在 URL 添加 `?debug=assets`（加载未压缩资源）

**4. 更新模块**:
```bash
# 通过 UI: Apps → Update Apps List → 升级模块
# 通过命令行:
docker exec -it odoo odoo-bin -u my_module -d mydb
```

### 3.3 调试方法

**VS Code + Docker 远程调试**:
```dockerfile
# Dockerfile
FROM odoo:19.0
RUN pip3 install debugpy
```

```yaml
# docker-compose.yml
services:
  odoo:
    command: >
      python3 -m debugpy --listen 0.0.0.0:8888
      /usr/bin/odoo-bin
    ports:
      - "8069:8069"
      - "8888:8888"  # 调试端口
```

**VS Code 配置** (`launch.json`):
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Odoo: Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 8888
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/mnt/extra-addons"
                }
            ]
        }
    ]
}
```

**日志调试**:
```python
import logging
_logger = logging.getLogger(__name__)

class MyModel(models.Model):
    _name = 'my.model'
    
    def my_method(self):
        _logger.info("Info message: %s", value)
        _logger.debug("Debug message")
        _logger.warning("Warning message")
        _logger.error("Error message")
```

### 3.4 测试框架

**测试结构**:
```
my_module/
└── tests/
    ├── __init__.py          # from . import test_my_model
    └── test_my_model.py     # 测试文件（必须以 test_ 开头）
```

**测试类**:
```python
from odoo.tests import TransactionCase, tagged, Form

class TestMyModel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 类级别的设置，运行一次
        cls.test_partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
        })
    
    def setUp(self):
        super().setUp()
        # 每个测试方法前运行
    
    def test_create_record(self):
        """测试创建记录"""
        record = self.env['my.model'].create({
            'name': 'Test',
            'partner_id': self.test_partner.id,
        })
        self.assertEqual(record.name, 'Test')
        self.assertTrue(record.exists())
    
    def test_action_confirm(self):
        """测试动作方法"""
        record = self.env['my.model'].create({...})
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
    
    @tagged('post_install', '-at_install')
    def test_integration(self):
        """集成测试（所有模块安装后运行）"""
        pass
    
    def test_with_form(self):
        """使用 Form 测试（模拟 UI 行为）"""
        with Form(self.env['my.model']) as f:
            f.name = 'Test'
            f.partner_id = self.test_partner
        record = f.save()
        self.assertEqual(record.name, 'Test')
```

**运行测试**:
```bash
# 运行特定测试文件
odoo-bin --test-file=my_module/tests/test_my_model.py -d testdb

# 运行模块所有测试
odoo-bin --test-enable --test-tags=/my_module -d testdb

# 运行带标签的测试
odoo-bin --test-enable --test-tags=post_install -d testdb

# Docker 中运行
docker exec -it odoo odoo-bin --test-enable -i my_module -d testdb
```

---

## 4. Docker 部署

### 4.1 开发环境配置

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  odoo:
    image: odoo:19.0
    container_name: odoo-dev
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./custom-addons:/mnt/extra-addons:ro
      - odoo-web-data:/var/lib/odoo
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    command: --dev=reload

  db:
    image: postgres:16
    container_name: odoo-db
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"  # 开发环境暴露数据库端口

volumes:
  odoo-web-data:
  postgres-data:
```

**odoo.conf** (开发):
```ini
[options]
admin_passwd = admin
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
dbfilter = ^%d$

addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons

log_level = debug
list_db = True

# 开发模式
dev = reload
```

### 4.2 生产环境配置

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  odoo:
    image: odoo:19.0
    container_name: odoo-prod
    restart: always
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "127.0.0.1:8069:8069"
    volumes:
      - ./custom-addons:/mnt/extra-addons:ro
      - odoo-web-data:/var/lib/odoo
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=${DB_PASSWORD}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  db:
    image: postgres:16
    container_name: odoo-db
    restart: always
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=postgres
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    container_name: odoo-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - odoo

volumes:
  odoo-web-data:
  postgres-data:
```

**odoo.conf** (生产):
```ini
[options]
admin_passwd = ${ADMIN_PASSWORD}
db_host = db
db_port = 5432
db_user = odoo
db_password = ${DB_PASSWORD}
dbfilter = ^%d$

addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons

log_level = warn
list_db = False

# 多工作进程 (2 * CPU 核心数 + 1)
workers = 9
max_cron_threads = 1

# 内存限制 (每工作进程)
limit_memory_soft = 2048
limit_memory_hard = 3072
limit_time_cpu = 60
limit_time_real = 120

# 安全
proxy_mode = True
```

### 4.3 备份策略

**数据库备份**:
```bash
docker exec odoo-db pg_dump -U odoo -Fc mydb > backup_$(date +%Y%m%d).dump
```

**文件存储备份**:
```bash
docker run --rm \
  -v odoo-knowledge-base_odoo-web-data:/source:ro \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/filestore_$(date +%Y%m%d).tar.gz -C /source .
```

**自动化备份脚本**:
```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/odoo"
DATE=$(date +%Y%m%d_%H%M%S)

# 数据库备份
docker exec odoo-db pg_dump -U odoo -Fc mydb > ${BACKUP_DIR}/db_${DATE}.dump

# 文件存储备份
docker run --rm \
  -v odoo-knowledge-base_odoo-web-data:/source:ro \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/filestore_${DATE}.tar.gz -C /source .

# 保留最近 7 天备份
find ${BACKUP_DIR} -name "*.dump" -mtime +7 -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +7 -delete
```

---

## 5. 最佳实践

### 5.1 安全

1. **API Key 管理**:
   - 使用专用集成用户（最小权限）
   - API Key 存储在环境变量中
   - 定期轮换（最多 3 个月）
   - 不在代码中硬编码

2. **数据库安全**:
   - 使用强密码
   - 限制数据库管理器访问 (`list_db = False`)
   - 定期备份
   - 启用 PostgreSQL SSL

3. **访问控制**:
   - 定义 `ir.model.access.csv`
   - 使用记录规则限制数据访问
   - 审计日志跟踪敏感操作

### 5.2 性能优化

1. **索引优化**:
   ```python
   class MyModel(models.Model):
       _name = 'my.model'
       _order = 'create_date desc'
       
       name = fields.Char(index=True)  # 添加索引
       date = fields.Date(index=True)
   ```

2. **批量操作**:
   ```python
   # ❌ 避免循环中的单独写入
   for record in records:
       record.write({'state': 'done'})
   
   # ✅ 批量写入
   records.write({'state': 'done'})
   ```

3. **搜索优化**:
   ```python
   # ❌ 避免读取所有字段
   records = self.env['my.model'].search([])
   
   # ✅ 指定需要的字段
   records = self.env['my.model'].search_read(
       [], ['name', 'state'], limit=100
   )
   ```

### 5.3 代码质量

1. **遵循 PEP 8**: 使用 `pylint-odoo` 检查
2. **编写测试**: 覆盖关键业务逻辑
3. **文档化**: 在模型和方法中添加 docstring
4. **版本控制**: 使用语义化版本

---

## 6. Skill 开发计划

基于调研结果，建议创建以下三个 Skill：

### 6.1 odoo-architecture-skill

**目标**: 帮助开发者理解 Odoo 技术架构

**功能**:
- 解释三层架构
- 模块结构查询
- ORM 概念说明
- 数据库设计指导

**触发器**:
- "Odoo 架构"
- "模块结构"
- "ORM 是什么"
- "Odoo 数据库设计"

### 6.2 odoo-api-skill

**目标**: 提供 Odoo API 集成指导

**功能**:
- API 协议选择建议
- 认证流程指导
- CRUD 操作示例生成
- 域过滤器构建帮助
- 关系字段处理指导

**触发器**:
- "Odoo API"
- "XML-RPC 示例"
- "JSON-2 API"
- "如何连接 Odoo"
- "搜索客户"

### 6.3 odoo-development-skill

**目标**: 辅助 Odoo 模块开发和部署

**功能**:
- 模块脚手架生成
- 测试代码示例
- Docker 配置生成
- 调试方法指导
- 最佳实践建议

**触发器**:
- "创建 Odoo 模块"
- "Odoo 测试"
- "Docker 部署 Odoo"
- "调试 Odoo"

---

## 7. 资源链接

### 官方文档
- [Odoo 19 开发者文档](https://www.odoo.com/documentation/19.0/developer/)
- [架构概述](https://www.odoo.com/documentation/19.0/developer/tutorials/server_framework_101/01_architecture.html)
- [外部 API 参考](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html)
- [模块清单参考](https://www.odoo.com/documentation/19.0/developer/reference/backend/module.html)
- [测试框架](https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html)

### 社区资源
- [Odoo Docker Compose 示例](https://github.com/minhng92/odoo-17-docker-compose)
- [OCA (Odoo Community Association)](https://github.com/OCA)
- [Odoo 官方 Docker 镜像](https://hub.docker.com/_/odoo/)

### 工具
- [OEC.sh Docker Compose 生成器](https://oec.sh/tools/docker-compose-generator)
- [pylint-odoo](https://github.com/OCA/pylint-odoo)

---

## 附录 A: 快速参考卡片

### API 端点
```
JSON-2 API:  POST /json/2/<model>/<method>
XML-RPC:     /xmlrpc/2/common (认证), /xmlrpc/2/object (数据)
JSON-RPC:    /jsonrpc
健康检查：   /web/health
版本信息：   /web/version
```

### 认证方式
```python
# JSON-2 API (推荐)
headers = {"Authorization": "bearer <api-key>"}

# XML-RPC
common.authenticate(db, username, password, {})

# JSON-RPC Session
POST /web/session/authenticate
```

### 常用命令
```bash
# 开发模式启动
odoo-bin --dev=reload

# 更新模块
odoo-bin -u my_module -d mydb

# 运行测试
odoo-bin --test-enable --test-tags=/my_module

# Docker 日志
docker logs -f odoo

# 进入容器
docker exec -it odoo bash
```

---

**报告完成日期**: 2026-04-12  
**下次更新**: Odoo 20 发布时
