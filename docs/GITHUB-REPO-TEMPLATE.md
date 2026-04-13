# GitHub 仓库配置模板

## 1. README.md 模板

```markdown
# Odoo [模块名] Skill

[![CI/CD](https://github.com/your-username/odoo-[module]-skill/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/odoo-[module]-skill/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

OpenClaw Skill for Odoo [模块名] module.

## ✨ 功能特性

- [功能 1]
- [功能 2]
- [功能 3]

## 📦 安装

### 方法 1: Git 克隆

```bash
cd ~/.openclaw/skills/
git clone https://github.com/your-username/odoo-[module]-skill.git [module]-skill
```

### 方法 2: 下载 .skill 文件

```bash
cd ~/.openclaw/skills/
wget https://github.com/your-username/odoo-[module]-skill/releases/latest/download/odoo-[module]-skill.skill
unzip odoo-[module]-skill.skill -d [module]-skill
```

## 🚀 使用

### 基础配置

```bash
export ODOO_URL="https://your-company.odoo.com"
export ODOO_DB="your_database"
export ODOO_API_KEY="your_api_key"
```

### 示例

```bash
# 示例命令 1
[command 1]

# 示例命令 2
[command 2]
```

## 📚 文档

- [SKILL.md](SKILL.md) - 完整使用说明
- [参考资料](references/) - 详细参考文档
- [示例代码](scripts/) - 可运行脚本

## 🧪 测试

```bash
# 运行测试
python -m pytest tests/

# 运行脚本
python scripts/[script].py --help
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

## 📞 支持

如有问题，请提交 Issue 或联系维护者。
```

## 2. LICENSE 模板 (MIT)

```
MIT License

Copyright (c) 2026 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 3. .gitignore 模板

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Environment
.env
.env.local

# Test
.coverage
htmlcov/
.pytest_cache/

# Build
dist/
build/
*.skill
```

## 4. GitHub Issues 模板

### Bug Report

```markdown
**描述问题**
简明扼要地描述问题

**复现步骤**
1. 执行 '...'
2. 看到错误 '...'

**期望行为**
清晰描述期望的行为

**环境信息**
- Odoo 版本：[e.g. 17.0]
- OpenClaw 版本：[e.g. 1.0]
- Python 版本：[e.g. 3.11]

**截图**
如有，添加截图
```

### Feature Request

```markdown
**功能描述**
简明扼要地描述想要的功能

**使用场景**
描述使用场景和解决的问题

**实现建议**
如有，提供实现建议

**替代方案**
描述考虑过的替代方案
```

## 5. Pull Request 模板

```markdown
## 变更类型
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## 变更描述
简要描述变更内容

## 相关 Issue
Fixes #<issue_number>

## 测试
- [ ] 已添加测试
- [ ] 所有测试通过
- [ ] 已手动测试

## 检查清单
- [ ] 代码符合规范
- [ ] 文档已更新
- [ ] 无破坏性变更
```

## 6. 仓库创建命令

```bash
#!/bin/bash
# create-repo.sh

SKILL_NAME=$1
DESCRIPTION=$2

if [ -z "$SKILL_NAME" ]; then
    echo "Usage: $0 <skill-name> <description>"
    exit 1
fi

# Create GitHub repo
gh repo create $SKILL_NAME --public --description "$DESCRIPTION"

# Initialize local git
cd src/skills/$SKILL_NAME
git init
git add .
git commit -m "Initial commit: $SKILL_NAME v1.0.0"
git branch -M main
git remote add origin git@github.com:$(gh config get user)/$SKILL_NAME.git
git push -u origin main

# Add topics
gh repo edit --topics "odoo" "openclaw" "skill" "erp"

echo "✓ Repository created: $SKILL_NAME"
```

---

*模板版本：1.0.0*
*创建时间：2026-04-12*
