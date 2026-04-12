# Odoo 模块化设计

## 模块概念

### 什么是模块

Odoo 模块是**功能单元**，包含：
- 数据模型定义
- 业务逻辑
- 用户界面
- 安全配置
- 数据文件

### 模块类型

| 类型 | 标识 | 说明 | 示例 |
|------|------|------|------|
| **App** | 📱 | 主要应用，带图标 | Sales, Inventory, CRM |
| **Technical** | 🔧 | 技术依赖模块 | base, web |
| **Extension** | ➕ | 扩展现有功能 | sale_discount |

---

## 模块目录结构

### 完整结构

```
my_module/
├── __init__.py                 # Python 包初始化
├── __manifest__.py             # 模块清单 (必需)
│
├── models/                     # 数据模型
│   ├── __init__.py
│   ├── sale_order.py           # 销售订单模型
│   └── product.py              # 产品模型
│
├── controllers/                # HTTP 控制器
│   ├── __init__.py
│   └── main.py                 # 路由处理
│
├── views/                      # XML 视图
│   ├── menus.xml               # 菜单定义
│   ├── sale_order_views.xml    # 销售订单视图
│   └── templates.xml           # QWeb 模板
│
├── security/                   # 安全配置
│   ├── ir.model.access.csv     # 访问控制列表
│   └── security_rules.xml      # 记录规则
│
├── data/                       # 数据文件
│   ├── demo_data.xml           # 演示数据
│   └── mail_data.xml           # 邮件模板
│
├── static/                     # 静态资源
│   ├── description/
│   │   ├── icon.png            # 模块图标 (54x54)
│   │   └── screenshot.png      # 截图
│   └── src/
│       ├── css/                # 样式文件
│       ├── js/                 # JavaScript
│       └── xml/                # QWeb 模板
│
├── wizard/                     # 向导 (临时对话框)
│   ├── __init__.py
│   └── wizard_view.xml
│
├── report/                     # 报表
│   ├── __init__.py
│   ├── sale_report.py          # 报表模型
│   └── report.xml              # 报表定义
│
├── tests/                      # 测试用例
│   └── test_sale.py
│
└── i18n/                       # 国际化
    ├── zh_CN.po                # 简体中文
    └── en_US.po                # 英文
```

---

## 模块清单 (__manifest__.py)

### 完整示例

```python
{
    # 基本信息
    'name': 'Custom Sales Module',
    'version': '17.0.1.0.0',
    'category': 'Sales/Sales',
    'summary': 'Custom sales functionality',
    'description': """
        Custom Sales Module
        ===================
        This module extends the sales functionality with:
        - Custom fields
        - Advanced reporting
        - Workflow automation
    """,
    
    # 作者信息
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'maintainer': 'Your Name',
    'contributors': ['Name1', 'Name2'],
    
    # 许可证
    'license': 'LGPL-3',
    
    # 依赖模块
    'depends': [
        'base',
        'sale',
        'stock',
    ],
    
    # 数据文件 (始终加载)
    'data': [
        # 安全配置 (必须在前)
        'security/ir.model.access.csv',
        'security/security_rules.xml',
        
        # 视图
        'views/menus.xml',
        'views/sale_order_views.xml',
        'views/templates.xml',
        
        # 数据
        'data/mail_data.xml',
        
        # 报表
        'report/report.xml',
    ],
    
    # 演示数据 (仅演示模式)
    'demo': [
        'data/demo_data.xml',
    ],
    
    # 静态资源 (前端)
    'assets': {
        'web.assets_backend': [
            'my_module/static/src/css/custom.css',
            'my_module/static/src/js/custom.js',
        ],
    },
    
    # 安装选项
    'installable': True,
    'application': True,      # 是否为 App
    'auto_install': False,    # 是否自动安装
    'post_init_hook': 'post_init',  # 安装后钩子
    'uninstall_hook': 'uninstall',   # 卸载钩子
}
```

### 版本命名规范

```
主版本。次版本。补丁版本。发布版本
   ↓      ↓      ↓      ↓
  17     0      1      0

17.0.1.0.0 = Odoo 17.0, 模块版本 1.0.0
```

### 许可证类型

| 许可证 | 说明 | 适用场景 |
|--------|------|----------|
| LGPL-3 | 开源，允许商业使用 | 社区模块 |
| OPL-1 | Odoo 专有许可证 | 企业模块 |
| MIT | 宽松开源 | 工具库 |

---

## 模块依赖管理

### 依赖声明

```python
'depends': [
    'base',         # 基础模块 (必须)
    'sale',         # 销售模块
    'stock',        # 库存模块
    'account',      # 会计模块
],
```

### 依赖解析顺序

```
安装顺序:
base → sale → stock → account → my_module
```

### 循环依赖检测

❌ **错误**: 循环依赖
```
Module A depends on Module B
Module B depends on Module A
```

✅ **正确**: 单向依赖
```
Module A depends on Module B
Module B depends on base
```

---

## 数据文件

### XML 数据文件

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- 菜单项 -->
    <menuitem id="menu_sales_root"
              name="Sales"
              sequence="10"/>
    
    <!-- 视图 -->
    <record id="view_sale_order_form" model="ir.ui.view">
        <field name="name">sale.order.form</field>
        <field name="model">sale.order</field>
        <field name="arch" type="xml">
            <form string="Sales Order">
                <field name="name"/>
                <field name="partner_id"/>
            </form>
        </field>
    </record>
    
    <!-- 服务器动作 -->
    <record id="action_sale_order" model="ir.actions.act_window">
        <field name="name">Sales Orders</field>
        <field name="res_model">sale.order</field>
        <field name="view_mode">tree,form</field>
    </record>
</odoo>
```

### CSV 数据文件

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sale_order_user,sale.order.user,model_sale_order,base.group_user,1,1,1,0
access_sale_order_manager,sale.order.manager,model_sale_order,sales_team.group_sale_manager,1,1,1,1
```

---

## 模块继承模式

### 1. 模型继承

```python
# 扩展现有模型
class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    custom_field = fields.Char(string='Custom Field')
```

### 2. 视图继承

```xml
<record id="view_order_form_inherit" model="ir.ui.view">
    <field name="name">sale.order.form.inherit</field>
    <field name="model">sale.order</field>
    <field name="inherit_id" ref="sale.view_order_form"/>
    <field name="arch" type="xml">
        <!-- 在指定位置后添加字段 -->
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="custom_field"/>
        </xpath>
        
        <!-- 替换整个字段 -->
        <xpath expr="//field[@name='amount_total']" position="replace">
            <field name="amount_total" widget="monetary"/>
        </xpath>
        
        <!-- 在末尾添加 -->
        <xpath expr="//form" position="inside">
            <group string="Custom Group">
                <field name="custom_field"/>
            </group>
        </xpath>
    </field>
</record>
```

### 3. 类继承 (Python)

```python
# 方式 1: 原型继承
class MyModel(ParentModel):
    _name = 'my.model'
    _inherit = 'parent.model'

# 方式 2: 混入
class MyMixin(models.AbstractModel):
    _name = 'my.mixin'
    _description = 'My Mixin'
    
    common_field = fields.Char()

class MyModel(models.Model):
    _name = 'my.model'
    _inherit = ['base', 'my.mixin']
```

---

## 模块开发最佳实践

### 代码组织

✅ **推荐**:
```
models/
├── __init__.py
├── sale_order.py
└── product.py

views/
├── menus.xml
├── sale_order_views.xml
└── product_views.xml
```

❌ **不推荐**:
```
# 所有代码在一个文件
my_module.py (2000+ 行)
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模型名 | 小写 + 点 | `sale.order` |
| 字段名 | 小写 + 下划线 | `order_date` |
| 类名 | 驼峰 | `SaleOrder` |
| 方法名 | 小写 + 下划线 | `action_confirm` |
| XML ID | 小写 + 下划线 | `view_sale_order_form` |

### 性能优化

```python
# ✅ 推荐：批量操作
records = self.env['sale.order'].search([('state', '=', 'draft')])
records.action_confirm()

# ❌ 不推荐：循环调用
for record in self.env['sale.order'].search([('state', '=', 'draft')]):
    record.action_confirm()

# ✅ 推荐：使用 read_group 聚合
result = self.env['sale.order'].read_group(
    domain=[],
    fields=['amount_total:sum'],
    groupby=['state']
)

# ❌ 不推荐：Python 中聚合
total = sum(order.amount_total for order in orders)
```

---

## 模块测试

### 测试类

```python
from odoo.tests import common

class TestSaleOrder(common.TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.product = self.env.ref('product.product_product_7')
    
    def test_create_order(self):
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
            })],
        })
        self.assertEqual(order.state, 'draft')
    
    def test_confirm_order(self):
        order = self.env['sale.order'].create({...})
        order.action_confirm()
        self.assertEqual(order.state, 'sale')
```

### 运行测试

```bash
# 运行模块测试
odoo-bin --test-enable --test-tags /my_module

# 运行特定测试
odoo-bin --test-enable --test-tags /my_module:TestSaleOrder.test_create_order
```

---

## 模块发布

### 发布前检查清单

- [ ] `__manifest__.py` 配置完整
- [ ] 所有文件有正确的许可证头
- [ ] 通过 pylint-odoo 检查
- [ ] 测试用例覆盖核心功能
- [ ] 文档完整（README）
- [ ] 无硬编码值
- [ ] 支持多语言（i18n）

### 发布到 Odoo Apps

1. 创建 [apps.odoo.com](https://apps.odoo.com) 账户
2. 上传模块 ZIP 包
3. 填写模块信息
4. 等待审核
5. 发布

---

*参考：Odoo 官方模块开发指南*
