# Odoo 调试方法参考

## 日志配置

### odoo.conf 日志配置

```ini
[options]
# 日志级别：debug, info, warn, error, critical
log_level = debug

# 日志处理器
log_handler = :DEBUG

# 可指定模块日志级别
log_handler = odoo.models:DEBUG
log_handler = odoo.addons.my_module:DEBUG
log_handler = werkzeug:WARNING

# 日志文件
logfile = /var/log/odoo/odoo.log

# 数据库日志（SQL 查询）
log_db = True
log_db_level = warning
```

### Python 日志代码

```python
import logging
_logger = logging.getLogger(__name__)

class MyModel(models.Model):
    _name = 'my.model'

    def my_method(self):
        _logger.info("Processing record %s, amount=%s", self.name, self.amount)
        _logger.debug("Debug info: state=%s", self.state)
        _logger.warning("Warning: low stock for %s", self.name)
        _logger.error("Error: failed to process %s", self.name)

        # 异常日志
        try:
            result = do_something()
        except Exception as e:
            _logger.exception("Exception occurred: %s", str(e))
            raise
```

### 命令行指定日志级别

```bash
# 启动并指定日志
odoo-bin -d testdb --log-level=debug

# 指定日志文件
odoo-bin -d testdb --logfile=/var/log/odoo/odoo.log

# 仅显示 SQL 日志
odoo-bin -d testdb --log-db-level=debug

# Docker
docker run odoo:19.0 odoo-bin -d testdb --log-level=debug
```

### 查看日志

```bash
# Docker 日志
docker logs -f odoo
docker logs --tail 100 odoo

# 过滤特定模块
docker logs odoo 2>&1 | grep my_module
docker logs odoo 2>&1 | grep -E "(ERROR|Exception)"

# 实时过滤
docker logs -f odoo 2>&1 | grep --line-buffered my_model

# 查看日志文件
docker exec odoo tail -f /var/log/odoo/odoo.log
```

## 开发者模式

### 启用方式

1. **UI 方式**：Settings → General Settings → Developer Mode
2. **URL 方式**：
   - `http://localhost:8069/web?debug=1`
   - `http://localhost:8069/web?debug=assets`（未压缩资源）
3. **Cookie 方式**：浏览器控制台执行 `document.cookie = 'debug=1'`

### 开发者模式功能

- 查看视图结构（View → View Metadata）
- 查看字段详情（View → Fields View Get）
- 访问技术菜单（Settings → Technical）
- 调试工作流（Workflow → Instances）
- 查看 SQL 查询（Settings → Database Structure）
- 触发自动重载（修改代码后自动生效）

## pdb 断点调试

### 基本使用

```python
import pdb

class MyModel(models.Model):
    _name = 'my.model'

    def my_method(self):
        pdb.set_trace()  # 执行到这里会暂停
        result = self.do_something()
        return result
```

### 启动后调试

```bash
# 启动 Odoo
odoo-bin -d testdb

# 终端会进入 pdb
(Pdb) n   # next line
(Pdb) s   # step into
(Pdb) c   # continue
(Pdb) p variable_name  # print variable
(Pdb) l   # list code
(Pdb) w   # stack trace
(Pdb) q   # quit
```

### Remote pdb（远程调试）

```python
import rpdb
rpdb.set_trace()
```

### ipdb（增强版 pdb）

```bash
pip install ipdb
```

```python
import ipdb
ipdb.set_trace()
```

## 数据库直接调试

### 连接 PostgreSQL

```bash
# Docker 环境
docker exec -it odoo-db psql -U odoo -d postgres

# 本地环境
psql -U odoo -d postgres -h localhost -p 5432
```

### 常用 SQL

```sql
-- 查看所有表
\dt

-- 查看模块相关表
\dt res_partner
\dt my_model

-- 查看记录
SELECT id, name, amount, state FROM my_model;

-- 查看字段定义
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'my_model';

-- 查看最近创建的记录
SELECT * FROM my_model ORDER BY create_date DESC LIMIT 10;

-- 查看访问日志（谁修改了什么）
SELECT * FROM ir.model.data WHERE name LIKE '%my_model%';

-- 查看日志（ir.logging）
SELECT * FROM ir.logging WHERE name = 'my.model' ORDER BY create_date DESC;

-- 查看 SQL 正在执行
SELECT pid, query, state FROM pg_stat_activity WHERE datname = 'postgres';

-- 杀掉长时间运行的查询
SELECT pg_cancel_backend(pid);
```

### 常用 psql 命令

```sql
\dt          -- 列出所有表
\d table     -- 查看表结构
\du          -- 列出所有用户
\di          -- 列出所有索引
\l           -- 列出所有数据库
\c dbname    -- 切换数据库
\x           -- 格式化输出
\watch       -- 定时刷新
\q           -- 退出
```

## 开发模式 `--dev`

```bash
# 启用所有开发功能
odoo-bin -d testdb --dev=all

# 单独启用
odoo-bin -d testdb --dev=reload    # Python 修改自动重载
odoo-bin -d testdb --dev=xml       # XML 视图修改自动重载
odoo-bin -d testdb --dev=qweb     # QWeb 修改热重载
odoo-bin -d testdb --dev=pdb       # pdb 断点启用
```

### dev 选项详解

| 选项 | 功能 |
|------|------|
| `reload` | 检测 Python 文件变化自动重载 |
| `xml` | 检测 XML 视图变化自动重载 |
| `qweb` | 检测 QWeb 模板变化热重载 |
| `pdb` | 启用 pdb 断点调试 |
| `none` | 禁用所有开发功能 |

## 常见报错排查

### 模块不显示

```bash
# 检查模块是否被识别
docker logs odoo | grep "my_module"

# 手动更新应用列表
docker exec odoo odoo-bin -u base -d testdb

# 检查 __manifest__.py 语法
python3 -c "import ast; ast.parse(open('my_module/__manifest__.py').read())"
```

### 视图报错

```bash
# 检查 XML 语法
docker logs odoo | grep "my_model"

# 验证 XML
python3 -c "import xml.etree.ElementTree as ET; ET.parse('views/my_model.xml')"

# 清除缓存
docker exec odoo odoo-bin -d testdb --stop-after-init
```

### 数据库迁移失败

```sql
-- 检查迁移状态
SELECT name, state FROM ir_module_module WHERE name = 'my_module';

-- 查看迁移日志
SELECT * FROM ir_attachment WHERE name LIKE '%migration%';
```

### 权限错误

```sql
-- 检查用户权限
SELECT * FROM res_users WHERE login = 'myuser';
SELECT * FROM res_groups WHERE name = 'My Group';

-- 检查访问控制
SELECT * FROM ir_model_access WHERE model_id = (SELECT id FROM ir_model WHERE model = 'my.model');
```

### 性能问题

```sql
-- 查找慢查询
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND duration > interval '5 seconds';

-- 查看锁
SELECT * FROM pg_locks WHERE not granted;

-- 查看索引使用
SELECT indexrelname, idx_scan, idx_tup_read
FROM pg_stat_user_indexes
WHERE schemaname = 'public';
```

## PyCharm/VS Code 调试配置

### VS Code

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Odoo: Debug",
            "type": "python",
            "request": "launch",
            "program": "/usr/bin/odoo-bin",
            "args": ["-d", "testdb", "--dev=all"],
            "env": {
                "PYTHONPATH": "/mnt/extra-addons"
            }
        },
        {
            "name": "Odoo: Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 8888
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/mnt/extra-addons"
                }
            ]
        }
    ]
}
```

### PyCharm

```
Configuration:
  Script: /usr/bin/odoo-bin
  Parameters: -d testdb --dev=all
  Environment: PYTHONPATH=/mnt/extra-addons
  Working directory: /
```

## 常用调试技巧

1. **print 调试**：在代码中添加 `print(self.name)` 简单输出
2. **raise Exception**：在可疑处抛出异常，查看调用栈
3. **取消自动重载**：调试时禁用 `--dev=reload` 避免干扰
4. **单用户模式**：使用 `--no-database` 或 `-d` 限制影响范围
5. **清洁环境**：测试前创建新数据库 `docker exec odoo-db createdb testdb2`
