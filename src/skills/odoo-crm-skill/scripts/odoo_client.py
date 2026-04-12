#!/usr/bin/env python3
"""
Odoo API Client

Odoo XML-RPC API 客户端封装，提供统一的认证和调用接口。
"""

import json
import requests
from typing import Any, Dict, List, Optional
from pathlib import Path


class OdooClient:
    """Odoo API 客户端"""
    
    def __init__(
        self,
        url: str,
        database: str,
        username: str,
        password: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30
    ):
        """
        初始化 Odoo 客户端
        
        Args:
            url: Odoo 实例 URL (如：https://company.odoo.com)
            database: 数据库名称
            username: 用户名
            password: 密码（与 api_key 二选一）
            api_key: API Key（与 password 二选一）
            timeout: 请求超时时间（秒）
        """
        self.url = url.rstrip('/')
        self.database = database
        self.username = username
        self.password = password or api_key
        self.timeout = timeout
        self.uid = None
        
        # 自动认证
        self._authenticate()
    
    def _authenticate(self):
        """执行认证，获取用户 ID"""
        common_url = f"{self.url}/jsonrpc"
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self.database, self.username, self.password]
            },
            "id": 1
        }
        
        response = requests.post(common_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        result = response.json()
        
        if "error" in result:
            raise Exception(f"认证失败：{result['error'].get('message', 'Unknown error')}")
        
        self.uid = result.get("result")
        
        if not self.uid:
            raise Exception("认证失败：未返回用户 ID")
    
    def execute(
        self,
        model: str,
        method: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        执行 Odoo 模型方法
        
        Args:
            model: 模型名称 (如：crm.lead, res.partner)
            method: 方法名称 (如：create, read, write, unlink)
            args: 位置参数列表
            kwargs: 关键字参数字典
            
        Returns:
            方法执行结果
        """
        endpoint_url = f"{self.url}/jsonrpc"
        
        params = {
            "service": "object",
            "method": "execute_kw",
            "args": [
                self.database,
                self.uid,
                self.password,
                model,
                method
            ]
        }
        
        if args:
            params["args"].extend(args)
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": params,
            "id": 1
        }
        
        response = requests.post(endpoint_url, json=payload, timeout=self.timeout)
        response.raise_for_status()
        
        result = response.json()
        
        if "error" in result:
            error = result["error"]
            raise Exception(f"API 调用失败：{error.get('message', 'Unknown error')}")
        
        return result.get("result")
    
    # ========== 便捷方法 ==========
    
    def create(self, model: str, values: Dict[str, Any]) -> int:
        """创建记录"""
        return self.execute(model, "create", [values])
    
    def read(self, model: str, ids: List[int], fields: Optional[List[str]] = None) -> List[Dict]:
        """读取记录"""
        kwargs = {"fields": fields} if fields else {}
        return self.execute(model, "read", [ids], kwargs)
    
    def search(self, model: str, domain: List, limit: Optional[int] = None) -> List[int]:
        """搜索记录 ID"""
        kwargs = {"limit": limit} if limit else {}
        return self.execute(model, "search", [domain], kwargs)
    
    def search_read(
        self,
        model: str,
        domain: List,
        fields: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        order: Optional[str] = None
    ) -> List[Dict]:
        """搜索并读取记录"""
        kwargs = {}
        if fields:
            kwargs["fields"] = fields
        if limit:
            kwargs["limit"] = limit
        if offset:
            kwargs["offset"] = offset
        if order:
            kwargs["order"] = order
        
        return self.execute(model, "search_read", [domain], kwargs)
    
    def write(self, model: str, ids: List[int], values: Dict[str, Any]) -> bool:
        """更新记录"""
        return self.execute(model, "write", [ids, values])
    
    def unlink(self, model: str, ids: List[int]) -> bool:
        """删除记录"""
        return self.execute(model, "unlink", [ids])
    
    def fields_get(self, model: str) -> Dict:
        """获取模型字段定义"""
        return self.execute(model, "fields_get")
    
    def get_version(self) -> str:
        """获取 Odoo 版本"""
        return self.execute("ir.http", "version")


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径，默认 ~/.openclaw/odoo-config.json
        
    Returns:
        配置字典
    """
    if not config_path:
        config_path = str(Path.home() / ".openclaw" / "odoo-config.json")
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        # 尝试从环境变量读取
        return {
            "url": getenv("ODOO_URL", ""),
            "database": getenv("ODOO_DB", ""),
            "username": getenv("ODOO_USERNAME", ""),
            "api_key": getenv("ODOO_API_KEY", ""),
            "timeout": int(getenv("ODOO_TIMEOUT", "30"))
        }
    
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_client(config_path: Optional[str] = None) -> OdooClient:
    """
    创建 Odoo 客户端实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        OdooClient 实例
    """
    config = load_config(config_path)
    
    return OdooClient(
        url=config["url"],
        database=config["database"],
        username=config["username"],
        api_key=config.get("api_key"),
        password=config.get("password"),
        timeout=config.get("timeout", 30)
    )


# 环境变量辅助函数
def getenv(name: str, default: str = "") -> str:
    """安全获取环境变量"""
    import os
    return os.environ.get(name, default)


if __name__ == "__main__":
    # 测试连接
    try:
        client = create_client()
        print(f"✅ 连接成功！")
        print(f"   用户 ID: {client.uid}")
        print(f"   用户名：{client.username}")
        
        # 获取版本
        version = client.get_version()
        print(f"   Odoo 版本：{version}")
        
    except Exception as e:
        print(f"❌ 连接失败：{e}")
