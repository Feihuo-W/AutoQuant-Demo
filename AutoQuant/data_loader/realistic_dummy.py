#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 真实模拟数据生成器
模拟 2023 年 BTC-USD 的价格走势
"""

from datetime import datetime, timedelta
from typing import List
import numpy as np
from types_def import Bar


def generate_realistic_btc_data(start_date: str = "2023-01-01", end_date: str = "2023-12-31", seed: int = 42) -> List[Bar]:
    """
    生成模拟 2023 年 BTC-USD 价格走势的数据
    
    Args:
        start_date: 开始日期，格式为 "YYYY-MM-DD"
        end_date: 结束日期，格式为 "YYYY-MM-DD"
        seed: 随机种子，用于生成可重复的数据
        
    Returns:
        List[Bar]: K线数据列表
    """
    print(f"生成模拟 BTC-USD 从 {start_date} 到 {end_date} 的数据...")
    
    # 设置随机种子，确保数据可重复
    np.random.seed(seed)
    
    # 转换日期格式
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days + 1
    
    # 2023 年 BTC-USD 的实际价格范围和波动特性
    initial_price = 16500.0  # 2023-01-01 的实际开盘价约为 16,500 美元
    
    # 创建日期序列
    dates = [start + timedelta(days=i) for i in range(days)]
    
    # 生成模拟价格序列（使用随机游走模型，添加趋势和波动性）
    prices = [initial_price]
    
    for _ in range(1, days):
        # 基础波动（-2% 到 +2%）
        base_change = np.random.uniform(-0.02, 0.02)
        
        # 趋势项（2023 年整体呈上升趋势，全年涨幅约 160%）
        # 模拟一个逐渐上升的趋势
        trend = 0.0015  # 每天平均上涨 0.15%
        
        # 波动率调整（模拟真实市场的波动率变化）
        volatility = np.random.uniform(0.5, 1.5)
        
        # 计算当天价格变化
        change = (base_change * volatility) + trend
        new_price = prices[-1] * (1 + change)
        
        # 确保价格为正数
        new_price = max(new_price, 0.01)
        
        prices.append(new_price)
    
    # 生成 K 线数据
    bars = []
    
    for i, date in enumerate(dates):
        current_price = prices[i]
        
        # 生成日内波动
        open_price = current_price
        
        # 日内最高价和最低价（波动范围 -1% 到 +1%）
        high_price = open_price * (1 + np.random.uniform(0, 0.01))
        low_price = open_price * (1 - np.random.uniform(0, 0.01))
        
        # 收盘价（在开盘价附近波动 -0.5% 到 +0.5%）
        close_price = open_price * (1 + np.random.uniform(-0.005, 0.005))
        
        # 生成成交量（随机范围，模拟真实市场的成交量分布）
        volume = np.random.uniform(1000000000, 5000000000)  # 10亿到50亿美元的日成交量
        
        # 创建 Bar 对象
        bar = Bar(
            symbol="BTC-USD",
            timestamp=date,
            open=round(open_price, 2),
            high=round(high_price, 2),
            low=round(low_price, 2),
            close=round(close_price, 2),
            volume=round(volume, 2)
        )
        
        bars.append(bar)
    
    print(f"成功生成 {len(bars)} 条 BTC-USD 模拟数据")
    return bars
