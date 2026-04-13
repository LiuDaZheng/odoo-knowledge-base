# Odoo 模块脚手架参考

## 标准目录结构

```
my_module/
├── __init__.py              # 模块入口，必需
├── __manifest__.py          # 清单文件，必需
├── models/
│   ├── __init__.py
│   ├── my_model.py          # 模型定义
│   └── my_model_line.py     # 子模型
├── views/
│   ├── views.xml            # 视图定义
│   ├── my_model_form.xml
│   ├── my_model_tree.xml
│   └── my_model_action.xml
├── controllers/
│   ├── __init__.py
│   └── my_controller.py     # HTTP 控制器
├── security/
│   ├── ir.model.access.csv  # 访问控制列表
│   └── security.xml         # 记录规则
├── data/
│   ├── data.xml             # 数据文件
│   └── sequence.xml         # 序列
├── demo/
│   └── demo.xml             # 示例数据
├── reports/
│   ├── __init__.py
│   ├── report_my_model.py   # 报表
│   └── report_my_model.mako
├── wizards/
│   ├── __init__.py
│   └── my_wizard.py         # 向导
├── static/
│   ├── description/
│   │   ├── icon.png         # 模块图标
│   │   └── banner.png       # 模块横幅
│   └── src/
│       ├── js/
│       │   └── my_model.js  # 前端 JS
│       └── xml/
│           └── my_model.xml # QWeb 模板
└── tests/
    ├── __init__.py
    ├── test_my_model.py     # 单元测试
    └── test_my_model_ui.py  # UI 测试
```

## __manifest__.py 完整字段说明

```python
{
    # === 必需字段 ===
    'name': "My Module",           # 显示名称（必需）
    'version': '1.0.0',            # 版本号（必需）

    # === 基础信息 ===
    'summary': "Brief description", # 简短描述
    'description': """
        Detailed multi-line description.
        ==============================
        - Feature 1
        - Feature 2
    """,
    'author': "Your Name / Company",
    'website': "https://www.example.com",
    'license': 'LGPL-3',          # 常用: LGPL-3, GPL-3, AGPL-3, Proprietary
    'category': 'Sales/Sales',    # 分类：Sales, Accounting, Inventory等

    # === 依赖 ===
    'depends': ['base'],           # 模块依赖，base 几乎总是需要
    # 可选：
    'external_dependencies': {
        'python': ['requests'],
        'bin': ['curl'],
    },

    # === 数据文件（安装时加载）===
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/my_model_form.xml',
        'data/data.xml',
        'data/sequence.xml',
    ],

    # === 示例数据（演示模式下加载）===
    'demo': [
        'demo/demo.xml',
    ],

    # === 安装配置 ===
    'installable': True,           # 是否可安装，默认 True
    'application': True,           # 是否为应用（显示在 Apps），默认 False
    'auto_install': False,         # 自动安装（依赖满足时），默认 False
    'maintenance': False,          # 维护模式
    'uninstallable': False,        # 是否可卸载

    # === 加载顺序 ===
    'sequence': 100,               # 应用列表中的顺序
    'instance_count': 'new',        # new / limitless

    # === Web ===
    'qweb': [
        'static/src/xml/my_template.xml',
    ],

    # === 国别化 ===
    'country_ids': [],             # 适用国家
    'lang': 'en_US',               # 默认语言

    # === 图标 ===
    'images': [],                  # 预览图

    # === 贡献者 ===
    'contributors': [
        'Name <email@example.com>',
    ],
    'maintainer': 'Name <email@example.com>',
}
```

## 使用脚手架命令创建模块

```bash
# Odoo 17+
odoo-bin scaffold my_module /path/to/addons/

# 指定继承
odoo-bin scaffold -t minimal my_module /path/to/addons/

# Docker 环境
docker exec -it odoo odoo-bin scaffold my_module /mnt/extra-addons/
```

## 最小可运行模块示例

### 文件结构
```
hello_module/
├── __init__.py
└── __manifest__.py
```

### __init__.py
```python
from . import models
```

### models/__init__.py
```python
# 可以为空或从 . import my_model
```

### __manifest__.py
```python
{
    'name': "Hello Module",
    'version': '1.0.0',
    'summary': "A minimal working module",
    'author': "Developer",
    'license': 'LGPL-3',
    'depends': ['base'],
    'installable': True,
}
```

## 带模型的最小模块

```
hello_module/
├── __init__.py
├── __manifest__.py
└── models/
    ├── __init__.py
    └── models.py
```

### models/__init__.py
```python
from . import models
```

### models/models.py
```python
from odoo import models, fields

class HelloModel(models.Model):
    _name = 'hello.model'
    _description = 'Hello Model'

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
```

### security/ir.model.access.csv（最小 ACL）
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_hello_model_user,hello.model.user,model_hello_model,base.group_user,1,1,1,1
```

## 模型字段速查

| 字段类型 | 示例 | 说明 |
|---------|------|------|
| Char | `fields.Char(size=100)` | 字符串 |
| Text | `fields.Text()` | 多行文本 |
| Html | `fields.Html()` | 富文本 |
| Integer | `fields.Integer()` | 整数 |
| Float | `fields.Float(digits=(12,2))` | 浮点数 |
| Monetary | `fields.Monetary()` | 货币 |
| Boolean | `fields.Boolean(default=False)` | 布尔 |
| Date | `fields.Date()` | 日期 |
| Datetime | `fields.Datetime()` | 日期时间 |
| Binary | `fields.Binary()` | 二进制文件 |
| Selection | `fields.Selection([('a','A'),('b','B')])` | 枚举 |
| Many2one | `fields.Many2one('res.partner')` | 外键 |
| One2many | `fields.One2many('sale.order.line', 'order_id')` | 一对多 |
| Many2many | `fields.Many2many('res.partner.category')` | 多对多 |
| Image | `fields.Image(max_width=1920, max_height=1920)` | 图片 |
| Reference | `fields.Reference([('sale.order', 'Sale Order')])` | 跨模型引用 |

## 计算字段与约束

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class MyModel(models.Model):
    _name = 'my.model'

    amount = fields.Float()
    quantity = fields.Integer(default=1)
    total = fields.Float(compute='_compute_total', store=True, readonly=True)

    @api.depends('amount', 'quantity')
    def _compute_total(self):
        for record in self:
            record.total = record.amount * record.quantity

    @api.constrains('amount')
    def _check_amount(self):
        for record in self:
            if record.amount < 0:
                raise ValidationError('Amount must be positive!')
```

## 视图类型速查

| 视图类型 | 用途 | XML 根标签 |
|---------|------|-----------|
| form | 表单编辑 | `<form>` |
| tree | 列表/表格 | `<tree>` |
| kanban | 看板 | `<kanban>` |
| calendar | 日历 | `<calendar>` |
| gantt |甘特图 | `<gantt>` |
| graph | 图表 | `<graph>` |
| pivot | 数据透视 | `<pivot>` |
| search | 搜索面板 | `<search>` |
| qweb | QWeb 报表 | `<qweb>` |
