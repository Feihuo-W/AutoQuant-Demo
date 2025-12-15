#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 执行引擎基类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict
from types_def import Signal, OrderStatus, Direction


class Order:
    """
    订单类
    """
    def __init__(self,
                 order_id: str,
                 symbol: str,
                 direction: Direction,
                 price: float,
                 quantity: float,
                 status: OrderStatus = OrderStatus.CREATED):
        """
        初始化订单
        
        Args:
            order_id: 订单ID
            symbol: 交易对
            direction: 交易方向
            price: 订单价格
            quantity: 订单数量
            status: 订单状态，默认为 CREATED
        """
        self.order_id = order_id
        self.symbol = symbol
        self.direction = direction
        self.price = price
        self.quantity = quantity
        self.status = status


class ExecutionEngine(ABC):
    """
    执行引擎抽象基类
    """
    
    def __init__(self):
        """
        初始化执行引擎
        """
        self.orders: Dict[str, Order] = {}  # 订单字典，key为order_id
    
    @abstractmethod
    def execute_order(self, signal: Signal, quantity: float) -> Optional[Order]:
        """
        执行订单
        
        Args:
            signal: 交易信号
            quantity: 交易数量
            
        Returns:
            Optional[Order]: 创建的订单，如果执行失败则返回None
        """
        pass
    
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """
        获取订单状态
        
        Args:
            order_id: 订单ID
            
        Returns:
            Optional[OrderStatus]: 订单状态，如果订单不存在则返回None
        """
        order = self.orders.get(order_id)
        return order.status if order else None
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        获取订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            Optional[Order]: 订单对象，如果订单不存在则返回None
        """
        return self.orders.get(order_id)
