# Odoo 快速参考手册

## 功能清单

### Website Builder 功能

| 功能类别 | 具体功能 | 配置路径 |
|---------|---------|---------|
| **页面设计** | 拖拽式编辑器 | Website → Pages → Edit |
| | Building Blocks | 编辑器右侧面板 |
| | 响应式布局 | 自动适配 |
| **SEO** | Meta 标签优化 | Website → Site → Optimize SEO |
| | Sitemap | /sitemap.xml (自动生成) |
| | robots.txt | Website → Config → Settings → SEO |
| | 301 重定向 | Website → Pages → Properties |
| **主题** | 主题切换 | Website → Configuration → Themes |
| | 自定义 CSS/SCSS | 主题模块 static/src/scss/ |
| | 自定义 JavaScript | 主题模块 static/src/js/ |
| **表单** | 联系表单 | Website → Contact Us |
| | 表单字段配置 | 编辑器 → 表单 → 配置 |
| | CRM 集成 | Action → Create an Opportunity |
| **菜单** | 导航菜单 | Website → Configuration → Menus |
| | 页脚菜单 | Website → Edit → Footer |

### eCommerce 功能

| 功能类别 | 具体功能 | 配置路径 |
|---------|---------|---------|
| **产品管理** | 产品创建 | Website → Shop → New |
| | 产品变体 | Website → Config → Settings → Product Variants |
| | 产品分类 | Website → Shop → Categories |
| | 批量导入 | Website → Products → ⚙️ → Import |
| **购物车** | 加购行为 | Website → Config → Settings → Shop - Checkout |
| | Buy Now 按钮 | 同上 → Buy Now |
| | Wishlist | 同上 → Wishlist |
| **结账** | 结账流程配置 | Website → Config → Settings → Shop - Checkout |
| | 条款确认 | Website → Config → Settings → Accept Terms |
| | 新闻通讯 | 同上 → Newsletter |
| **支付** | 支付提供商 | Website → Configuration → Payment Providers |
| | PayPal | 同上 → Activate PayPal |
| | 电子钱包/礼品卡 | Website → Config → Settings → Shop - Products |
| **配送** | 配送方式 | Inventory → Configuration → Delivery Methods |
| | 运费计算 | 同上 → Create → Based on Rules |
| | 第三方物流 | 同上 → Third-party Carrier |
| | 店内取货 | Website → Config → Settings → Click & Collect |
| **订单** | 订单管理 | Sales → Orders → Sales Orders |
| | 订单跟踪 | Inventory → Delivery Orders |
| | 客户门户 | Website → Configuration → Customer Accounts |

---

## API 参考卡片

### 连接示例 (Python)

```python
import xmlrpc.client

# 配置
url = 'https://your-company.odoo.com'
db = 'your_database'
username = 'your_email@example.com'
password = 'your_api_key'

# 连接
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 认证
uid = common.authenticate(db, username, password, {})

# 测试连接
version = common.version()
print(f"Connected to Odoo {version['server_version']}")
```

### 常用 API 操作

#### 产品查询
```python
# 查询所有已发布产品
products = models.execute_kw(
    db, uid, password,
    'product.template',
    'search_read',
    [[['website_published', '=', True]]],
    {
        'fields': ['name', 'list_price', 'website_url', 'categ_id'],
        'limit': 50
    }
)
```

#### 创建产品
```python
product_id = models.execute_kw(
    db, uid, password,
    'product.template',
    'create',
    [{
        'name': '新产品',
        'list_price': 99.99,
        'website_published': True,
        'description_ecommerce': '产品描述',
        'categ_id': 1,  # 分类 ID
    }]
)
```

#### 更新产品
```python
models.execute_kw(
    db, uid, password,
    'product.template',
    'write',
    [[product_id], {
        'list_price': 89.99,
        'website_published': False,
    }]
)
```

#### 创建页面
```python
page_id = models.execute_kw(
    db, uid, password,
    'website.page',
    'create',
    [{
        'name': 'About Us',
        'type': 'qweb',
        'website_published': True,
        'url': '/about-us',
    }]
)
```

#### 查询订单
```python
orders = models.execute_kw(
    db, uid, password,
    'sale.order',
    'search_read',
    [[['state', 'in', ['sale', 'done']]]],
    {
        'fields': ['name', 'partner_id', 'amount_total', 'date_order'],
        'order': 'date_order desc',
        'limit': 10
    }
)
```

#### 创建销售订单
```python
order_id = models.execute_kw(
    db, uid, password,
    'sale.order',
    'create',
    [{
        'partner_id': customer_id,
        'order_line': [
            (0, 0, {
                'product_id': product_id,
                'product_uom_qty': 2,
                'price_unit': 99.99,
            })
        ],
    }]
)

# 确认订单
models.execute_kw(
    db, uid, password,
    'sale.order',
    'action_confirm',
    [[order_id]]
)
```

---

## 核心模型字段参考

### product.template (产品模板)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| name | char | 产品名称 |
| list_price | float | 销售价格 |
| standard_price | float | 成本价 |
| categ_id | many2one | 产品分类 |
| website_published | boolean | 网站发布状态 |
| website_url | char | 网站 URL |
| description_ecommerce | html | 电商描述 |
| image_1920 | binary | 主图 |
| website_sequence | integer | 网站排序 |
| website_size_x | integer | 网站网格宽度 |
| website_size_y | integer | 网站网格高度 |
| website_style | char | 网站样式 |

### sale.order (销售订单)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| name | char | 订单编号 |
| partner_id | many2one | 客户 |
| date_order | datetime | 订单日期 |
| amount_total | float | 订单总额 |
| amount_untaxed | float | 不含税金额 |
| amount_tax | float | 税额 |
| state | selection | 订单状态 (draft/sent/sale/done/cancel) |
| website_id | many2one | 网站 |
| order_line | one2many | 订单行 |

### website.page (网站页面)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| name | char | 页面名称 |
| type | selection | 页面类型 (qweb/url) |
| url | char | 页面 URL |
| website_published | boolean | 发布状态 |
| website_meta_title | char | Meta 标题 |
| website_meta_description | text | Meta 描述 |
| website_meta_keywords | text | Meta 关键词 |
| arch_db | text | 页面架构 (QWeb) |

### payment.provider (支付提供商)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| name | char | 提供商名称 |
| provider | selection | 提供商类型 (paypal/stripe/adyen 等) |
| state | selection | 状态 (disabled/test/enabled) |
| payment_flow | selection | 支付流程 (direct/form) |
| sequence | integer | 排序 |

### delivery.carrier (配送方式)

| 字段名 | 类型 | 说明 |
|-------|------|------|
| name | char | 配送方式名称 |
| delivery_type | selection | 类型 (fixed/base_based_rule) |
| fixed_price | float | 固定价格 |
| product_id | many2one | 配送产品 |
| website_published | boolean | 网站发布状态 |

---

## 常用域名过滤 (Domains)

### 产品过滤
```python
# 已发布产品
[['website_published', '=', True]]

# 特定分类产品
[['categ_id', '=', category_id]]

# 价格区间
[['list_price', '>=', 50], ['list_price', '<=', 200]]

# 有库存产品
[['qty_available', '>', 0]]
```

### 订单过滤
```python
# 已确认订单
[['state', '=', 'sale']]

# 已完成订单
[['state', '=', 'done']]

# 特定客户订单
[['partner_id', '=', customer_id]]

# 最近 7 天订单
[['date_order', '>=', (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')]]
```

### 页面过滤
```python
# 已发布页面
[['website_published', '=', True]]

# 特定 URL 页面
[['url', '=', '/about-us']]

# 自定义页面
[['type', '=', 'qweb']]
```

---

## 错误代码处理

### 常见错误

| 错误 | 原因 | 解决方案 |
|-----|------|---------|
| `AccessDenied` | 认证失败 | 检查用户名/密码/API Key |
| `ValidationError` | 数据验证失败 | 检查必填字段和数据格式 |
| `UserError` | 业务逻辑错误 | 查看错误消息详情 |
| `Timeout` | 请求超时 | 增加超时时间或优化查询 |
| `ConnectionRefused` | 连接被拒绝 | 检查网络和防火墙设置 |

### 错误处理示例
```python
import xmlrpc.client
from xmlrpc.client import Fault

try:
    result = models.execute_kw(db, uid, password, model, method, args)
except Fault as e:
    print(f"RPC Error: {e.faultString}")
except Exception as e:
    print(f"General Error: {str(e)}")
```

---

## 性能优化建议

### API 调用优化
- ✅ 使用 `search_read` 替代 `search` + `read`
- ✅ 指定需要的字段 `fields` 参数
- ✅ 使用 `limit` 限制返回数量
- ✅ 批量操作使用 `write` 而非多次调用
- ✅ 使用 `search_count` 获取数量而非 `len(search())`

### 查询优化
```python
# ❌ 低效：获取所有字段
products = models.execute_kw(db, uid, password, 'product.template', 'read', [ids])

# ✅ 高效：只获取需要的字段
products = models.execute_kw(
    db, uid, password, 
    'product.template', 
    'read', 
    [ids], 
    {'fields': ['name', 'list_price']}
)
```

### 批量操作
```python
# ❌ 低效：逐个更新
for product_id in ids:
    models.execute_kw(db, uid, password, 'product.template', 'write', 
                      [[product_id], {'website_published': True}])

# ✅ 高效：批量更新
models.execute_kw(db, uid, password, 'product.template', 'write', 
                  [ids, {'website_published': True}])
```

---

## 安全最佳实践

### API Key 管理
- ✅ 为不同用途创建不同 API Key
- ✅ 定期轮换 API Key
- ✅ 不在代码中硬编码 Key
- ✅ 使用环境变量存储凭证

```python
import os
from dotenv import load_dotenv

load_dotenv()

url = os.getenv('ODOO_URL')
db = os.getenv('ODOO_DB')
username = os.getenv('ODOO_USERNAME')
password = os.getenv('ODOO_API_KEY')  # 从环境变量读取
```

### 权限控制
- ✅ 创建专用 API 用户 (非 admin)
- ✅ 最小权限原则
- ✅ 定期审计访问日志
- ✅ 限制 IP 访问 (如可能)

---

**最后更新**: 2026-04-12  
**版本**: v1.0  
**维护者**: Gates
