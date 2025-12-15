#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 核心数据结构定义
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Direction(Enum):
    """交易方向枚举"""
    LONG = "long"
    SHORT = "short"


class OrderStatus(Enum):
    """订单状态枚举"""
    CREATED = "created"
    SUBMITTED = "submitted"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"


@dataclass
class Bar:
    """K线数据类"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    @property
    def value(self) -> float:
        """默认返回收盘价，方便计算"""
        return self.close


@dataclass
class Signal:
    """交易信号数据类"""
    symbol: str
    timestamp: datetime
    direction: Direction
    price: float
