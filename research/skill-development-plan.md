# Odoo Skill 开发计划

**项目**: Odoo Knowledge Base Skill Suite  
**创建日期**: 2026-04-12  
**版本**: v1.0  
**负责人**: Gates

---

## 项目概述

开发两个 OpenClaw Skills，用于自动化管理 Odoo 网站和电商模块：

1. **odoo-website-skill**: 网站内容管理自动化
2. **odoo-ecommerce-skill**: 电商运营自动化

---

## Skill 1: odoo-website-skill

### 基本信息

```yaml
name: odoo-website-skill
description: Odoo 网站管理自动化 Skill，支持页面创建、SEO 优化、表单管理
version: 1.0.0
author: Gates
license: MIT
openclaw_version: "1.0"
```

### 功能范围

#### P0 功能 (必须实现)
- [ ] **页面管理**
  - 创建新页面
  - 更新页面内容
  - 发布/取消发布
  - 删除页面
  
- [ ] **SEO 优化**
  - 批量更新 Meta 标签
  - 生成 SEO 报告
  - 检查 SEO 问题
  
- [ ] **菜单管理**
  - 创建导航菜单
  - 更新菜单顺序
  - 删除菜单项

#### P1 功能 (推荐使用)
- [ ] **Building Blocks**
  - 添加常用代码块
  - 自定义代码块模板
  
- [ ] **表单管理**
  - 创建联系表单
  - 配置表单字段
  - 查看表单提交

- [ ] **多语言支持**
  - 页面翻译
  - 语言切换配置

### 技术实现

#### 目录结构
```
odoo-website-skill/
├── SKILL.md                 # Skill 定义文件
├── README.md                # 使用说明
├── requirements.txt         # Python 依赖
├── src/
│   ├── __init__.py
│   ├── client.py           # Odoo API 客户端
│   ├── page_manager.py     # 页面管理
│   ├── seo_optimizer.py    # SEO 优化
│   ├── menu_manager.py     # 菜单管理
│   └── form_builder.py     # 表单构建
├── tests/
│   ├── __init__.py
│   ├── test_page_manager.py
│   └── test_seo_optimizer.py
└── examples/
    ├── create_page.py
    └── bulk_seo_update.py
```

#### 核心代码示例

**client.py** - Odoo API 客户端
```python
import xmlrpc.client
from typing import Optional, Dict, Any, List

class OdooClient:
    def __init__(self, url: str, db: str, username: str, password: str):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        
        # 初始化连接
        self.common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        self.models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        
        # 认证
        self.uid = self.common.authenticate(db, username, password, {})
        
        if not self.uid:
            raise Exception("Authentication failed")
    
    def version(self) -> Dict[str, Any]:
        """获取 Odoo 版本信息"""
        return self.common.version()
    
    def execute(self, model: str, method: str, *args, **kwargs):
        """执行模型方法"""
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, method, args, kwargs
        )
    
    def search_read(self, model: str, domain: List, 
                    fields: Optional[List[str]] = None, 
                    limit: Optional[int] = None) -> List[Dict]:
        """搜索并读取记录"""
        params = {}
        if fields:
            params['fields'] = fields
        if limit:
            params['limit'] = limit
        return self.execute(model, 'search_read', domain, **params)
    
    def create(self, model: str, values: Dict) -> int:
        """创建记录"""
        return self.execute(model, 'create', [values])
    
    def write(self, model: str, ids: List[int], values: Dict) -> bool:
        """更新记录"""
        return self.execute(model, 'write', [ids, values])
    
    def unlink(self, model: str, ids: List[int]) -> bool:
        """删除记录"""
        return self.execute(model, 'unlink', [ids])
```

**page_manager.py** - 页面管理
```python
from typing import Optional, List, Dict
from .client import OdooClient

class PageManager:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def create_page(self, name: str, url: str, 
                    content: Optional[str] = None,
                    published: bool = True) -> int:
        """创建新页面"""
        values = {
            'name': name,
            'type': 'qweb',
            'url': url,
            'website_published': published,
        }
        
        if content:
            values['arch_db'] = content
        
        return self.client.create('website.page', values)
    
    def update_page(self, page_id: int, **kwargs) -> bool:
        """更新页面"""
        allowed_fields = ['name', 'url', 'arch_db', 
                         'website_published', 'website_meta_title',
                         'website_meta_description', 'website_meta_keywords']
        
        values = {k: v for k, v in kwargs.items() if k in allowed_fields}
        return self.client.write('website.page', [page_id], values)
    
    def publish_page(self, page_id: int, publish: bool = True) -> bool:
        """发布/取消发布页面"""
        return self.update_page(page_id, website_published=publish)
    
    def delete_page(self, page_id: int) -> bool:
        """删除页面"""
        return self.client.unlink('website.page', [page_id])
    
    def get_pages(self, published: Optional[bool] = None, 
                  limit: int = 50) -> List[Dict]:
        """获取页面列表"""
        domain = []
        if published is not None:
            domain.append(['website_published', '=', published])
        
        return self.client.search_read(
            'website.page',
            domain,
            fields=['id', 'name', 'url', 'website_published', 'website_meta_title'],
            limit=limit
        )
    
    def optimize_seo(self, page_id: int, 
                     title: Optional[str] = None,
                     description: Optional[str] = None,
                     keywords: Optional[str] = None) -> bool:
        """优化页面 SEO"""
        values = {}
        if title:
            values['website_meta_title'] = title
        if description:
            values['website_meta_description'] = description
        if keywords:
            values['website_meta_keywords'] = keywords
        
        return self.update_page(page_id, **values)
```

**seo_optimizer.py** - SEO 优化
```python
from typing import List, Dict
from .client import OdooClient

class SEOOptimizer:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def audit_all_pages(self) -> Dict[str, List[Dict]]:
        """审计所有页面的 SEO"""
        pages = self.client.search_read(
            'website.page',
            [['website_published', '=', True]],
            fields=['id', 'name', 'url', 'website_meta_title', 
                   'website_meta_description', 'website_meta_keywords']
        )
        
        issues = {
            'missing_title': [],
            'missing_description': [],
            'short_description': [],
            'missing_keywords': [],
        }
        
        for page in pages:
            if not page.get('website_meta_title'):
                issues['missing_title'].append(page)
            
            if not page.get('website_meta_description'):
                issues['missing_description'].append(page)
            elif len(page['website_meta_description']) < 50:
                issues['short_description'].append(page)
            
            if not page.get('website_meta_keywords'):
                issues['missing_keywords'].append(page)
        
        return issues
    
    def bulk_update_seo(self, updates: List[Dict]) -> int:
        """批量更新 SEO 信息"""
        count = 0
        for update in updates:
            page_id = update.pop('id')
            self.client.write('website.page', [page_id], update)
            count += 1
        return count
    
    def generate_sitemap_report(self) -> Dict:
        """生成 Sitemap 报告"""
        pages = self.client.search_read(
            'website.page',
            [['website_published', '=', True]],
            fields=['id', 'name', 'url', 'write_date']
        )
        
        return {
            'total_pages': len(pages),
            'pages': pages,
            'sitemap_url': f'{self.client.url}/sitemap.xml'
        }
```

### 命令接口设计

```python
# 命令示例
commands = {
    # 页面管理
    "create_page": {
        "description": "创建新页面",
        "parameters": {
            "name": "页面名称",
            "url": "页面 URL",
            "content": "页面内容 (可选)",
            "published": "是否发布 (默认 True)"
        }
    },
    
    "update_page": {
        "description": "更新页面",
        "parameters": {
            "page_id": "页面 ID",
            "name": "新名称 (可选)",
            "content": "新内容 (可选)",
            "published": "发布状态 (可选)"
        }
    },
    
    "delete_page": {
        "description": "删除页面",
        "parameters": {
            "page_id": "页面 ID"
        }
    },
    
    # SEO 优化
    "optimize_seo": {
        "description": "优化页面 SEO",
        "parameters": {
            "page_id": "页面 ID",
            "title": "Meta 标题",
            "description": "Meta 描述",
            "keywords": "Meta 关键词"
        }
    },
    
    "audit_seo": {
        "description": "审计所有页面 SEO",
        "parameters": {}
    },
    
    "bulk_seo_update": {
        "description": "批量更新 SEO",
        "parameters": {
            "updates": "更新列表 [{'id': 1, 'title': '...', 'description': '...'}]"
        }
    },
    
    # 菜单管理
    "create_menu": {
        "description": "创建菜单项",
        "parameters": {
            "name": "菜单名称",
            "url": "菜单 URL",
            "parent_id": "父菜单 ID (可选)",
            "sequence": "排序 (可选)"
        }
    },
    
    "update_menu": {
        "description": "更新菜单",
        "parameters": {
            "menu_id": "菜单 ID",
            "name": "新名称",
            "url": "新 URL",
            "sequence": "新排序"
        }
    },
}
```

### 测试计划

```python
# tests/test_page_manager.py
import unittest
from src.page_manager import PageManager
from src.client import OdooClient

class TestPageManager(unittest.TestCase):
    def setUp(self):
        self.client = OdooClient(
            url='https://test.odoo.com',
            db='test_db',
            username='test',
            password='test_key'
        )
        self.manager = PageManager(self.client)
    
    def test_create_page(self):
        page_id = self.manager.create_page(
            name='Test Page',
            url='/test-page',
            published=False
        )
        self.assertIsInstance(page_id, int)
        self.assertGreater(page_id, 0)
    
    def test_update_page(self):
        page_id = self.test_create_page()
        result = self.manager.update_page(
            page_id,
            name='Updated Page'
        )
        self.assertTrue(result)
    
    def test_get_pages(self):
        pages = self.manager.get_pages(limit=10)
        self.assertIsInstance(pages, list)
    
    def tearDown(self):
        # 清理测试数据
        pass

if __name__ == '__main__':
    unittest.main()
```

---

## Skill 2: odoo-ecommerce-skill

### 基本信息

```yaml
name: odoo-ecommerce-skill
description: Odoo 电商管理自动化 Skill，支持产品、订单、支付、配送管理
version: 1.0.0
author: Gates
license: MIT
openclaw_version: "1.0"
```

### 功能范围

#### P0 功能 (必须实现)
- [ ] **产品管理**
  - 创建产品
  - 更新产品信息
  - 批量导入产品
  - 产品查询
  
- [ ] **订单管理**
  - 查询订单
  - 更新订单状态
  - 创建订单
  - 订单导出

- [ ] **库存管理**
  - 库存查询
  - 库存预警
  - 库存调整

#### P1 功能 (推荐使用)
- [ ] **支付配置**
  - 支付提供商配置
  - 支付状态查询
  
- [ ] **配送管理**
  - 配送方式配置
  - 运费模板管理
  - 物流跟踪

- [ ] **数据分析**
  - 销售报表
  - 产品分析
  - 客户分析

### 目录结构
```
odoo-ecommerce-skill/
├── SKILL.md
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── client.py           # Odoo API 客户端 (复用)
│   ├── product_manager.py  # 产品管理
│   ├── order_manager.py    # 订单管理
│   ├── inventory_manager.py # 库存管理
│   ├── payment_manager.py  # 支付管理
│   ├── shipping_manager.py # 配送管理
│   └── analytics.py        # 数据分析
├── tests/
│   ├── test_product_manager.py
│   ├── test_order_manager.py
│   └── test_inventory_manager.py
└── examples/
    ├── bulk_import_products.py
    ├── sales_report.py
    └── inventory_alert.py
```

### 核心代码示例

**product_manager.py** - 产品管理
```python
from typing import List, Dict, Optional
from .client import OdooClient

class ProductManager:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def create_product(self, name: str, price: float, 
                       category_id: Optional[int] = None,
                       description: Optional[str] = None,
                       published: bool = True) -> int:
        """创建产品"""
        values = {
            'name': name,
            'list_price': price,
            'website_published': published,
        }
        
        if category_id:
            values['categ_id'] = category_id
        
        if description:
            values['description_ecommerce'] = description
        
        return self.client.create('product.template', values)
    
    def update_product(self, product_id: int, **kwargs) -> bool:
        """更新产品"""
        allowed_fields = ['name', 'list_price', 'standard_price',
                         'description_ecommerce', 'website_published',
                         'categ_id']
        
        values = {k: v for k, v in kwargs.items() if k in allowed_fields}
        return self.client.write('product.template', [product_id], values)
    
    def get_products(self, published: Optional[bool] = None,
                     category_id: Optional[int] = None,
                     limit: int = 50) -> List[Dict]:
        """获取产品列表"""
        domain = []
        if published is not None:
            domain.append(['website_published', '=', published])
        if category_id:
            domain.append(['categ_id', '=', category_id])
        
        return self.client.search_read(
            'product.template',
            domain,
            fields=['id', 'name', 'list_price', 'website_url', 
                   'website_published', 'qty_available'],
            limit=limit
        )
    
    def bulk_import_products(self, products: List[Dict]) -> List[int]:
        """批量导入产品"""
        ids = []
        for product_data in products:
            product_id = self.create_product(**product_data)
            ids.append(product_id)
        return ids
    
    def delete_product(self, product_id: int) -> bool:
        """删除产品"""
        return self.client.unlink('product.template', [product_id])
```

**order_manager.py** - 订单管理
```python
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .client import OdooClient

class OrderManager:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def get_orders(self, state: Optional[str] = None,
                   customer_id: Optional[int] = None,
                   date_from: Optional[str] = None,
                   limit: int = 50) -> List[Dict]:
        """获取订单列表"""
        domain = []
        if state:
            domain.append(['state', '=', state])
        if customer_id:
            domain.append(['partner_id', '=', customer_id])
        if date_from:
            domain.append(['date_order', '>=', date_from])
        
        return self.client.search_read(
            'sale.order',
            domain,
            fields=['id', 'name', 'partner_id', 'amount_total',
                   'state', 'date_order'],
            order='date_order desc',
            limit=limit
        )
    
    def create_order(self, customer_id: int, 
                     products: List[Dict]) -> int:
        """创建订单"""
        order_lines = []
        for product in products:
            line = (0, 0, {
                'product_id': product['product_id'],
                'product_uom_qty': product.get('qty', 1),
                'price_unit': product.get('price', 0),
            })
            order_lines.append(line)
        
        order_id = self.client.create('sale.order', {
            'partner_id': customer_id,
            'order_line': order_lines,
        })
        
        return order_id
    
    def confirm_order(self, order_id: int) -> bool:
        """确认订单"""
        return self.client.execute(
            'sale.order', 'action_confirm', [order_id]
        )
    
    def cancel_order(self, order_id: int) -> bool:
        """取消订单"""
        return self.client.execute(
            'sale.order', 'action_cancel', [order_id]
        )
    
    def get_order_details(self, order_id: int) -> Dict:
        """获取订单详情"""
        orders = self.client.search_read(
            'sale.order',
            [['id', '=', order_id]],
            fields=['name', 'partner_id', 'amount_total',
                   'amount_untaxed', 'amount_tax', 'state',
                   'date_order', 'order_line']
        )
        return orders[0] if orders else None
```

**inventory_manager.py** - 库存管理
```python
from typing import List, Dict
from .client import OdooClient

class InventoryManager:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def get_stock_levels(self, product_ids: Optional[List[int]] = None) -> List[Dict]:
        """获取库存水平"""
        domain = []
        if product_ids:
            domain.append(['product_id', 'in', product_ids])
        
        return self.client.search_read(
            'stock.quant',
            domain,
            fields=['product_id', 'quantity', 'reserved_quantity',
                   'available_quantity', 'location_id']
        )
    
    def check_low_stock(self, threshold: int = 10) -> List[Dict]:
        """检查低库存产品"""
        stocks = self.get_stock_levels()
        low_stock = []
        
        for stock in stocks:
            if stock['available_quantity'] <= threshold:
                low_stock.append(stock)
        
        return low_stock
    
    def update_stock(self, product_id: int, quantity: int, 
                     location_id: Optional[int] = None) -> bool:
        """更新库存"""
        domain = [['product_id', '=', product_id]]
        if location_id:
            domain.append(['location_id', '=', location_id])
        
        stocks = self.client.search_read('stock.quant', domain)
        
        if stocks:
            return self.client.write('stock.quant', [stocks[0]['id']], {
                'quantity': quantity
            })
        else:
            # 创建新库存记录
            values = {
                'product_id': product_id,
                'quantity': quantity,
            }
            if location_id:
                values['location_id'] = location_id
            return self.client.create('stock.quant', values)
```

**analytics.py** - 数据分析
```python
from typing import Dict, List
from datetime import datetime, timedelta
from .client import OdooClient

class Analytics:
    def __init__(self, client: OdooClient):
        self.client = client
    
    def sales_report(self, date_from: str, date_to: str) -> Dict:
        """销售报表"""
        orders = self.client.search_read(
            'sale.order',
            [
                ['state', 'in', ['sale', 'done']],
                ['date_order', '>=', date_from],
                ['date_order', '<=', date_to]
            ],
            fields=['amount_total', 'date_order']
        )
        
        total_sales = sum(order['amount_total'] for order in orders)
        order_count = len(orders)
        avg_order_value = total_sales / order_count if order_count > 0 else 0
        
        return {
            'total_sales': total_sales,
            'order_count': order_count,
            'avg_order_value': avg_order_value,
            'period': f'{date_from} to {date_to}'
        }
    
    def product_performance(self, limit: int = 10) -> List[Dict]:
        """产品表现分析"""
        products = self.client.search_read(
            'product.template',
            [['website_published', '=', True]],
            fields=['id', 'name', 'list_price', 'sales_count'],
            order='sales_count desc',
            limit=limit
        )
        return products
    
    def customer_analysis(self) -> Dict:
        """客户分析"""
        partners = self.client.search_read(
            'res.partner',
            [['customer', '=', True]],
            fields=['id', 'name', 'email', 'sale_order_count']
        )
        
        total_customers = len(partners)
        active_customers = sum(1 for p in partners if p['sale_order_count'] > 0)
        
        return {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'activation_rate': active_customers / total_customers if total_customers > 0 else 0
        }
```

### 命令接口设计

```python
commands = {
    # 产品管理
    "create_product": {
        "description": "创建产品",
        "parameters": {
            "name": "产品名称",
            "price": "销售价格",
            "category_id": "分类 ID (可选)",
            "description": "产品描述 (可选)",
            "published": "是否发布 (默认 True)"
        }
    },
    
    "bulk_import_products": {
        "description": "批量导入产品",
        "parameters": {
            "products": "产品列表 [{'name': '...', 'price': 99.99, ...}]"
        }
    },
    
    "update_product": {
        "description": "更新产品",
        "parameters": {
            "product_id": "产品 ID",
            "name": "新名称",
            "price": "新价格",
            "published": "发布状态"
        }
    },
    
    # 订单管理
    "get_orders": {
        "description": "查询订单",
        "parameters": {
            "state": "订单状态 (可选)",
            "customer_id": "客户 ID (可选)",
            "date_from": "起始日期 (可选)",
            "limit": "数量限制 (默认 50)"
        }
    },
    
    "create_order": {
        "description": "创建订单",
        "parameters": {
            "customer_id": "客户 ID",
            "products": "产品列表 [{'product_id': 1, 'qty': 2, 'price': 99.99}]"
        }
    },
    
    "confirm_order": {
        "description": "确认订单",
        "parameters": {
            "order_id": "订单 ID"
        }
    },
    
    # 库存管理
    "check_stock": {
        "description": "查询库存",
        "parameters": {
            "product_id": "产品 ID (可选，不传则查询所有)"
        }
    },
    
    "low_stock_alert": {
        "description": "低库存预警",
        "parameters": {
            "threshold": "预警阈值 (默认 10)"
        }
    },
    
    # 数据分析
    "sales_report": {
        "description": "销售报表",
        "parameters": {
            "date_from": "起始日期 (YYYY-MM-DD)",
            "date_to": "结束日期 (YYYY-MM-DD)"
        }
    },
    
    "product_performance": {
        "description": "产品表现分析",
        "parameters": {
            "limit": "返回数量 (默认 10)"
        }
    },
}
```

---

## 开发时间表

### Phase 1: 基础框架 (2 周)
**时间**: 2026-04-13 ~ 2026-04-26

- [ ] 搭建项目结构
- [ ] 实现 OdooClient 基类
- [ ] 配置认证和连接
- [ ] 编写单元测试框架
- [ ] 文档模板创建

**交付物**:
- 项目骨架
- 基础客户端库
- 测试框架

### Phase 2: 核心功能开发 (3 周)
**时间**: 2026-04-27 ~ 2026-05-17

#### Week 1: odoo-website-skill
- [ ] PageManager 实现
- [ ] SEOOptimizer 实现
- [ ] MenuManager 实现

#### Week 2: odoo-ecommerce-skill
- [ ] ProductManager 实现
- [ ] OrderManager 实现
- [ ] InventoryManager 实现

#### Week 3: 测试和优化
- [ ] 单元测试
- [ ] 集成测试
- [ ] Bug 修复

**交付物**:
- 完整的核心功能
- 测试覆盖率 >80%

### Phase 3: 高级功能 (2 周)
**时间**: 2026-05-18 ~ 2026-05-31

- [ ] 批量操作支持
- [ ] 数据分析模块
- [ ] 定时任务支持
- [ ] 性能优化

**交付物**:
- 高级功能模块
- 性能优化报告

### Phase 4: 测试与文档 (1 周)
**时间**: 2026-06-01 ~ 2026-06-07

- [ ] 集成测试
- [ ] 用户文档
- [ ] API 文档
- [ ] 示例脚本
- [ ] 代码审查

**交付物**:
- 完整文档
- 示例库
- 发布版本

---

## 质量保障

### 代码标准
- ✅ 遵循 PEP 8 规范
- ✅ 类型注解完整
- ✅ 文档字符串齐全
- ✅ 单元测试覆盖 >80%

### 测试要求
```bash
# 运行测试
pytest tests/ -v --cov=src --cov-report=html

# 覆盖率要求
# Line Coverage: >= 80%
# Branch Coverage: >= 70%
```

### 代码审查清单
- [ ] 代码符合规范
- [ ] 测试通过
- [ ] 文档完整
- [ ] 无安全漏洞
- [ ] 性能可接受

---

## 风险管理

### 技术风险
| 风险 | 影响 | 概率 | 缓解措施 |
|-----|------|------|---------|
| API 变更 | 高 | 低 | 使用官方稳定版本 API |
| 性能问题 | 中 | 中 | 批量操作、缓存优化 |
| 认证失败 | 高 | 低 | 完善的错误处理 |

### 应对措施
1. **API 版本控制**: 锁定 Odoo 18.0 API
2. **错误处理**: 完善的异常捕获和日志
3. **性能监控**: 关键操作耗时统计
4. **文档更新**: 及时同步 API 变更

---

## 成功指标

### 功能指标
- ✅ 所有 P0 功能实现
- ✅ 测试覆盖率 >80%
- ✅ 文档完整度 100%

### 性能指标
- ✅ API 调用成功率 >99%
- ✅ 平均响应时间 <2s
- ✅ 批量操作效率提升 >50%

### 用户指标
- ✅ 用户满意度 >4.5/5
- ✅ 文档清晰度 >4.5/5
- ✅ 易用性 >4.5/5

---

## 附录

### 环境配置

**requirements.txt**
```
xmlrpc-client>=0.1.0
python-dotenv>=1.0.0
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
```

**开发环境设置**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发工具
pip install black flake8 mypy pytest pytest-cov
```

### 环境变量
```bash
# .env 文件
ODOO_URL=https://your-company.odoo.com
ODOO_DB=your_database
ODOO_USERNAME=your_email@example.com
ODOO_API_KEY=your_api_key
```

### 参考资源
- [Odoo 官方文档](https://www.odoo.com/documentation/18.0/)
- [External API 参考](https://www.odoo.com/documentation/18.0/developer/reference/external_api.html)
- [OpenClaw Skill 规范](https://docs.openclaw.ai/tools/skills)

---

**文档版本**: v1.0  
**最后更新**: 2026-04-12  
**维护者**: Gates  
**审批状态**: 待审批
