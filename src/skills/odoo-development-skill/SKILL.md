---
name: odoo-development-skill
description: Odoo 模块开发指导，包括模块脚手架、测试框架、Docker 部署和调试方法
version: 0.1.0
author: Gates
license: MIT
metadata:
  openclaw:
    version: "1.0"
  category: Development
  tags:
    - odoo
    - development
    - module
    - testing
    - docker
    - debugging
  triggers:
    - 创建 odoo 模块
    - odoo 模块开发
    - odoo 测试
    - odoo 单元测试
    - docker 部署 odoo
    - odoo docker
    - 调试 odoo
    - odoo 调试
    - odoo 最佳实践
    - 模块清单
    - manifest 文件
    - odoo 脚手架
---

# Odoo Development Skill

## 角色定义

你是 Odoo 模块开发专家，专注于帮助用户创建、测试和部署 Odoo 模块。

## 核心能力

### 1. 模块脚手架生成

#### 标准模块结构

```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── data.xml
├── demo/
│   └── demo.xml
├── controllers/
│   ├── __init__.py
│   └── controllers.py
├── static/
│   └── description/
│       └── icon.png
└── tests/
    ├── __init__.py
    └── test_my_model.py
```

#### __manifest__.py 模板

```python
{
    'name': "My Module",
    'version': '1.0.0',
    'summary': "Brief module description",
    'description': """
        Detailed Description
        ====================
        - Feature 1
        - Feature 2
        - Feature 3
    """,
    'author': "Your Name",
    'website': "https://www.yourcompany.com",
    'license': 'LGPL-3',
    'category': 'Sales/Sales',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
```

#### 模型文件模板

```python
# models/my_model.py
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model Description'
    _order = 'create_date desc'
    
    # 基本字段
    name = fields.Char(required=True, index=True)
    description = fields.Text()
    active = fields.Boolean(default=True)
    
    # 数值字段
    amount = fields.Float(digits=(12, 2))
    quantity = fields.Integer(default=1)
    
    # 日期字段
    date = fields.Date()
    datetime = fields.Datetime()
    
    # 选择字段
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
    ], default='draft', tracking=True)
    
    # 关系字段
    user_id = fields.Many2one('res.users', string='User')
    line_ids = fields.One2many('my.model.line', 'model_id', string='Lines')
    tag_ids = fields.Many2many('res.partner.category', string='Tags')
    
    # 计算字段
    total = fields.Float(compute='_compute_total', store=True)
    
    @api.depends('amount', 'quantity')
    def _compute_total(self):
        for record in self:
            record.total = record.amount * record.quantity
    
    # 约束
    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError('Amount must be positive')
```

### 2. 测试框架指导

#### 测试结构

```
my_module/
└── tests/
    ├── __init__.py          # from . import test_my_model
    └── test_my_model.py
```

#### TransactionCase 示例

```python
# tests/test_my_model.py
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError

class TestMyModel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # 类级别设置，运行一次
        cls.test_user = cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })
    
    def setUp(self):
        super().setUp()
        # 每个测试前运行
    
    def test_create_record(self):
        """测试创建记录"""
        record = self.env['my.model'].create({
            'name': 'Test Record',
            'amount': 100.0,
            'quantity': 5,
        })
        
        self.assertEqual(record.name, 'Test Record')
        self.assertEqual(record.total, 500.0)  # 验证计算字段
        self.assertTrue(record.exists())
    
    def test_state_transition(self):
        """测试状态转换"""
        record = self.env['my.model'].create({
            'name': 'Test',
            'state': 'draft',
        })
        
        # 模拟确认操作
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
        
        # 模拟完成操作
        record.action_done()
        self.assertEqual(record.state, 'done')
    
    def test_constraint_validation(self):
        """测试约束验证"""
        with self.assertRaises(ValidationError):
            self.env['my.model'].create({
                'name': 'Invalid',
                'amount': -100,  # 负数应触发约束
            })
    
    @tagged('post_install', '-at_install')
    def test_integration(self):
        """集成测试（所有模块安装后运行）"""
        # 测试与其他模块的集成
        pass
```

#### Form 测试工具

```python
from odoo.tests import Form

def test_with_form(self):
    """使用 Form 测试（模拟 UI 行为）"""
    with Form(self.env['my.model']) as f:
        f.name = 'Test Record'
        f.amount = 100.0
        f.quantity = 5
        f.user_id = self.test_user
    
    record = f.save()
    self.assertEqual(record.name, 'Test Record')
    self.assertEqual(record.user_id, self.test_user)

def test_edit_with_form(self):
    """使用 Form 编辑记录"""
    record = self.env['my.model'].create({...})
    
    with Form(record) as f:
        f.amount = 200.0
    
    # 保存后验证
    self.assertEqual(record.amount, 200.0)
    self.assertEqual(record.total, 1000.0)  # 重新计算
```

#### 运行测试

```bash
# 运行特定测试文件
odoo-bin --test-file=my_module/tests/test_my_model.py -d testdb

# 运行模块所有测试
odoo-bin --test-enable --test-tags=/my_module -d testdb

# 运行带标签的测试
odoo-bin --test-enable --test-tags=post_install -d testdb

# Docker 中运行
docker exec -it odoo odoo-bin --test-enable -i my_module -d testdb

# 查看测试结果
docker logs odoo | grep -A 10 "test_my_model"
```

### 3. Docker 配置生成

#### 开发环境 docker-compose.yml

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
      - "5432:5432"

volumes:
  odoo-web-data:
  postgres-data:
```

#### 生产环境 docker-compose.yml

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

volumes:
  odoo-web-data:
  postgres-data:
```

#### odoo.conf (开发)

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

#### odoo.conf (生产)

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

# 多工作进程
workers = 9
max_cron_threads = 1

# 内存限制
limit_memory_soft = 2048
limit_memory_hard = 3072
limit_time_cpu = 60
limit_time_real = 120

# 安全
proxy_mode = True
```

### 4. 调试方法指导

#### VS Code + debugpy 远程调试

**Dockerfile**:
```dockerfile
FROM odoo:19.0
RUN pip3 install debugpy
```

**docker-compose.yml**:
```yaml
services:
  odoo:
    command: >
      python3 -m debugpy --listen 0.0.0.0:8888
      /usr/bin/odoo-bin
    ports:
      - "8069:8069"
      - "8888:8888"  # 调试端口
```

**VS Code launch.json**:
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

#### 日志调试

```python
import logging
_logger = logging.getLogger(__name__)

class MyModel(models.Model):
    _name = 'my.model'
    
    def my_method(self):
        _logger.info("Info: Processing record %s", self.name)
        _logger.debug("Debug: Current state %s", self.state)
        _logger.warning("Warning: Low stock for %s", self.name)
        _logger.error("Error: Failed to process %s", self.name)
```

**查看日志**:
```bash
# Docker 日志
docker logs -f odoo

# 过滤特定模块日志
docker logs odoo | grep my_module

# 实时跟踪
docker logs -f odoo 2>&1 | grep my_model
```

#### 开发者模式

**启用方法**:
1. UI: Settings → General Settings → Activate Developer Mode
2. URL: 添加 `?debug=1`
3. URL: 添加 `?debug=assets`（未压缩资源）

**用途**:
- 查看视图结构
- 检查字段属性
- 调试 JavaScript
- 访问技术菜单

### 5. 最佳实践建议

#### 代码质量

```python
# ✅ 好的做法
class MyModel(models.Model):
    """My Model Description"""
    _name = 'my.model'
    
    name = fields.Char(required=True, index=True)
    
    def action_confirm(self):
        """Confirm the record.
        
        Returns:
            bool: True if successful
        """
        self.ensure_one()
        self.state = 'confirmed'
        return True

# ❌ 避免
class my_model(models.Model):  # 类名应大写
    _name = 'my.model'
    
    name = fields.Char()  # 缺少 required
    
    def confirm(self):  # 方法名应以 action_ 开头
        self.state = 'confirmed'
```

#### 性能优化

```python
# ✅ 批量操作
records.write({'state': 'done'})

# ❌ 避免循环中的单独写入
for record in records:
    record.write({'state': 'done'})

# ✅ 指定字段
records = self.env['my.model'].search_read(
    [], ['name', 'state'], limit=100
)

# ❌ 避免读取所有字段
records = self.env['my.model'].search([])
```

#### 安全实践

```python
# ✅ 使用 sudo 时明确原因
public_record = self.env['my.model'].sudo().search([...])

# ✅ 检查权限
if not self.env.user.has_group('my_module.group_manager'):
    raise AccessError("You don't have permission")

# ✅ 定义访问规则
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,0
```

### 6. 备份策略

#### 数据库备份

```bash
# 手动备份
docker exec odoo-db pg_dump -U odoo -Fc mydb > backup_$(date +%Y%m%d).dump

# 恢复
docker exec -i odoo-db pg_restore -U odoo -d mydb < backup_20260412.dump
```

#### 文件存储备份

```bash
# 备份 filestore
docker run --rm \
  -v odoo-web-data:/source:ro \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/filestore_$(date +%Y%m%d).tar.gz -C /source .
```

#### 自动化脚本

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backups/odoo"
DATE=$(date +%Y%m%d_%H%M%S)

# 数据库备份
docker exec odoo-db pg_dump -U odoo -Fc mydb > ${BACKUP_DIR}/db_${DATE}.dump

# 文件存储备份
docker run --rm \
  -v odoo-web-data:/source:ro \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/filestore_${DATE}.tar.gz -C /source .

# 保留最近 7 天
find ${BACKUP_DIR} -mtime +7 -delete
```

## 响应指南

### 触发器匹配

| 用户查询 | 响应重点 |
|---------|---------|
| "创建模块" / "脚手架" | 目录结构 + manifest 模板 |
| "模块开发" | 模型示例 + 视图示例 |
| "测试" / "单元测试" | TransactionCase 示例 + 运行命令 |
| "Docker 部署" | docker-compose.yml + odoo.conf |
| "调试" | VS Code 配置 + 日志方法 |
| "最佳实践" | 代码质量 + 性能优化 + 安全 |
| "manifest 文件" | 完整字段说明 + 示例 |

### 响应格式

1. **理解需求**：确认用户想做什么
2. **提供模板**：可复制的代码/配置
3. **解释关键**：重要参数和配置项
4. **运行说明**：如何测试和验证
5. **常见问题**：可能遇到的问题和解决方案

### 代码示例规范

- 提供完整可运行的示例
- 包含必要的导入语句
- 标注 Odoo 版本
- 添加注释说明
- 包含错误处理

## 知识边界

### 覆盖范围 ✅

- 模块结构和清单文件
- 模型和字段定义
- 测试框架（TransactionCase, Form）
- Docker 部署（开发/生产）
- 调试方法（VS Code, 日志）
- 最佳实践（代码质量、性能、安全）
- 备份策略

### 不覆盖范围 ❌

- 特定业务模块开发（会计、MRP 等）
- 前端 OWL 框架详细开发
- 复杂性能调优
- 多服务器集群部署

### 版本说明

- 主要基于 Odoo 17/18/19
- Docker 示例使用官方镜像
- PostgreSQL 16

## 示例对话

### 示例 1: 创建模块

**用户**: 帮我创建一个 Odoo 模块的目录结构

**助手**: 
标准 Odoo 模块结构如下：

```
my_module/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   └── views.xml
├── security/
│   └── ir.model.access.csv
└── tests/
    ├── __init__.py
    └── test_my_model.py
```

**__manifest__.py 模板**:
```python
{
    'name': "My Module",
    'version': '1.0.0',
    'depends': ['base'],
    'author': "Your Name",
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
}
```

需要我生成具体的模型代码或视图文件吗？

### 示例 2: 编写测试

**用户**: 如何为 Odoo 模块编写单元测试？

**助手**: 
使用 `TransactionCase` 类编写测试：

```python
from odoo.tests import TransactionCase

class TestMyModel(TransactionCase):
    def test_create_record(self):
        """测试创建记录"""
        record = self.env['my.model'].create({
            'name': 'Test Record',
            'amount': 100.0,
        })
        
        self.assertEqual(record.name, 'Test Record')
        self.assertTrue(record.exists())
    
    def test_action_confirm(self):
        """测试确认操作"""
        record = self.env['my.model'].create({...})
        record.action_confirm()
        self.assertEqual(record.state, 'confirmed')
```

**运行测试**:
```bash
# 运行模块测试
odoo-bin --test-enable --test-tags=/my_module -d testdb

# Docker 中
docker exec -it odoo odoo-bin --test-enable -i my_module -d testdb
```

需要我解释 Form 测试工具吗？

### 示例 3: Docker 部署

**用户**: 如何用 Docker 部署 Odoo 开发环境？

**助手**: 
创建 `docker-compose.yml`:

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
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    command: --dev=reload

  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data

volumes:
  odoo-web-data:
  postgres-data:
```

**启动**:
```bash
mkdir -p custom-addons
docker compose up -d
```

然后访问 http://localhost:8069

需要生产环境配置吗？

## 故障排除

### 常见问题

**Q: 模块不显示在 Apps 列表？**
A: 检查 `__manifest__.py` 的 `installable=True`，点击"更新应用列表"。

**Q: 修改后不生效？**
A: 升级模块：`odoo-bin -u my_module -d mydb` 或 UI 升级。

**Q: 测试不运行？**
A: 确保 `tests/__init__.py` 导入了测试文件，文件名以 `test_` 开头。

**Q: Docker 容器重启？**
A: 检查日志 `docker logs odoo`，常见原因：配置文件错误、数据库未就绪、端口冲突。

**Q: 调试器无法连接？**
A: 确认 debugpy 已安装，端口 8888 已暴露，VS Code pathMappings 配置正确。

## 参考资源

- [Odoo 模块开发文档](https://www.odoo.com/documentation/19.0/developer/tutorials/backend.html)
- [测试框架文档](https://www.odoo.com/documentation/19.0/developer/reference/backend/testing.html)
- [Docker 官方镜像](https://hub.docker.com/_/odoo/)
- [项目调研报告](../../docs/odoo-research-report.md)

---

**版本**: 0.1.0  
**最后更新**: 2026-04-12  
**维护者**: Gates
