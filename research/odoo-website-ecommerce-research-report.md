# Odoo 网站和电商模块调研报告

**调研日期**: 2026-04-12  
**调研版本**: Odoo 18.0 (最新稳定版)  
**调研范围**: Website Builder + eCommerce 模块

---

## 执行摘要

本次调研全面分析了 Odoo 网站构建器和电商模块的核心功能、API 接口、开发最佳实践。调研发现：

- **Website Builder**: 提供拖拽式页面设计、SEO 优化、主题模板系统、表单构建器
- **eCommerce**: 完整的产品管理、购物车结账、支付集成、订单履行流程
- **API 支持**: XML-RPC/JSON-RPC 接口，支持外部系统集成
- **开发扩展**: 支持自定义 Building Blocks、主题开发、模块定制

---

## 1. Odoo 网站构建器调研

### 1.1 网站页面设计

#### 核心功能
- **拖拽式编辑器**: 可视化编辑，实时预览
- **Building Blocks (代码片段)**: 预构建的内容模块，可拖拽使用
- **响应式设计**: 基于 Bootstrap，自动适配桌面/平板/手机
- **多媒体支持**: 图片、视频、画廊、轮播

#### Building Blocks 结构
```
views/
├── snippets/
│   ├── options.xml          # 选项配置
│   └── s_snippet_name.xml   # 代码片段模板

static/
├── src/
│   └── snippets/
│       └── s_snippet_name/
│           ├── 000.js       # JavaScript
│           ├── 000.scss     # 样式
│           └── 000.xml      # 模板
```

#### 自定义代码片段示例
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="s_custom_snippet" name="Custom Snippet">
        <section class="s_custom_snippet" data-name="Custom" data-snippet="s_custom_snippet">
            <div class="container">
                <h2>Custom Content</h2>
            </div>
        </section>
    </template>
</odoo>
```

### 1.2 主题和模板

#### 主题系统
- **官方主题**: Odoo 提供多个免费主题
- **第三方主题市场**: apps.odoo.com/apps/themes
- **自定义主题开发**: 支持 SCSS、JavaScript、XML 模板

#### 主题开发结构
```
theme_custom/
├── __manifest__.py
├── views/
│   └── snippets/
├── static/
│   └── src/
│       ├── scss/
│       └── js/
└── templates/
```

#### 最佳实践
- 使用 Bootstrap 原生类
- 自定义类添加前缀 (如 `.x_nav`)
- 避免在 section 内使用 ID 属性
- 使用小写 + 下划线命名

### 1.3 SEO 优化

#### 内置 SEO 功能
- **Meta 标签管理**: Title、Description、Keywords
- **自动 Sitemap**: `/sitemap.xml`，每 12 小时更新
- **robots.txt**: 自动生成，可自定义
- **301 重定向**: 页面 URL 变更自动创建重定向
- **结构化数据**: 支持 schema.org Microdata
- **Hreflang 标签**: 多语言自动支持

#### SEO 优化工具
路径：`Website ‣ Site ‣ Optimize SEO`

**可配置项**:
- Title Tag (页面标题)
- Description Tag (页面描述)
- Keywords (关键词分析)
- 预览搜索引擎显示效果

#### 图片优化
- 自动压缩并转换为 WebP 格式
- Alt Tag 自动管理
- 支持 Zoom 功能 (最小 1024px)

#### Indexation 控制
- 页面级：取消 Indexed 开关
- 网站级：修改 Domain 字段添加 noindex 标签
- Google Search Console 集成

### 1.4 表单和调查

#### 表单构建器功能
- **拖拽式表单设计**: 可视化字段配置
- **字段类型**: Text、Email、Telephone、URL、Date 等
- **表单动作**:
  - Send an Email (发送邮件)
  - Create an Opportunity (创建 CRM 商机)
- **字段配置**:
  - Required (必填)
  - Default Value (默认值)
  - Visibility (可见性控制)
  - Animation (动画效果)

#### 表单自定义示例
```html
<form action="/website/form/" method="post" 
      enctype="multipart/form-data" 
      class="o_mark_required" 
      data-mark="*" 
      data-success-mode="message">
    <!-- 表单字段 -->
</form>
```

#### CRM 集成
- 表单提交自动创建 Leads/Opportunities
- 可分配给指定销售团队/销售人员
- 支持文件上传

#### 调查功能
- 通过第三方模块支持 (如 odoo-powr-form-builder)
- 市场调研、客户反馈收集

---

## 2. Odoo 电商模块调研

### 2.1 产品管理

#### 核心功能
- **产品创建**: 前端/后端均可创建
- **产品变体**: 支持多属性组合 (颜色、尺寸等)
- **产品分类**: 多级分类系统
- **数字文件**: 支持证书、电子书、用户手册
- **多语言**: 字段级翻译支持

#### 产品页面配置
```python
# 产品字段示例
{
    'name': '产品名称',
    'list_price': '销售价格',
    'taxes_id': '客户税率',
    'description_ecommerce': '电商描述',
    'website_published': '是否发布',
}
```

#### 产品媒体管理
- **图片**: PNG/JPG 格式，支持 Zoom (≥1024px)
- **视频**: 支持 URL 或 Embed 代码
- **布局**: Carousel (轮播) / Grid (网格)
- **缩略图**: 左侧/底部对齐

#### 批量操作
- **导入**: 支持 XLSX/CSV 批量导入
- **批量发布**: 列表视图批量切换 Published 状态

### 2.2 购物车和结账

#### 购物车配置
路径：`Website ‣ Configuration ‣ Settings ‣ Shop - Checkout Process`

**配置选项**:
- **Add to Cart 行为**:
  - Stay on Product Page (留在产品页)
  - Go to Cart (跳转购物车)
  - Let the user decide (弹窗选择)
- **Buy Now 按钮**: 直接跳转结账
- **Re-order From Portal**: 允许客户再次下单

#### 结账流程
```
1. Review Order (订单确认)
   - 查看商品、调整数量
   - 使用促销码/礼品卡
   - 添加到愿望清单

2. Delivery (配送信息)
   - 登录/输入邮箱
   - 配送地址
   - 选择配送方式

3. Extra Info (可选)
   - B2B 字段
   - 新闻通讯订阅

4. Payment (支付)
   - 选择支付方式
   - 同意条款 (可启用)

5. Order Confirmation (订单确认)
   - 订单摘要
   - 确认邮件
```

#### 自定义功能
- **Suggested Accessories**: 推荐配件产品
- **Promo Code**: 促销码/折扣码
- **Wishlist**: 愿望清单
- **Terms & Conditions**: 条款确认

### 2.3 支付集成

#### 支持的支付提供商
- **PayPal**: 内置支持
- **Stripe**: 内置支持
- **Authorize.net**: 支持
- **SEPA Direct Debit**: 欧洲直接借记
- **Adyen**: 支持
- **Flutterwave**: 支持

#### 支付配置
路径：`Website ‣ Configuration ‣ Payment Providers`

**配置步骤**:
1. Activate 支付提供商
2. 配置凭证 (API Keys 等)
3. 设置捕获方式 (自动/手动)
4. 测试交易

#### 电子钱包和礼品卡
路径：`Website ‣ Configuration ‣ Settings ‣ Shop-Products`

- 启用 eWallet/Gift Cards
- 客户可在结账时使用
- 支持礼品卡码输入

#### 快速结账
- 支持 Express Checkout 的支付商会显示快速按钮
- 客户可直接从购物车跳转到确认页

### 2.4 订单履行

#### 配送方式配置
路径：`Inventory ‣ Configuration ‣ Delivery Methods`

**配送类型**:
- **Fixed Price**: 固定运费
- **Based on Rules**: 基于规则 (重量、价格、数量)
- **Third-party Carrier**: 第三方物流集成

#### 第三方物流集成
- **DHL**: 内置集成
- **FedEx**: 内置集成
- **UPS**: 内置集成
- **Sendcloud**: 支持
- **EasyPost**: 支持
- **Starshipit**: 支持

#### 运费计算
```python
# 运费规则示例
{
    'condition_amount': '基于订单金额',
    'condition_weight': '基于重量',
    'fixed_price': 50.00,
    'free_if_order_above': 500.00,  # 满额免运费
}
```

#### 订单跟踪
- **Tracking Link**: 客户可在门户查看物流
- **Carrier Integration**: 自动获取运单号
- **客户门户**: 查看订单状态、物流信息

#### 店内取货 (Click & Collect)
路径：`Website ‣ Configuration ‣ Settings ‣ eCommerce`

- 启用 Click & Collect
- 指定取货仓库
- 客户可选择取货

---

## 3. API 参考

### 3.1 外部 API (XML-RPC/JSON-RPC)

#### 连接配置
```python
import xmlrpc.client

url = 'https://mycompany.odoo.com'
db = 'mycompany'
username = 'admin'
password = 'api_key_or_password'

# 连接
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 认证
uid = common.authenticate(db, username, password, {})
```

#### API Keys
路径：`Preferences ‣ Account Security ‣ New API Key`

- 替代密码用于 API 访问
- 可创建多个 Key 用于不同用途
- 支持撤销

#### 常用操作

**查询记录**:
```python
# 搜索
ids = models.execute_kw(
    db, uid, password,
    'product.template',
    'search',
    [[['website_published', '=', True]]]
)

# 读取
products = models.execute_kw(
    db, uid, password,
    'product.template',
    'search_read',
    [[['website_published', '=', True]]],
    {'fields': ['name', 'list_price', 'website_url'], 'limit': 10}
)
```

**创建记录**:
```python
product_id = models.execute_kw(
    db, uid, password,
    'product.template',
    'create',
    [{
        'name': 'New Product',
        'list_price': 99.99,
        'website_published': True
    }]
)
```

**更新记录**:
```python
models.execute_kw(
    db, uid, password,
    'product.template',
    'write',
    [[product_id], {
        'list_price': 89.99
    }]
)
```

**删除记录**:
```python
models.execute_kw(
    db, uid, password,
    'product.template',
    'unlink',
    [[product_id]]
)
```

### 3.2 网站相关模型

#### 核心模型
- `website.page`: 网站页面
- `website.menu`: 网站菜单
- `product.template`: 产品模板
- `product.product`: 产品变体
- `sale.order`: 销售订单
- `payment.provider`: 支付提供商
- `delivery.carrier`: 配送方式

#### 产品模型字段
```python
product_fields = {
    'name': '产品名称',
    'list_price': '销售价格',
    'standard_price': '成本',
    'categ_id': '产品分类',
    'website_published': '网站发布状态',
    'website_url': '网站 URL',
    'description_ecommerce': '电商描述',
    'image_1920': '主图',
    'website_sequence': '网站排序',
}
```

### 3.3 订单管理 API

#### 创建销售订单
```python
order_id = models.execute_kw(
    db, uid, password,
    'sale.order',
    'create',
    [{
        'partner_id': customer_id,
        'website_id': website_id,
        'order_line': [
            (0, 0, {
                'product_id': product_id,
                'product_uom_qty': 2,
            })
        ]
    }]
)
```

#### 确认订单
```python
models.execute_kw(
    db, uid, password,
    'sale.order',
    'action_confirm',
    [[order_id]]
)
```

---

## 4. 示例代码

### 4.1 自定义 Building Block

**文件**: `views/snippets/s_hero_banner.xml`
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <template id="s_hero_banner" name="Hero Banner">
        <section class="s_hero_banner s_parallax_is_fixed" 
                 data-name="Hero Banner" 
                 data-snippet="s_hero_banner">
            <div class="o_we_bg_filter bg-black-50"/>
            <div class="container">
                <div class="row">
                    <div class="col-lg-6">
                        <h1>Welcome to Our Store</h1>
                        <p>Discover amazing products</p>
                        <a href="/shop" class="btn btn-primary">Shop Now</a>
                    </div>
                    <div class="col-lg-6">
                        <img src="/web/image/website.s_hero_banner_image" alt="Hero"/>
                    </div>
                </div>
            </div>
        </section>
    </template>
</odoo>
```

### 4.2 自定义表单处理

**Python 代码**:
```python
from odoo import http
from odoo.http import request

class CustomFormController(http.Controller):
    @http.route('/custom/form/submit', type='http', auth='public', methods=['POST'], csrf=True)
    def submit_form(self, **kwargs):
        # 创建 CRM Lead
        lead_id = request.env['crm.lead'].sudo().create({
            'name': kwargs.get('subject', 'New Lead'),
            'contact_name': kwargs.get('name'),
            'email_from': kwargs.get('email'),
            'phone': kwargs.get('phone'),
            'description': kwargs.get('message'),
        })
        
        # 发送确认邮件
        request.env['mail.mail'].sudo().create({
            'email_to': kwargs.get('email'),
            'subject': 'Thank you for contacting us',
            'body_html': f'<p>Dear {kwargs.get("name")},</p><p>We received your message.</p>',
        }).send()
        
        return request.redirect('/thank-you')
```

### 4.3 产品批量导入脚本

**Python 脚本**:
```python
import csv
import xmlrpc.client

url = 'https://mycompany.odoo.com'
db = 'mycompany'
username = 'admin'
password = 'api_key'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

uid = common.authenticate(db, username, password, {})

# 读取 CSV
with open('products.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        product_id = models.execute_kw(
            db, uid, password,
            'product.template',
            'create',
            [{
                'name': row['name'],
                'list_price': float(row['price']),
                'website_published': True,
                'description_ecommerce': row['description'],
            }]
        )
        print(f"Created product {product_id}: {row['name']}")
```

### 4.4 自定义主题配置

**SCSS 变量**: `static/src/scss/variables.scss`
```scss
// 主题颜色
$o-brand-primary: #0056b3;
$o-brand-secondary: #6c757d;

// 字体
$font-family-sans-serif: 'Roboto', sans-serif;

// 间距
$spacer: 1rem;
$grid-gutter-width: 30px;
```

---

## 5. 最佳实践

### 5.1 网站开发最佳实践

#### 性能优化
- ✅ 使用 WebP 图片格式
- ✅ 启用 CDN (Cloudflare)
- ✅ 最小化 CSS/JS
- ✅ 使用缓存 (Odoo 自动缓存 Sitemap)

#### SEO 最佳实践
- ✅ 每页一个 H1 标签
- ✅ 填写 Meta Title/Description
- ✅ 为图片添加 Alt Tag
- ✅ 使用结构化数据 (schema.org)
- ✅ 创建 Sitemap
- ✅ 配置 robots.txt

#### 响应式设计
- ✅ 使用 Bootstrap 栅格系统
- ✅ 测试移动端显示
- ✅ 避免固定宽度
- ✅ 使用相对单位 (rem, em, %)

### 5.2 电商运营最佳实践

#### 产品管理
- ✅ 高质量产品图片 (≥1024px)
- ✅ 详细的产品描述
- ✅ 合理的产品分类
- ✅ 设置产品标签便于筛选
- ✅ 启用产品评价

#### 转化率优化
- ✅ 简化结账流程
- ✅ 提供多种支付方式
- ✅ 显示运费计算
- ✅ 启用购物车保存 (Wishlist)
- ✅ 添加社会证明 (评价、评分)

#### 订单履行
- ✅ 设置清晰的配送政策
- ✅ 提供订单跟踪
- ✅ 自动发送订单确认邮件
- ✅ 配置库存预警
- ✅ 支持店内取货

### 5.3 安全最佳实践

#### API 安全
- ✅ 使用 API Keys 替代密码
- ✅ 限制 API 访问权限
- ✅ 使用 HTTPS
- ✅ 定期轮换 API Keys

#### 数据安全
- ✅ 启用双因素认证
- ✅ 定期备份数据库
- ✅ 限制管理员访问
- ✅ 审计日志监控

---

## 6. Skill 开发计划

### 6.1 odoo-website-skill

#### 目标
创建 Odoo 网站管理 Skill，支持通过自然语言管理网站内容。

#### 功能范围
- **页面管理**: 创建/编辑/发布页面
- **SEO 优化**: 批量优化 Meta 标签
- **Building Blocks**: 快速添加常用代码块
- **表单管理**: 创建联系表单、调查问卷
- **菜单管理**: 配置网站导航

#### 技术实现
```yaml
name: odoo-website-skill
description: Odoo 网站管理自动化 Skill
version: 1.0.0

capabilities:
  - create_page: 创建网站页面
  - update_seo: 优化 SEO 设置
  - add_snippet: 添加 Building Block
  - create_form: 创建表单
  - manage_menu: 管理菜单

api_integration:
  protocol: XML-RPC
  models:
    - website.page
    - website.menu
    - ir.attachment
```

#### 示例命令
```
- "创建一个关于我们页面"
- "优化所有产品的 SEO"
- "添加一个联系表单到首页"
- "更新导航菜单"
```

### 6.2 odoo-ecommerce-skill

#### 目标
创建 Odoo 电商管理 Skill，支持产品、订单、支付的自动化管理。

#### 功能范围
- **产品管理**: 批量创建/更新产品
- **库存管理**: 库存查询、预警
- **订单处理**: 订单查询、状态更新
- **支付配置**: 支付提供商管理
- **配送管理**: 运费模板配置
- **数据分析**: 销售报表生成

#### 技术实现
```yaml
name: odoo-ecommerce-skill
description: Odoo 电商管理自动化 Skill
version: 1.0.0

capabilities:
  - product_create: 创建产品
  - product_update: 更新产品信息
  - product_import: 批量导入产品
  - order_query: 查询订单
  - order_update: 更新订单状态
  - inventory_check: 库存查询
  - payment_config: 支付配置
  - shipping_config: 配送配置
  - sales_report: 销售报表

api_integration:
  protocol: XML-RPC
  models:
    - product.template
    - product.product
    - sale.order
    - stock.quant
    - payment.provider
    - delivery.carrier
```

#### 示例命令
```
- "导入这批新产品"
- "查询昨天的订单"
- "检查产品库存"
- "生成月度销售报告"
- "配置 PayPal 支付"
```

### 6.3 开发路线图

#### Phase 1: 基础框架 (2 周)
- [ ] 搭建 Skill 项目结构
- [ ] 配置 XML-RPC 连接
- [ ] 实现基础认证
- [ ] 创建错误处理机制

#### Phase 2: 核心功能 (3 周)
- [ ] 实现产品管理命令
- [ ] 实现订单管理命令
- [ ] 实现页面管理命令
- [ ] 编写单元测试

#### Phase 3: 高级功能 (2 周)
- [ ] 批量操作支持
- [ ] 数据分析报表
- [ ] 定时任务支持
- [ ] 性能优化

#### Phase 4: 测试与文档 (1 周)
- [ ] 集成测试
- [ ] 用户文档
- [ ] API 文档
- [ ] 示例脚本

---

## 7. 资源链接

### 官方文档
- [Odoo 18.0 Website 文档](https://www.odoo.com/documentation/18.0/applications/websites/website.html)
- [Odoo 18.0 eCommerce 文档](https://www.odoo.com/documentation/18.0/applications/websites/ecommerce.html)
- [External API 参考](https://www.odoo.com/documentation/18.0/developer/reference/external_api.html)
- [Building Blocks 开发](https://www.odoo.com/documentation/18.0/developer/howtos/website_themes/building_blocks.html)
- [SEO 优化指南](https://www.odoo.com/documentation/18.0/applications/websites/website/structure/seo.html)

### 教程
- [Odoo Tutorials: Website](https://www.odoo.com/slides/website-25)
- [Odoo Tutorials: eCommerce](https://www.odoo.com/slides/ecommerce-26)
- [Theme 开发教程](https://www.odoo.com/documentation/18.0/developer/tutorials/website_theme/)

### 第三方资源
- [Odoo Apps Store](https://apps.odoo.com/apps/themes) - 主题市场
- [OCA/website-themes](https://github.com/OCA/website-themes) - 社区主题
- [Odoo JSON-RPC API Guide](https://github.com/amlaksil/Odoo-JSON-RPC-API/)

---

## 8. 总结

### 关键发现

1. **Website Builder 功能强大**
   - 拖拽式编辑，无需编码
   - 丰富的 Building Blocks
   - 完整的 SEO 工具集

2. **eCommerce 模块成熟**
   - 完整的产品 - 订单 - 支付流程
   - 多支付提供商集成
   - 灵活的配送配置

3. **API 支持完善**
   - XML-RPC/JSON-RPC 接口
   - 支持所有核心模型
   - API Keys 认证

4. **开发扩展性好**
   - 自定义 Building Blocks
   - 主题开发支持
   - 模块定制能力

### 建议

1. **优先开发 odoo-ecommerce-skill**
   - 电商需求更明确
   - ROI 更容易量化
   - 产品管理是高频需求

2. **采用分阶段开发**
   - 先实现核心功能
   - 逐步添加高级特性
   - 重视测试和文档

3. **关注性能和安全**
   - API 调用频率控制
   - 敏感数据加密
   - 定期安全审计

---

**报告生成时间**: 2026-04-12 23:58  
**调研负责人**: Gates (Skill 工程师)  
**版本**: v1.0
