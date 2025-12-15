#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据集的最终收盘价
"""

from data_loader import generate_realistic_btc_data

# 生成数据
start_date = "2023-01-01"
end_date = "2023-12-31"
data = generate_realistic_btc_data(start_date=start_date, end_date=end_date, seed=42)

# 打印数据信息
print(f"数据数量: {len(data)}")
print(f"开始日期: {data[0].timestamp}")
print(f"结束日期: {data[-1].timestamp}")
print(f"开始开盘价: {data[0].open}")
print(f"结束收盘价: {data[-1].close}")

# 检查最后10天的数据
print("\n最后10天的数据:")
for bar in data[-10:]:
    print(f"{bar.timestamp.date()} - 开盘: {bar.open:.2f}, 收盘: {bar.close:.2f}")
