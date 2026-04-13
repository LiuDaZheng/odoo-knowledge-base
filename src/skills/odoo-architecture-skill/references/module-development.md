# Odoo 模块开发指南

## 开发环境设置

### 安装依赖

```bash
# Python 依赖
pip3 install -r requirements.txt

# 开发工具
pip3 install pylint-odoo black flake8
```

### 配置文件

```ini
# ~/.odoorc
[options]
addons_path = ~/odoo/addons,~/odoo-custom
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
data_dir = ~/.local/share/Odoo
```

### 启动开发模式

```bash
# 方式 1: URL 参数
http://localhost:8069?debug=1

# 方式 2: 命令行
odoo-bin --dev=all

# 方式 3: 配置文件
[options]
dev = all
```

---

## 创建模块

### 步骤 1: 创建目录结构

```bash
mkdir -p my_module/{models,controllers,views,security,data,static}
```

### 步骤 2: 创建 __init__.py

```python
# __init__.py
from . import models
from . import controllers
```

```python
# models/__init__.py
from . import sale_order
from . import product
```

### 步骤 3: 创建 __manifest__.py

```python
{
    'name': 'My Module',
    'version': '17.0.1.0.0',
    'depends': ['base', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
}
```

---

## 模型开发

### 创建模型

```python
# models/sale_order.py
from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    custom_field = fields.Char(string='Custom Field')
    custom_date = fields.Date(string='Custom Date')
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        # 当客户变更时
        if self.partner_id:
            self.custom_field = self.partner_id.name
```

### 添加计算字段

```python
custom_total = fields.Monetary(
    string='Custom Total',
    compute='_compute_custom_total',
    store=True
)

@api.depends('order_line.price_total', 'custom_field')
def _compute_custom_total(self):
    for order in self:
        base_total = sum(line.price_total for line in order.order_line)
        order.custom_total = base_total * 1.1 if order.custom_field else base_total
```

### 添加约束

```python
from odoo.exceptions import ValidationError

@api.constrains('custom_date')
def _check_custom_date(self):
    for record in self:
        if record.custom_date and record.custom_date < fields.Date.today():
            raise ValidationError('Date cannot be in the past')
```

---

## 视图开发

### 扩展现有视图

```xml
<!-- views/sale_order_views.xml -->
<odoo>
    <record id="view_order_form_inherit" model="ir.ui.view">
        <field name="name">sale.order.form.inherit</field>
        <field name="model">sale.order</field>
        <field name="inherit_id" ref="sale.view_order_form"/>
        <field name="arch" type="xml">
            
            <!-- 在 partner_id 后添加字段 -->
            <xpath expr="//field[@name='partner_id']" position="after">
                <field name="custom_field"/>
                <field name="custom_date"/>
            </xpath>
            
            <!-- 在 notebook 中添加页面 -->
            <xpath expr="//notebook" position="inside">
                <page string="Custom Info">
                    <group>
                        <field name="custom_total"/>
                    </group>
                </page>
            </xpath>
            
        </field>
    </record>
</odoo>
```

### 创建新视图

```xml
<record id="view_custom_tree" model="ir.ui.view">
    <field name="name">sale.order.tree.custom</field>
    <field name="model">sale.order</field>
    <field name="arch" type="xml">
        <tree string="Sales Orders">
            <field name="name"/>
            <field name="partner_id"/>
            <field name="date_order"/>
            <field name="amount_total" widget="monetary"/>
            <field name="state" widget="badge" 
                   decoration-info="state == 'draft'"
                   decoration-success="state == 'sale'"/>
        </tree>
    </field>
</record>
```

---

## 菜单和动作

### 创建菜单

```xml
<!-- views/menus.xml -->
<odoo>
    <!-- 根菜单 -->
    <menuitem id="menu_custom_root"
              name="Custom Sales"
              sequence="10"/>
    
    <!-- 子菜单 -->
    <menuitem id="menu_custom_orders"
              name="Orders"
              parent="menu_custom_root"
              sequence="10"/>
    
    <!-- 关联动作 -->
    <menuitem id="menu_custom_orders_all"
              name="All Orders"
              parent="menu_custom_orders"
              action="action_custom_orders"
              sequence="10"/>
</odoo>
```

### 创建窗口动作

```xml
<record id="action_custom_orders" model="ir.actions.act_window">
    <field name="name">Sales Orders</field>
    <field name="res_model">sale.order</field>
    <field name="view_mode">tree,form</field>
    <field name="domain">[('state', 'in', ['draft', 'sent'])]</field>
    <field name="context">{'search_default_draft': 1}</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Create your first order!
        </p>
    </field>
</record>
```

---

## 安全配置

### 访问控制列表

```csv
# security/ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sale_order_user,sale.order.user,model_sale_order,base.group_user,1,1,1,0
access_sale_order_manager,sale.order.manager,model_sale_order,sales_team.group_sale_manager,1,1,1,1
```

### 记录规则

```xml
<!-- security/security_rules.xml -->
<odoo>
    <record id="sale_order_user_rule" model="ir.rule">
        <field name="name">User: see only own orders</field>
        <field name="model_id" ref="model_sale_order"/>
        <field name="domain_force">[('user_id','=',user.id)]</field>
        <field name="groups" eval="[(4, ref('base.group_user'))]"/>
    </record>
    
    <record id="sale_order_manager_rule" model="ir.rule">
        <field name="name">Manager: see all orders</field>
        <field name="model_id" ref="model_sale_order"/>
        <field name="domain_force">[(1,'=',1)]</field>
        <field name="groups" eval="[(4, ref('sales_team.group_sale_manager'))]"/>
    </record>
</odoo>
```

---

## 控制器开发

### HTTP 路由

```python
# controllers/main.py
from odoo import http
from odoo.http import request

class SaleController(http.Controller):
    
    @http.route('/custom/sales/orders', type='json', auth='user')
    def list_orders(self, **kwargs):
        """获取订单列表"""
        domain = []
        if kwargs.get('state'):
            domain.append(('state', '=', kwargs['state']))
        
        orders = request.env['sale.order'].search(domain, limit=100)
        return orders.read(['name', 'partner_id', 'amount_total', 'state'])
    
    @http.route('/custom/sales/order/<int:order_id>', type='json', auth='user')
    def get_order(self, order_id):
        """获取订单详情"""
        order = request.env['sale.order'].browse(order_id)
        if not order.exists():
            return {'error': 'Order not found'}
        return order.read()[0]
    
    @http.route('/custom/sales/create', type='json', auth='user')
    def create_order(self, **kwargs):
        """创建订单"""
        try:
            order = request.env['sale.order'].create({
                'partner_id': kwargs.get('partner_id'),
                'order_line': kwargs.get('lines', []),
            })
            return {'id': order.id, 'name': order.name}
        except Exception as e:
            return {'error': str(e)}
```

---

## 数据文件

### 演示数据

```xml
<!-- data/demo_data.xml -->
<odoo>
    <record id="demo_order_1" model="sale.order">
        <field name="name">SO-DEMO-001</field>
        <field name="partner_id" ref="base.res_partner_1"/>
        <field name="state">draft</field>
    </record>
    
    <record id="demo_order_line_1" model="sale.order.line">
        <field name="order_id" ref="demo_order_1"/>
        <field name="product_id" ref="product.product_product_7"/>
        <field name="product_uom_qty">5</field>
        <field name="price_unit">100.00</field>
    </record>
</odoo>
```

### 邮件模板

```xml
<!-- data/mail_data.xml -->
<record id="mail_template_sale_confirmation" model="mail.template">
    <field name="name">Sales Order: Confirmation</field>
    <field name="model_id" ref="model_sale_order"/>
    <field name="subject">Order {{ object.name }} confirmed</field>
    <field name="body_html" type="html">
        <p>Dear {{ object.partner_id.name }},</p>
        <p>Your order {{ object.name }} has been confirmed.</p>
        <p>Thank you for your business!</p>
    </field>
</record>
```

---

## 测试

### 单元测试

```python
# tests/test_sale.py
from odoo.tests import common

class TestSaleOrder(common.TransactionCase):
    
    def setUp(self):
        super().setUp()
        self.partner = self.env.ref('base.res_partner_1')
        self.product = self.env.ref('product.product_product_7')
    
    def test_create_order(self):
        """测试创建订单"""
        order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_uom_qty': 1,
                'price_unit': 100.0,
            })],
        })
        self.assertEqual(order.state, 'draft')
        self.assertEqual(order.amount_total, 100.0)
    
    def test_confirm_order(self):
        """测试确认订单"""
        order = self.env['sale.order'].create({...})
        order.action_confirm()
        self.assertEqual(order.state, 'sale')
```

### 运行测试

```bash
# 运行所有测试
odoo-bin --test-enable --test-tags /my_module

# 运行特定测试类
odoo-bin --test-enable --test-tags /my_module:TestSaleOrder

# 运行特定测试方法
odoo-bin --test-enable --test-tags /my_module:TestSaleOrder.test_create_order
```

---

## 调试技巧

### 日志记录

```python
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def action_confirm(self):
        _logger.info('Confirming order: %s', self.name)
        _logger.debug('Order details: %s', self.read())
        
        try:
            # 业务逻辑
            pass
        except Exception as e:
            _logger.error('Error confirming order: %s', e)
            raise
```

### 断点调试

```python
# 使用 pdb
import pdb

def my_method(self):
    pdb.set_trace()  # 断点
    # 代码执行到这里会暂停
```

### 查看 SQL

```python
# 启用 SQL 日志
# 启动时添加：--log-level=debug_sql

# 或手动执行
self.env.cr.execute("SELECT * FROM sale_order WHERE id = %s", (1,))
print(self.env.cr.mogrify("SELECT * FROM sale_order WHERE id = %s", (1,)))
```

---

## 性能优化

### 避免 N+1 查询

```python
# ❌ 不推荐
for order in orders:
    print(order.partner_id.name)  # 每次访问都查询

# ✅ 推荐
orders.read(['partner_id'])  # 预加载
for order in orders:
    print(order.partner_id.name)  # 使用缓存
```

### 批量操作

```python
# ✅ 推荐：批量创建
self.env['sale.order'].create(vals_list)

# ✅ 推荐：批量写入
records.write({'state': 'done'})
```

---

## 发布前检查

- [ ] 通过 pylint-odoo 检查
- [ ] 测试用例覆盖核心功能
- [ ] 文档完整
- [ ] 无硬编码值
- [ ] 支持多语言
- [ ] 安全配置正确
- [ ] 性能测试通过

---

*参考：Odoo 官方开发文档*
