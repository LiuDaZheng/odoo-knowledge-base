"""
Odoo Inventory Client - 库存管理客户端

提供与 Odoo ERP 库存模块的 API 交互功能
"""

import requests
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime, date

logger = logging.getLogger(__name__)


class OdooInventoryClient:
    """Odoo 库存管理客户端"""
    
    def __init__(self, base_url: str, api_key: str, database: str):
        """
        初始化客户端
        
        Args:
            base_url: Odoo 实例 URL (如 https://company.odoo.com)
            api_key: API Key (Bearer Token)
            database: 数据库名称
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.database = database
        self.api_endpoint = f"{self.base_url}/json/2"
        
        self.headers = {
            "Authorization": f"bearer {api_key}",
            "X-Odoo-Database": database,
            "Content-Type": "application/json",
            "User-Agent": "odoo-inventory-skill/0.1.0"
        }
        
        logger.info(f"Initialized OdooInventoryClient for database: {database}")
    
    def _call(self, model: str, method: str, params: Optional[Dict] = None) -> Any:
        """
        调用 Odoo API
        
        Args:
            model: 模型名称 (如 stock.picking)
            method: 方法名称 (如 create, search_read)
            params: 方法参数
            
        Returns:
            API 响应数据
            
        Raises:
            requests.HTTPError: HTTP 请求失败
        """
        url = f"{self.api_endpoint}/{model}/{method}"
        
        payload = params or {}
        
        try:
            logger.debug(f"Calling {url} with params: {payload}")
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Response: {result}")
            return result
        except requests.exceptions.RequestException as e:
            logger.error(f"API call failed: {e}")
            raise
    
    def _search_read(self, model: str, domain: List, fields: Optional[List[str]] = None, 
                     context: Optional[Dict] = None) -> List[Dict]:
        """
        搜索并读取记录
        
        Args:
            model: 模型名称
            domain: 搜索条件 (如 [["product_id", "=", 10]])
            fields: 返回字段列表
            context: 上下文参数
            
        Returns:
            记录列表
        """
        params = {
            "domain": domain,
            "fields": fields or [],
        }
        if context:
            params["context"] = context
            
        return self._call(model, "search_read", params)
    
    # ==================== 库存查询 ====================
    
    def get_stock_quantity(self, product_id: int, location_id: Optional[int] = None) -> Dict:
        """
        查询产品库存数量
        
        Args:
            product_id: 产品 ID
            location_id: 库位 ID (可选，不指定则返回所有库位)
            
        Returns:
            库存信息字典
        """
        domain = [["product_id", "=", product_id]]
        if location_id:
            domain.append(["location_id", "=", location_id])
        
        quants = self._search_read(
            "stock.quant",
            domain,
            fields=["id", "product_id", "location_id", "quantity", "reserved_quantity", "available_quantity"]
        )
        
        total_quantity = sum(q.get("quantity", 0) for q in quants)
        total_reserved = sum(q.get("reserved_quantity", 0) for q in quants)
        
        return {
            "product_id": product_id,
            "location_id": location_id,
            "total_quantity": total_quantity,
            "reserved_quantity": total_reserved,
            "available_quantity": total_quantity - total_reserved,
            "details": quants
        }
    
    def get_available_stock(self, product_id: int) -> int:
        """
        查询产品可用库存 (扣除预留)
        
        Args:
            product_id: 产品 ID
            
        Returns:
            可用库存数量
        """
        stock_info = self.get_stock_quantity(product_id)
        return stock_info["available_quantity"]
    
    def get_product_info(self, product_id: int) -> Dict:
        """
        查询产品信息
        
        Args:
            product_id: 产品 ID
            
        Returns:
            产品信息字典
        """
        products = self._search_read(
            "product.product",
            [["id", "=", product_id]],
            fields=["id", "name", "default_code", "type", "uom_id", "categ_id", "list_price", "standard_price"]
        )
        
        if not products:
            raise ValueError(f"Product {product_id} not found")
        
        return products[0]
    
    def get_stock_moves(self, product_id: int, date_from: Optional[date] = None, 
                       date_to: Optional[date] = None, state: Optional[str] = None) -> List[Dict]:
        """
        查询库存移动历史
        
        Args:
            product_id: 产品 ID
            date_from: 开始日期
            date_to: 结束日期
            state: 移动状态 (draft, confirmed, assigned, done, cancel)
            
        Returns:
            库存移动列表
        """
        domain = [["product_id", "=", product_id]]
        
        if date_from:
            domain.append(["date", ">=", date_from.isoformat()])
        if date_to:
            domain.append(["date", "<=", date_to.isoformat()])
        if state:
            domain.append(["state", "=", state])
        
        return self._search_read(
            "stock.move",
            domain,
            fields=["id", "product_id", "product_uom_qty", "product_uom", "picking_id", 
                   "location_id", "location_dest_id", "state", "date"]
        )
    
    def get_picking_by_origin(self, origin: str) -> List[Dict]:
        """
        根据来源单号查询调拨单
        
        Args:
            origin: 来源单号 (如销售订单号、采购订单号)
            
        Returns:
            调拨单列表
        """
        return self._search_read(
            "stock.picking",
            [["origin", "=", origin]],
            fields=["id", "name", "picking_type_id", "origin", "state", "scheduled_date"]
        )
    
    # ==================== 调拨管理 ====================
    
    def create_incoming_picking(self, partner_id: int, product_lines: List[Dict], 
                               origin: Optional[str] = None, 
                               scheduled_date: Optional[str] = None) -> int:
        """
        创建入库单
        
        Args:
            partner_id: 供应商 ID
            product_lines: 产品列表 [{"product_id": 10, "qty": 100, "uom_id": 1}]
            origin: 来源单号 (如采购订单号)
            scheduled_date: 计划日期
            
        Returns:
            创建的调拨单 ID
        """
        move_lines = []
        for line in product_lines:
            move_lines.append([0, 0, {
                "product_id": line["product_id"],
                "product_uom_qty": line["qty"],
                "product_uom": line.get("uom_id", 1),
                "name": line.get("name", "")
            }])
        
        picking_data = {
            "picking_type_id": 1,  # 入库类型 ID，需要根据实际配置调整
            "partner_id": partner_id,
            "move_lines": move_lines,
            "origin": origin or "",
        }
        
        if scheduled_date:
            picking_data["scheduled_date"] = scheduled_date
        
        result = self._call("stock.picking", "create", picking_data)
        logger.info(f"Created incoming picking: {result}")
        return result
    
    def create_outgoing_picking(self, partner_id: int, product_lines: List[Dict], 
                               origin: Optional[str] = None,
                               scheduled_date: Optional[str] = None) -> int:
        """
        创建出库单
        
        Args:
            partner_id: 客户 ID
            product_lines: 产品列表 [{"product_id": 10, "qty": 50, "uom_id": 1}]
            origin: 来源单号 (如销售订单号)
            scheduled_date: 计划日期
            
        Returns:
            创建的调拨单 ID
        """
        move_lines = []
        for line in product_lines:
            move_lines.append([0, 0, {
                "product_id": line["product_id"],
                "product_uom_qty": line["qty"],
                "product_uom": line.get("uom_id", 1),
                "name": line.get("name", "")
            }])
        
        picking_data = {
            "picking_type_id": 2,  # 出库类型 ID，需要根据实际配置调整
            "partner_id": partner_id,
            "move_lines": move_lines,
            "origin": origin or "",
        }
        
        if scheduled_date:
            picking_data["scheduled_date"] = scheduled_date
        
        result = self._call("stock.picking", "create", picking_data)
        logger.info(f"Created outgoing picking: {result}")
        return result
    
    def create_internal_transfer(self, from_location: int, to_location: int, 
                                product_lines: List[Dict]) -> int:
        """
        创建内部调拨单
        
        Args:
            from_location: 源库位 ID
            to_location: 目标库位 ID
            product_lines: 产品列表 [{"product_id": 10, "qty": 20, "uom_id": 1}]
            
        Returns:
            创建的调拨单 ID
        """
        move_lines = []
        for line in product_lines:
            move_lines.append([0, 0, {
                "product_id": line["product_id"],
                "product_uom_qty": line["qty"],
                "product_uom": line.get("uom_id", 1),
                "name": line.get("name", ""),
                "location_id": from_location,
                "location_dest_id": to_location
            }])
        
        picking_data = {
            "picking_type_id": 3,  # 内部调拨类型 ID
            "move_lines": move_lines,
            "location_id": from_location,
            "location_dest_id": to_location,
        }
        
        result = self._call("stock.picking", "create", picking_data)
        logger.info(f"Created internal transfer: {result}")
        return result
    
    def validate_picking(self, picking_id: int) -> bool:
        """
        验证调拨单 (确认出库/入库)
        
        Args:
            picking_id: 调拨单 ID
            
        Returns:
            是否成功
        """
        try:
            self._call("stock.picking", "button_validate", {"ids": [picking_id]})
            logger.info(f"Validated picking: {picking_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to validate picking {picking_id}: {e}")
            raise
    
    def cancel_picking(self, picking_id: int) -> bool:
        """
        取消调拨单
        
        Args:
            picking_id: 调拨单 ID
            
        Returns:
            是否成功
        """
        try:
            self._call("stock.picking", "action_cancel", {"ids": [picking_id]})
            logger.info(f"Cancelled picking: {picking_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to cancel picking {picking_id}: {e}")
            raise
    
    # ==================== 库存调整 ====================
    
    def create_inventory_adjustment(self, product_id: int, counted_quantity: float, 
                                   location_id: Optional[int] = None,
                                   reason: Optional[str] = None) -> int:
        """
        创建库存调整单
        
        Args:
            product_id: 产品 ID
            counted_quantity: 实际盘点数量
            location_id: 库位 ID
            reason: 调整原因
            
        Returns:
            库存调整单 ID
        """
        # 先查询当前库存
        stock_info = self.get_stock_quantity(product_id, location_id)
        
        adjustment_data = {
            "product_id": product_id,
            "product_uom_qty": counted_quantity,
            "inventory_quantity": counted_quantity,
            "location_id": location_id or stock_info["details"][0]["location_id"] if stock_info["details"] else 1,
        }
        
        if reason:
            adjustment_data["notes"] = reason
        
        result = self._call("stock.quant", "create", adjustment_data)
        logger.info(f"Created inventory adjustment: {result}")
        return result
    
    def create_scrap(self, product_id: int, quantity: float, reason: Optional[str] = None) -> int:
        """
        创建报废单
        
        Args:
            product_id: 产品 ID
            quantity: 报废数量
            reason: 报废原因
            
        Returns:
            报废单 ID
        """
        scrap_data = {
            "product_id": product_id,
            "product_uom_qty": quantity,
            "scrap_qty": quantity,
        }
        
        if reason:
            scrap_data["reason"] = reason
        
        result = self._call("stock.scrap", "create", scrap_data)
        logger.info(f"Created scrap order: {result}")
        return result
    
    # ==================== 工具方法 ====================
    
    def get_picking_types(self) -> List[Dict]:
        """
        获取所有调拨类型
        
        Returns:
            调拨类型列表
        """
        return self._search_read(
            "stock.picking.type",
            [],
            fields=["id", "name", "code", "sequence_id"]
        )
    
    def get_locations(self, usage: Optional[str] = None) -> List[Dict]:
        """
        获取库位列表
        
        Args:
            usage: 库位类型 (supplier, customer, internal, inventory, etc.)
            
        Returns:
            库位列表
        """
        domain = []
        if usage:
            domain.append(["usage", "=", usage])
        
        return self._search_read(
            "stock.location",
            domain,
            fields=["id", "name", "usage", "complete_name"]
        )
    
    def check_stock_availability(self, product_id: int, required_qty: float) -> Dict:
        """
        检查库存是否满足需求
        
        Args:
            product_id: 产品 ID
            required_qty: 需求数量
            
        Returns:
            检查结果 {"available": bool, "available_qty": float, "message": str}
        """
        available_qty = self.get_available_stock(product_id)
        
        if available_qty >= required_qty:
            return {
                "available": True,
                "available_qty": available_qty,
                "message": f"库存充足：可用 {available_qty}, 需求 {required_qty}"
            }
        else:
            shortage = required_qty - available_qty
            return {
                "available": False,
                "available_qty": available_qty,
                "shortage": shortage,
                "message": f"库存不足：可用 {available_qty}, 需求 {required_qty}, 缺口 {shortage}"
            }
