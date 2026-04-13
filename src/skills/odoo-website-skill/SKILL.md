---
name: odoo-website-skill
description: Odoo 网站构建 Skill - 提供页面创建/编辑、菜单管理、媒体库管理、主题开发 (安装/配置/自定义样式)、SEO 优化 (Meta 标签/URL 优化/站点地图) 功能。Use when working with Odoo Website modules for: (1) Creating and editing web pages, (2) Menu and navigation management, (3) Theme customization, (4) SEO optimization, (5) Media library management.
---

# Odoo 网站构建 Skill

## 快速开始

### 使用 Odoo XML-RPC API

```python
from scripts.odoo_client import create_client

client = create_client()

# 创建页面
page_id = client.create('website.page', {
    'name': '关于我们',
    'url': '/about',
    'website_published': True,
    'arch': '<t t-name="website.about"><h1>关于我们</h1></t>',
    'key': 'website.about',
})

# 编辑页面
client.write('website.page', [page_id], {
    'arch': '<t t-name="website.about"><h1>Hello World</h1></t>',
})

# SEO 优化
client.write('website.page', [page_id], {
    'website_meta_title': '关于我们 - 公司名',
    'website_meta_description': '了解我们的公司...',
    'website_meta_keywords': '关于我们,公司介绍',
})
```

## 核心功能

### 1. 页面管理

#### 创建页面

```python
page_id = client.create('website.page', {
    'name': '关于我们',
    'url': '/about',
    'website_published': True,
    'arch': '<t t-name="website.about"><h1>关于我们</h1></t>',
    'key': 'website.about',
})
```

### 2. 菜单管理

```python
menu_id = client.create('website.menu', {
    'name': '产品服务',
    'parent_id': main_menu_id,
    'url': '/products',
    'sequence': 10,
})
```

### 3. 主题开发

#### 安装主题

```python
# 安装主题模块
module_id = client.execute('ir.module.module', 'search', [[['name', '=', 'theme_name']]])
client.execute('ir.module.module', 'button_immediate_install', [module_id])
```

#### 自定义样式

```python
# 创建自定义 CSS
css_data = {
    'name': 'Custom CSS',
    'type': 'scss',
    'content': '.custom-class { color: red; }'
}
```

### 4. SEO 优化

#### 设置 Meta 标签

```python
client.write('website.page', [page_id], {
    'website_meta_title': '产品页面',
    'website_meta_description': '产品描述...',
    'website_meta_keywords': '关键词 1，关键词 2',
})
```

## 最佳实践

- 使用响应式设计
- 优化页面加载速度
- 定期更新内容
- 遵循 SEO 最佳实践

## 支持的 Odoo 版本

- Odoo 16.0 LTS
- Odoo 17.0 LTS
- Odoo 18.0 (最新)
