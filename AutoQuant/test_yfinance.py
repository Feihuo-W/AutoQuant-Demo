#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 yfinance 是否能正常工作
"""

import yfinance as yf

# 简单测试：获取苹果股票数据
symbol = "AAPL"
start_date = "2023-01-01"
end_date = "2023-12-31"

print(f"测试获取 {symbol} 从 {start_date} 到 {end_date} 的数据...")

try:
    # 使用 yfinance 获取数据
    df = yf.download(symbol, start=start_date, end=end_date)
    
    print(f"数据获取成功!")
    print(f"数据形状: {df.shape}")
    print(f"数据头:")
    print(df.head())
    
    # 检查数据是否为空
    if df.empty:
        print("警告: 获取的数据为空!")
    else:
        print("数据非空，获取成功!")
        
except Exception as e:
    print(f"获取数据失败: {e}")
    import traceback
    traceback.print_exc()
