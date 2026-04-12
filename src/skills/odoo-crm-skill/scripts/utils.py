#!/usr/bin/env python3
"""
工具函数库

提供通用的辅助函数。
"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Optional


def format_currency(amount: float, currency: str = "CNY") -> str:
    """格式化货币"""
    symbols = {
        "CNY": "¥",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"


def format_date(date_str: Optional[str], format: str = "%Y-%m-%d") -> str:
    """格式化日期"""
    if not date_str:
        return "N/A"
    
    try:
        # 尝试解析 Odoo 日期格式
        if " " in date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime(format)
    except ValueError:
        return date_str


def format_percentage(value: Optional[float]) -> str:
    """格式化百分比"""
    if value is None:
        return "N/A"
    return f"{value:.0f}%"


def truncate_text(text: Optional[str], max_length: int = 50) -> str:
    """截断文本"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def print_table(headers: List[str], rows: List[List[Any]], align: Optional[List[str]] = None):
    """打印表格"""
    if not rows:
        print("无数据")
        return
    
    # 计算列宽
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # 打印表头
    header_line = " | ".join(
        h.ljust(col_widths[i]) if (align and align[i] == 'l') else h.rjust(col_widths[i])
        for i, h in enumerate(headers)
    )
    print(header_line)
    print("-" * len(header_line))
    
    # 打印数据行
    for row in rows:
        row_line = " | ".join(
            str(cell).ljust(col_widths[i]) if (align and align[i] == 'l') else str(cell).rjust(col_widths[i])
            for i, cell in enumerate(row)
        )
        print(row_line)


def print_success(message: str):
    """打印成功消息"""
    print(f"✅ {message}")


def print_error(message: str):
    """打印错误消息"""
    print(f"❌ {message}", file=sys.stderr)


def print_warning(message: str):
    """打印警告消息"""
    print(f"⚠️  {message}")


def print_info(message: str):
    """打印信息消息"""
    print(f"ℹ️  {message}")


def confirm_action(message: str) -> bool:
    """确认操作"""
    response = input(f"{message} (yes/no): ")
    return response.lower() in ["yes", "y"]


if __name__ == "__main__":
    # 测试
    print(format_currency(1234567.89))
    print(format_date("2026-04-12"))
    print(format_percentage(75.5))
    print(truncate_text("这是一个很长的文本，需要被截断", 10))
