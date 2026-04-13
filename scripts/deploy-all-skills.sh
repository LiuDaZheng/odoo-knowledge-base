#!/bin/bash
#
# Odoo Skill 批量部署脚本
# 用法：./deploy-all-skills.sh [--github-user <username>]
#

set -e

GITHUB_USER=${1:-$(gh config get user)}
SKILLS_DIR="$HOME/.openclaw/workspace-skilldev/odoo-knowledge-base/src/skills"
TARGET_DIR="$HOME/.openclaw/skills"

echo "=== Odoo Skill 批量部署脚本 ==="
echo "GitHub 用户：$GITHUB_USER"
echo "Skills 目录：$SKILLS_DIR"
echo "目标目录：$TARGET_DIR"
echo

SKILLS=(
    "odoo-accounting-skill:Odoo 财务会计 Skill"
    "odoo-mrp-skill:Odoo 生产制造 Skill"
    "odoo-hr-skill:Odoo 人力资源 Skill"
    "odoo-website-skill:Odoo 网站构建 Skill"
    "odoo-ecommerce-skill:Odoo 电商功能 Skill"
)

for skill_entry in "${SKILLS[@]}"; do
    SKILL_NAME="${skill_entry%%:*}"
    SKILL_DESC="${skill_entry##*:}"
    
    echo "----------------------------------------"
    echo "处理：$SKILL_NAME"
    echo "描述：$SKILL_DESC"
    echo
    
    SKILL_PATH="$SKILLS_DIR/$SKILL_NAME"
    
    if [ ! -d "$SKILL_PATH" ]; then
        echo "⚠️  跳过：目录不存在"
        continue
    fi
    
    # 1. 本地部署
    echo "1. 本地部署..."
    if [ -d "$TARGET_DIR/$SKILL_NAME" ]; then
        echo "  更新现有部署"
        rm -rf "$TARGET_DIR/$SKILL_NAME"
    fi
    cp -r "$SKILL_PATH" "$TARGET_DIR/$SKILL_NAME"
    echo "  ✓ 已部署到 $TARGET_DIR/$SKILL_NAME"
    
    echo
done

echo "========================================"
echo "✓ 批量部署完成!"
echo
echo "已部署的 Skills:"
ls -1 "$TARGET_DIR" | grep odoo- || echo "暂无"
echo
