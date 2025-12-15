#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 数据加载模块
"""

import random
from datetime import datetime, timedelta
from typing import List
from types_def import Bar


def generate_dummy_data(days: int = 100) -> List[Bar]:
    """
    生成模拟 K 线数据
    
    Args:
        days: 生成数据的天数，默认为 100
        
    Returns:
        List[Bar]: K 线数据列表
    """
    bars = []
    base_price = 10000.0
    current_price = base_price
    
    # 从当前日期开始生成数据
    current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for i in range(days):
        # 生成当天的开盘价、最高价、最低价和收盘价
        # 开盘价等于前一天的收盘价
        open_price = current_price
        
        # 生成随机波动范围 (-5% 到 +5%)
        price_change = random.uniform(-0.05, 0.05)
        close_price = open_price * (1 + price_change)
        
        # 生成最高价和最低价，确保最高价 >= 开盘价和收盘价，最低价 <= 开盘价和收盘价
        if open_price > close_price:
            high_price = open_price * (1 + random.uniform(0, 0.03))
            low_price = close_price * (1 - random.uniform(0, 0.03))
        else:
            high_price = close_price * (1 + random.uniform(0, 0.03))
            low_price = open_price * (1 - random.uniform(0, 0.03))
        
        # 生成随机成交量（10000 到 1000000）
        volume = random.uniform(10000, 1000000)
        
        # 创建 Bar 对象
        bar = Bar(
            symbol="BTC/USDT",  # 假设是 BTC/USDT 交易对
            timestamp=current_date,
            open=round(open_price, 2),
            high=round(high_price, 2),
            low=round(low_price, 2),
            close=round(close_price, 2),
            volume=round(volume, 2)
        )
        
        bars.append(bar)
        
        # 更新当前价格和日期
        current_price = close_price
        current_date += timedelta(days=1)
    
    return bars
