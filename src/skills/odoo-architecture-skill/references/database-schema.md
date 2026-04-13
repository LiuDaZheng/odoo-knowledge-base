# Odoo 数据库结构

## 概述

Odoo 使用 PostgreSQL 作为数据库，ORM 自动管理表结构。

---

## 自动字段

每个模型自动包含以下字段：

```sql
CREATE TABLE sale_order (
    id              SERIAL PRIMARY KEY,
    create_uid      INTEGER REFERENCES res_users(id),
    create_date     TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'UTC'),
    write_uid       INTEGER REFERENCES res_users(id),
    write_date      TIMESTAMP DEFAULT (NOW() AT TIME ZONE 'UTC')
);
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | SERIAL | 主键 |
| `create_uid` | INTEGER | 创建人 (FK to res_users) |
| `create_date` | TIMESTAMP | 创建时间 (UTC) |
| `write_uid` | INTEGER | 最后修改人 |
| `write_date` | TIMESTAMP | 最后修改时间 |

---

## 字段类型映射

### Python → PostgreSQL

| Python 字段 | PostgreSQL 类型 | 示例 |
|-------------|-----------------|------|
| Char | VARCHAR | `name VARCHAR(64)` |
| Text | TEXT | `description TEXT` |
| Html | TEXT | `content TEXT` |
| Integer | INTEGER | `qty INTEGER` |
| Float | NUMERIC | `price NUMERIC(16,3)` |
| Monetary | NUMERIC | `amount NUMERIC(16,2)` |
| Date | DATE | `order_date DATE` |
| Datetime | TIMESTAMP | `create_date TIMESTAMP` |
| Boolean | BOOLEAN | `active BOOLEAN` |
| Binary | BYTEA | `attachment BYTEA` |
| Many2one | INTEGER (FK) | `partner_id INTEGER` |

---

## 关系映射

### Many2one

```python
partner_id = fields.Many2one('res.partner')
```

```sql
ALTER TABLE sale_order ADD COLUMN partner_id INTEGER;
ALTER TABLE sale_order ADD CONSTRAINT sale_order_partner_id_fkey 
    FOREIGN KEY (partner_id) REFERENCES res_partner(id);
```

### One2many

```python
order_line = fields.One2many('sale.order.line', 'order_id')
```

```sql
-- 在 sale_order_line 表创建外键
ALTER TABLE sale_order_line ADD COLUMN order_id INTEGER;
ALTER TABLE sale_order_line ADD CONSTRAINT sale_order_line_order_id_fkey 
    FOREIGN KEY (order_id) REFERENCES sale_order(id);
```

### Many2many

```python
tag_ids = fields.Many2many('sale.tag')
```

```sql
-- 创建关联表
CREATE TABLE sale_order_sale_tag_rel (
    sale_order_id INTEGER NOT NULL,
    sale_tag_id INTEGER NOT NULL,
    PRIMARY KEY (sale_order_id, sale_tag_id),
    FOREIGN KEY (sale_order_id) REFERENCES sale_order(id),
    FOREIGN KEY (sale_tag_id) REFERENCES sale_tag(id)
);
```

---

## 索引

### 自动索引

- 主键 `id` (自动)
- Many2one 字段 (可选)

### 手动索引

```python
# 在字段定义中添加
partner_id = fields.Many2one('res.partner', index=True)

# 或使用 _sql_constraints
_sql_constraints = [
    ('name_uniq', 'unique (name)', 'Name must be unique!'),
]
```

### 创建索引

```sql
-- 单列索引
CREATE INDEX sale_order_partner_id_idx ON sale_order(partner_id);

-- 复合索引
CREATE INDEX sale_order_state_date_idx ON sale_order(state, date_order);

-- 部分索引
CREATE INDEX sale_order_draft_idx ON sale_order(id) WHERE state = 'draft';
```

---

## 表结构示例

### sale_order 表

```sql
CREATE TABLE sale_order (
    -- 自动字段
    id              SERIAL PRIMARY KEY,
    create_uid      INTEGER REFERENCES res_users(id),
    create_date     TIMESTAMP,
    write_uid       INTEGER REFERENCES res_users(id),
    write_date      TIMESTAMP,
    
    -- 业务字段
    name            VARCHAR(64) NOT NULL,
    date_order      TIMESTAMP,
    state           VARCHAR(32) DEFAULT 'draft',
    partner_id      INTEGER REFERENCES res_partner(id),
    amount_untaxed  NUMERIC(16,2),
    amount_tax      NUMERIC(16,2),
    amount_total    NUMERIC(16,2),
    currency_id     INTEGER REFERENCES res_currency(id),
    
    -- 索引
    CONSTRAINT sale_order_name_uniq UNIQUE (name)
);

CREATE INDEX sale_order_partner_id_idx ON sale_order(partner_id);
CREATE INDEX sale_order_state_idx ON sale_order(state);
CREATE INDEX sale_order_date_order_idx ON sale_order(date_order);
```

### sale_order_line 表

```sql
CREATE TABLE sale_order_line (
    -- 自动字段
    id              SERIAL PRIMARY KEY,
    create_uid      INTEGER REFERENCES res_users(id),
    create_date     TIMESTAMP,
    write_uid       INTEGER REFERENCES res_users(id),
    write_date      TIMESTAMP,
    
    -- 业务字段
    order_id        INTEGER REFERENCES sale_order(id) ON DELETE CASCADE,
    product_id      INTEGER REFERENCES product_product(id),
    product_uom_qty NUMERIC(16,3) DEFAULT 1,
    price_unit      NUMERIC(16,3),
    price_subtotal  NUMERIC(16,2),
    price_total     NUMERIC(16,2),
    
    -- 索引
    CONSTRAINT sale_order_line_order_product_uniq UNIQUE (order_id, product_id)
);

CREATE INDEX sale_order_line_order_id_idx ON sale_order_line(order_id);
CREATE INDEX sale_order_line_product_id_idx ON sale_order_line(product_id);
```

---

## 查询优化

### EXPLAIN 分析

```sql
-- 查看查询计划
EXPLAIN ANALYZE
SELECT * FROM sale_order 
WHERE state = 'draft' 
  AND amount_total > 1000;

-- 输出示例:
-- Index Scan using sale_order_state_idx on sale_order
--   Index Cond: (state = 'draft'::character varying)
--   Filter: (amount_total > 1000)
```

### 索引使用

```sql
-- ✅ 使用索引
SELECT * FROM sale_order WHERE state = 'draft';

-- ❌ 不使用索引 (函数导致)
SELECT * FROM sale_order WHERE UPPER(state) = 'DRAFT';

-- ❌ 不使用索引 (前缀通配符)
SELECT * FROM sale_order WHERE name LIKE '%SO%';

-- ✅ 使用索引 (后缀通配符)
SELECT * FROM sale_order WHERE name LIKE 'SO%';
```

---

## 数据库维护

### VACUUM

```sql
-- 清理死元组
VACUUM sale_order;

-- 完全清理 (锁表)
VACUUM FULL sale_order;

-- 分析表 (更新统计)
ANALYZE sale_order;

-- 组合
VACUUM ANALYZE sale_order;
```

### 表大小

```sql
-- 查看表大小
SELECT 
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- 查看行数
SELECT 
    relname AS table_name,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

### 索引维护

```sql
-- 查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- 重建索引
REINDEX TABLE sale_order;
REINDEX INDEX sale_order_partner_id_idx;
```

---

## 数据迁移

### 导出

```sql
-- 导出为 CSV
COPY (
    SELECT id, name, partner_id, amount_total 
    FROM sale_order 
    WHERE state = 'sale'
) TO '/tmp/sale_orders.csv' 
WITH (FORMAT CSV, HEADER);
```

### 导入

```sql
-- 从 CSV 导入
COPY sale_order (id, name, partner_id, amount_total) 
FROM '/tmp/sale_orders.csv' 
WITH (FORMAT CSV, HEADER);
```

---

## 备份与恢复

### 备份

```bash
# 完整备份
pg_dump -U odoo -h localhost mydb > backup.sql

# 仅结构
pg_dump -U odoo -h localhost --schema-only mydb > schema.sql

# 仅数据
pg_dump -U odoo -h localhost --data-only mydb > data.sql

# 压缩备份
pg_dump -U odoo -h localhost mydb | gzip > backup.sql.gz
```

### 恢复

```bash
# 从 SQL 恢复
psql -U odoo -h localhost mydb < backup.sql

# 从压缩恢复
gunzip -c backup.sql.gz | psql -U odoo -h localhost mydb
```

---

## 常见查询模式

### JOIN 查询

```sql
-- 订单 + 客户信息
SELECT 
    so.name AS order_name,
    so.amount_total,
    rp.name AS customer_name,
    rp.email
FROM sale_order so
JOIN res_partner rp ON so.partner_id = rp.id
WHERE so.state = 'sale';
```

### 聚合查询

```sql
-- 按客户汇总
SELECT 
    rp.name AS customer,
    COUNT(so.id) AS order_count,
    SUM(so.amount_total) AS total_amount
FROM sale_order so
JOIN res_partner rp ON so.partner_id = rp.id
WHERE so.state = 'sale'
GROUP BY rp.name
ORDER BY total_amount DESC;
```

### 子查询

```sql
-- 查找金额高于平均的订单
SELECT * FROM sale_order 
WHERE amount_total > (
    SELECT AVG(amount_total) 
    FROM sale_order 
    WHERE state = 'sale'
);
```

---

*参考：PostgreSQL 官方文档，Odoo ORM 源码*
