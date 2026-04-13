# Odoo Docker 部署参考

## 开发环境 docker-compose.yml

```yaml
version: '3.8'

services:
  odoo:
    image: odoo:19.0
    container_name: odoo-dev
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8069:8069"    # Web 界面
      - "8888:8888"    # 调试端口（可选）
    volumes:
      - ./custom-addons:/mnt/extra-addons:ro
      - odoo-web-data:/var/lib/odoo
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    command: --dev=reload
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:16
    container_name: odoo-db
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  odoo-web-data:
  postgres-data:
```

## 生产环境 docker-compose.yml

```yaml
version: '3.8'

services:
  odoo:
    image: odoo:19.0
    container_name: odoo-prod
    restart: always
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "127.0.0.1:8069:8069"
    volumes:
      - ./custom-addons:/mnt/extra-addons:ro
      - odoo-web-data:/var/lib/odoo
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=${DB_PASSWORD}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8069/web/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  db:
    image: postgres:16
    container_name: odoo-db
    restart: always
    environment:
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=postgres
      - PGDATA=/var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  odoo-web-data:
  postgres-data:
```

## 环境变量说明

### Odoo 容器

| 变量 | 说明 | 默认值 |
|------|------|-------|
| `HOST` | PostgreSQL 主机 | db |
| `PORT` | PostgreSQL 端口 | 5432 |
| `USER` | PostgreSQL 用户 | odoo |
| `PASSWORD` | PostgreSQL 密码 | odoo |
| `DB_FILTER` | 数据库过滤正则 | `^%d$` |
| `ADDONS_PATH` | 附加模块路径 | 已有 + /mnt/extra-addons |
| `ADMIN_PASSWORD` | 管理员密码 | admin |

### PostgreSQL 容器

| 变量 | 说明 | 默认值 |
|------|------|-------|
| `POSTGRES_DB` | 默认数据库 | postgres |
| `POSTGRES_USER` | 数据库用户 | odoo |
| `POSTGRES_PASSWORD` | 数据库密码 | odoo |
| `PGDATA` | 数据目录 | /var/lib/postgresql/data/pgdata |

## odoo.conf 配置

### 开发配置（odoo.conf）

```ini
[options]
; 管理员
admin_passwd = admin

; 数据库
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
dbfilter = ^%d$

; 模块路径
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons

; 日志
log_level = debug
log_handler = :DEBUG
logfile = /var/log/odoo/odoo.log

; 开发模式
dev = reload,xml

; 安全
list_db = True
```

### 生产配置（odoo.conf）

```ini
[options]
; 管理员
admin_passwd = ${ADMIN_PASSWORD}

; 数据库
db_host = db
db_port = 5432
db_user = odoo
db_password = ${DB_PASSWORD}
dbfilter = ^%d$

; 模块路径
addons_path = /mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons

; 日志
log_level = warn
log_handler = :WARNING
logfile = /var/log/odoo/odoo.log

; 性能
workers = 9
max_cron_threads = 1
limit_memory_soft = 2048
limit_memory_hard = 3072
limit_time_cpu = 60
limit_time_real = 120
limit_request = 65536

; 安全
list_db = False
proxy_mode = True
```

## 卷挂载说明

```yaml
volumes:
  # 自定义模块（代码开发）
  - ./custom-addons:/mnt/extra-addons:ro

  # Odoo 运行时数据（filestore, sessions）
  - odoo-web-data:/var/lib/odoo

  # 自定义配置文件
  - ./odoo.conf:/etc/odoo/odoo.conf:ro

  # 可选：日志目录
  - ./logs:/var/log/odoo

  # 可选：自定义 Python 库
  - ./python-packages:/usr/local/lib/python3.10/dist-packages:ro
```

## 常用 Docker 命令

### 启动与停止

```bash
# 启动开发环境
docker compose up -d

# 启动并实时查看日志
docker compose up

# 停止服务
docker compose down

# 停止并删除卷（重置）
docker compose down -v

# 重启服务
docker compose restart
docker compose restart odoo
```

### 进入容器

```bash
# 进入 Odoo 容器
docker exec -it odoo bash

# 进入 PostgreSQL 容器
docker exec -it odoo-db psql -U odoo -d postgres
```

### 模块操作

```bash
# 安装模块
docker exec odoo odoo-bin -i my_module -d testdb

# 升级模块
docker exec odoo odoo-bin -u my_module -d testdb

# 卸载模块
docker exec odoo odoo-bin -i my_module -d testdb --uninstall

# 更新应用列表
docker exec odoo odoo-bin -u base -d testdb
```

### 日志查看

```bash
# 查看 Odoo 日志
docker logs -f odoo

# 过滤模块日志
docker logs odoo | grep my_module

# 查看最近 100 行
docker logs --tail 100 odoo

# 查看错误
docker logs odoo 2>&1 | grep -i error
```

### 数据库操作

```bash
# 备份数据库
docker exec odoo-db pg_dump -U odoo -Fc mydb > backup_$(date +%Y%m%d).dump

# 恢复数据库
docker exec -i odoo-db pg_restore -U odoo -d mydb < backup_20260412.dump

# 创建数据库
docker exec odoo-db psql -U odoo -c "CREATE DATABASE mydb;"

# 列出数据库
docker exec odoo-db psql -U odoo -c "\l"
```

### 备份与恢复

```bash
# 备份所有数据
docker run --rm \
  -v odoo-db-data:/source:ro \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/db_$(date +%Y%m%d).tar.gz -C /source .

# 备份 filestore
docker run --rm \
  -v odoo-web-data:/source:ro \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/filestore_$(date +%Y%m%d).tar.gz -C /source .

# 自动备份脚本
./backup.sh
```

## 开发模式 `--dev`

```bash
# 启用所有开发功能
command: --dev=all

# 单独启用
command: --dev=reload    # Python 修改自动重载
command: --dev=xml       # XML 视图修改自动重载
command: --dev=qweb       # QWeb 模板热重载
command: --dev=pdb        # pdb 断点调试
```

## 带调试的开发配置

### Dockerfile（安装 debugpy）

```dockerfile
FROM odoo:19.0
RUN pip3 install debugpy
```

### 带调试端口的 docker-compose.yml

```yaml
services:
  odoo:
    build: .
    command: >
      python3 -m debugpy --listen 0.0.0.0:8888
      /usr/bin/odoo-bin
    ports:
      - "8069:8069"
      - "8888:8888"
```

### VS Code launch.json

```json
{
    "version": "0.2.0",
    "configurations": [
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

## 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Odoo 重启循环 | db 未就绪 | 添加 `depends_on` + `condition: service_healthy` |
| 连接拒绝 | 端口冲突 | 修改 `ports` 映射 |
| 模块不显示 | addons_path 错误 | 检查 `./custom-addons` 是否正确挂载 |
| 文件权限 | uid 不匹配 | 使用 `:ro` 挂载或调整权限 |
| 内存不足 | workers 过多 | 减少 `workers` 或 `memory` 限制 |
