---
name: odoo-development-skill
description: Odoo 模块开发指导。Use when: (1) 创建 Odoo 模块, (2) 编写 Odoo 单元测试, (3) Docker 部署 Odoo, (4) 调试 Odoo 模块, (5) __manifest__.py 模块清单。
---

# Odoo 模块开发 Skill

## 快速导航

| 主题 | 参考文档 | 说明 |
|------|----------|------|
| 模块脚手架 | [references/scaffolding.md](references/scaffolding.md) | 目录结构、manifest 字段、模型字段 |
| 测试框架 | [references/testing.md](references/testing.md) | TransactionCase、Form、命令 |
| Docker 部署 | [references/docker.md](references/docker.md) | docker-compose、odoo.conf、环境变量 |
| 调试方法 | [references/debugging.md](references/debugging.md) | 日志、pdb、开发模式 |

## 开发环境

### 连接测试

```bash
# Odoo Web 健康检查
curl -f http://localhost:8069/web/health

# PostgreSQL
docker exec -it odoo-db psql -U odoo -d postgres -c "SELECT version();"
```

### 快速启动（Docker）

```bash
# 1. 创建目录
mkdir -p custom-addons && cd custom-addons

# 2. 启动 Odoo + PostgreSQL
docker compose up -d

# 3. 访问 http://localhost:8069，创建数据库，安装模块
```

## 模块创建流程

### 概述

脚手架 → 模型 → 视图 → 权限 → 测试 → 安装验证。详细说明见 `references/` 目录。

### 1. 创建目录结构

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

### 2. `__manifest__.py`（最小示例）

```python
{
    'name': "My Module",
    'version': '1.0.0',
    'author': "Your Name",
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': ['security/ir.model.access.csv', 'views/views.xml'],
    'installable': True,
}
```

### 3. 模型定义

```python
# models/my_model.py
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model'

    name = fields.Char(required=True, index=True)
    amount = fields.Float(digits=(12, 2))
    active = fields.Boolean(default=True)

    @api.depends('amount')
    def _compute_total(self):
        for record in self:
            record.total = record.amount * 2
```

### 4. 视图 XML

```xml
<!-- views/views.xml -->
<odoo>
    <record id="view_my_model_form" model="ir.ui.view">
        <field name="name">my.model.form</field>
        <field name="model">my.model</field>
        <field name="arch" type="xml">
            <form><sheet><group>
                <field name="name"/>
                <field name="amount"/>
            </group></sheet></form>
        </field>
    </record>

    <record id="action_my_model" model="ir.actions.act_window">
        <field name="name">My Models</field>
        <field name="res_model">my.model</field>
        <field name="view_mode">tree,form</field>
    </record>

    <menuitem id="menu_my_model" action="action_my_model"/>
</odoo>
```

### 5. 访问控制

```csv
<!-- security/ir.model.access.csv -->
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,1,1,1
```

### 6. 单元测试

```python
# tests/test_my_model.py
from odoo.tests import TransactionCase

class TestMyModel(TransactionCase):
    def test_create(self):
        record = self.env['my.model'].create({'name': 'Test', 'amount': 100.0})
        self.assertEqual(record.name, 'Test')
        self.assertTrue(record.exists())
```

### 7. 安装验证

```bash
# Docker 环境
docker exec odoo odoo-bin -i my_module -d testdb --stop-after-init
docker exec odoo odoo-bin --test-enable -i my_module -d testdb
```

## 部署概览

### 开发部署（Docker）

参考 `references/docker.md` 获取完整 `docker-compose.yml` 和 `odoo.conf` 配置。

```yaml
# 核心结构
services:
  odoo:
    image: odoo:19.0
    ports: ["8069:8069"]
    volumes:
      - ./custom-addons:/mnt/extra-addons:ro
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
```

### 生产部署要点

1. `odoo.conf` 中 `admin_passwd` / `db_password` 使用环境变量
2. Nginx/Caddy 反向代理 + HTTPS
3. `workers = 2*CPU + 1`，配置内存限制
4. 配置 `healthcheck` + 每日备份（参考 docker.md）
5. 日志级别设为 `warn`

### 常用运维命令

```bash
docker compose up -d          # 启动
docker compose down            # 停止
docker exec odoo odoo-bin -u my_module -d testdb   # 升级模块
docker logs -f odoo            # 查看日志
docker exec -it odoo-db psql -U odoo -d postgres   # 数据库
```

---

**版本**: 1.0.0 | **参考文档**: `references/` 目录 | **最后更新**: 2026-04-13 | **维护者**: Gates
