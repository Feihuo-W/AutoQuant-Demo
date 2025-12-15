#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 策略基类定义
"""

from abc import ABC, abstractmethod
from typing import Optional
from types_def import Bar, Signal


class BaseStrategy(ABC):
    """
    策略抽象基类
    所有策略必须继承此类并实现 on_bar 方法
    """
    
    @abstractmethod
    def on_bar(self, bar: Bar) -> Optional[Signal]:
        """
        处理一根K线数据并生成交易信号
        
        Args:
            bar: K线数据
            
        Returns:
            Optional[Signal]: 交易信号，如果没有信号则返回 None
        """
        pass
