#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 模拟执行引擎
"""

import uuid
from typing import Optional
from .base import ExecutionEngine, Order
from types_def import Signal, OrderStatus


class SimulatedExecution(ExecutionEngine):
    """
    模拟执行引擎
    用于回测环境中的订单执行模拟
    """
    
    def __init__(self):
        """
        初始化模拟执行引擎
        """
        super().__init__()
        self.fee_rate = 0.001  # 手续费率，默认 0.1%
    
    def execute_order(self, signal: Signal, quantity: float) -> Optional[Order]:
        """
        执行订单（模拟）
        
        Args:
            signal: 交易信号
            quantity: 交易数量
            
        Returns:
            Optional[Order]: 创建的订单
        """
        # 生成唯一订单ID
        order_id = str(uuid.uuid4())
        
        # 创建订单
        order = Order(
            order_id=order_id,
            symbol=signal.symbol,
            direction=signal.direction,
            price=signal.price,
            quantity=quantity,
            status=OrderStatus.CREATED
        )
        
        # 模拟订单提交
        order.status = OrderStatus.SUBMITTED
        self.orders[order_id] = order
        
        # 模拟订单成交
        order.status = OrderStatus.FILLED
        
        print(f"模拟执行订单: {order_id} - {order.direction.value} {order.quantity} {order.symbol} @ {order.price}")
        print(f"订单状态: {order.status.value}")
        
        return order
    
    def set_fee_rate(self, fee_rate: float) -> None:
        """
        设置手续费率
        
        Args:
            fee_rate: 手续费率，如 0.001 表示 0.1%
        """
        self.fee_rate = fee_rate
