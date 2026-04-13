# Odoo 测试框架参考

## 测试环境基础

Odoo 测试基于 Python `unittest2` + `odoo.tests.common` 模块。

### 测试类层次

```
odoo.tests.common.BaseCase          # 基础类
├── odoo.tests.TransactionCase      # 事务隔离，每个测试一个事务
├── odoo.tests.SavepointCase        # 使用数据库保存点
└── odoo.tests.HttpCase             # HTTP/UI 测试（含 browser_js）
```

### 测试标签

```python
from odoo.tests import tagged

# at_install: 安装时运行（默认）
# post_install: 安装所有模块后运行
# 组合使用：
@tagged('post_install', '-at_install')   # post_install 且排除 at_install
@tagged('slow', 'standard')              # 自定义标签
```

## 单元测试 TransactionCase

### 基础结构

```python
# tests/test_my_model.py
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError, AccessError

class TestMyModel(TransactionCase):
    """my.model 单元测试"""

    @classmethod
    def setUpClass(cls):
        """类级别设置，所有测试前运行一次"""
        super().setUpClass()
        # 创建测试用户
        cls.admin_user = cls.env.ref('base.user_admin')
        cls.test_user = cls.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user',
            'email': 'test@example.com',
        })
        # 创建测试记录
        cls.test_record = cls.env['my.model'].create({
            'name': 'Test Record',
            'amount': 100.0,
        })

    def setUp(self):
        """方法级别设置，每个测试前运行"""
        super().setUp()
        # 每个测试前的准备
        pass

    def tearDown(self):
        """每个测试后清理"""
        super().tearDown()
        pass

    # ==================== 测试用例 ====================

    def test_create_record(self):
        """测试记录创建"""
        record = self.env['my.model'].create({
            'name': 'New Record',
            'amount': 50.0,
            'quantity': 2,
        })
        self.assertEqual(record.name, 'New Record')
        self.assertEqual(record.total, 100.0)  # amount * quantity
        self.assertTrue(record.active)
        self.assertEqual(record.state, 'draft')

    def test_record_exists(self):
        """测试记录存在性"""
        self.assertTrue(self.test_record.exists())
        self.assertEqual(self.test_record.amount, 100.0)

    def test_search_records(self):
        """测试搜索"""
        records = self.env['my.model'].search([('amount', '>', 50)])
        self.assertIn(self.test_record, records)

    def test_write_record(self):
        """测试更新"""
        self.test_record.write({'amount': 200.0})
        self.assertEqual(self.test_record.amount, 200.0)
        self.assertEqual(self.test_record.total, 200.0)

    def test_unlink_record(self):
        """测试删除"""
        record_id = self.test_record.id
        self.test_record.unlink()
        self.assertFalse(self.test_record.exists())

    def test_state_transition(self):
        """测试状态流转"""
        self.assertEqual(self.test_record.state, 'draft')
        self.test_record.action_confirm()
        self.assertEqual(self.test_record.state, 'confirmed')
        self.test_record.action_done()
        self.assertEqual(self.test_record.state, 'done')

    def test_constraint_amount(self):
        """测试约束验证 - amount"""
        with self.assertRaises(ValidationError):
            self.env['my.model'].create({
                'name': 'Invalid',
                'amount': -100,  # 负数应触发约束
            })

    def test_compute_total(self):
        """测试计算字段"""
        record = self.env['my.model'].create({
            'name': 'Compute Test',
            'amount': 10.0,
            'quantity': 5,
        })
        self.assertEqual(record.total, 50.0)

    def test_sudo_access(self):
        """测试 sudo 权限提升"""
        public_record = self.env['my.model'].sudo(self.test_user).search([], limit=1)
        self.assertTrue(public_record)

    @tagged('post_install', '-at_install')
    def test_integration_with_sale(self):
        """集成测试 - 与销售模块集成"""
        # 只有 post_install 时才运行
        pass
```

## Form 测试工具

Form 模拟 UI 表单操作（适合复杂表单测试）：

```python
from odoo.tests import Form

def test_create_with_form(self):
    """使用 Form 创建记录"""
    with Form(self.env['my.model']) as f:
        f.name = 'Form Test'
        f.amount = 100.0
        f.quantity = 3

    record = f.save()
    self.assertEqual(record.name, 'Form Test')
    self.assertEqual(record.total, 300.0)

def test_edit_with_form(self):
    """使用 Form 编辑记录"""
    record = self.env['my.model'].create({
        'name': 'Original',
        'amount': 100.0,
    })

    with Form(record) as f:
        f.amount = 200.0
        # 尝试设置不可见字段会失败

    self.assertEqual(record.amount, 200.0)
    self.assertEqual(record.total, 200.0)

def test_required_fields_with_form(self):
    """测试必填字段验证"""
    with self.assertRaises(AssertionError):
        with Form(self.env['my.model']) as f:
            f.amount = 100.0
            # 缺少 name，应触发验证
```

## HTTP/UI 测试 HttpCase

```python
from odoo.tests import HttpCase, tagged

class TestUi(HttpCase):
    """UI 测试（需要浏览器）"""

    @tagged('post_install', '-at_install')
    def test_admin_login(self):
        """测试管理员登录"""
        self.browser_js(
            "/web",
            "odoo.__DEBUG__.services['web_tour.tour'].run('main']",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.main'].steps",
            timeout=60,
        )

    def test_web_page_loads(self):
        """测试页面加载"""
        response = self.url_open('/web')
        self.assertEqual(response.status_code, 200)
```

## Mock 测试

```python
from unittest.mock import patch

def test_with_mock(self):
    """使用 Mock 模拟外部服务"""
    with patch('odoo.addons.my_module.models.my_model.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'key': 'value'}

        # 调用依赖外部服务的代码
        result = self.env['my.model'].fetch_external_data()
        self.assertEqual(result, {'key': 'value'})
        mock_get.assert_called_once()
```

## 测试命令

### 基本命令

```bash
# 运行单个测试文件
odoo-bin --test-file=my_module/tests/test_my_model.py -d testdb

# 运行模块所有测试
odoo-bin --test-enable -i my_module -d testdb

# 按标签运行
odoo-bin --test-enable --test-tags=/my_module -d testdb
odoo-bin --test-enable --test-tags=post_install -d testdb
odoo-bin --test-enable --test-tags=standard -d testdb

# 运行所有测试（所有模块）
odoo-bin --test-enable -d testdb

# 详细输出
odoo-bin --test-enable --log-level=test -d testdb
```

### Docker 环境

```bash
# 运行模块测试
docker exec -it odoo odoo-bin --test-enable -i my_module -d testdb

# 运行特定测试文件
docker exec -it odoo odoo-bin --test-file=/mnt/extra-addons/my_module/tests/test_my_model.py -d testdb

# 查看测试输出
docker logs odoo 2>&1 | grep -E "(test_|ERROR|FAIL)"

# 实时跟踪
docker exec odoo tail -f /var/log/odoo/odoo.log | grep test
```

### pytest-odoo（推荐替代方案）

```bash
# 安装
pip install pytest-odoo

# 运行（自动处理 Odoo 环境）
pytest tests/test_my_model.py -m odoo

# 只运行 at_install 测试
pytest tests/ -m odoo --odoo-at-install

# 只运行 post_install 测试
pytest tests/ -m odoo --odoo-post-install

# 带覆盖率
pytest tests/ --cov=my_module --cov-report=html
```

## 测试覆盖率

### Python 覆盖率

```bash
# 使用 coverage.py
pip install coverage
coverage run --source=my_module -m odoo.testsrunner --test-enable -i my_module -d testdb
coverage report
coverage html
```

### Docker + 覆盖率

```dockerfile
FROM odoo:19.0
RUN pip3 install coverage
```

```bash
# 宿主机
docker exec -it odoo coverage run --source=my_module -m odoo.testsrunner --test-enable -i my_module -d testdb
docker exec -it odoo coverage report
docker cp odoo:/coverage html/
```

## 测试数据

### XML 测试数据

```xml
<!-- tests/data/test_data.xml -->
<odoo>
    <record id="test_partner_1" model="res.partner">
        <field name="name">Test Partner</field>
        <field name="email">test@example.com</field>
    </record>
</odoo>
```

```python
# tests/data/__init__.py
from . import test_data
```

### YAML 测试数据

```yaml
# tests/data/test_data.yml
- model: my.model
  records:
    - id: test_record_1
      values:
        name: YAML Test
        amount: 100.0
```

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 测试不运行 | 文件名不以 `test_` 开头 | 改为 `test_xxx.py` |
| 测试不运行 | `tests/__init__.py` 未导入 | 在 `__init__.py` 添加 `from . import test_xxx` |
| Savepoint 问题 | 嵌套事务 | 使用 `TransactionCase` 而非手动事务 |
| browser_js 超时 | 浏览器启动慢 | 增加 `timeout` 参数 |
| 孤立测试数据 | tearDown 未清理 | 使用 `TransactionCase` 自动回滚 |
| 外部依赖失败 | 网络服务不可用 | 使用 `@patch` Mock 外部调用 |

## 测试最佳实践

1. **每个测试独立**：不依赖其他测试的执行顺序
2. **setUpClass 复用**：类级别创建测试数据，减少重复
3. **命名规范**：`test_<method>_<scenario>`
4. **断言信息**：`self.assertEqual(actual, expected, "msg")`
5. **避免 sleep**：使用轮询替代固定等待
6. **测试覆盖核心路径**：优先测试业务逻辑关键路径
