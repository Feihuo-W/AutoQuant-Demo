#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 结果可视化模块
"""

import matplotlib.pyplot as plt
from typing import List
from types_def import Bar, Signal, Direction


def plot_results(bars: List[Bar], signals: List[Signal], equity_curve: List[float]) -> None:
    """
    绘制回测结果
    
    Args:
        bars: K线数据列表
        signals: 交易信号列表
        equity_curve: 资金曲线列表
    """
    # 创建包含 2 个子图的画布
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
    
    # 准备数据
    dates = [bar.timestamp for bar in bars]
    close_prices = [bar.close for bar in bars]
    
    # 图1: 价格与信号
    ax1.plot(dates, close_prices, label='Close Price', color='blue', linewidth=1)
    
    # 绘制交易信号
    for signal in signals:
        # 找到信号对应的日期索引
        signal_date = signal.timestamp
        try:
            idx = dates.index(signal_date)
            price = close_prices[idx]
            
            if signal.direction == Direction.LONG:
                # 绿色向上三角形 - 买入标记
                ax1.plot(signal_date, price, 'g^', markersize=8, label='Buy Signal')
            else:
                # 红色向下三角形 - 卖出标记
                ax1.plot(signal_date, price, 'rv', markersize=8, label='Sell Signal')
        except ValueError:
            # 如果信号日期不在K线数据中，跳过
            continue
    
    # 添加图例和标题
    ax1.set_title('Price & Signals')
    ax1.set_ylabel('Price (USD)')
    ax1.grid(True)
    
    # 移除重复的图例
    handles, labels = ax1.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax1.legend(by_label.values(), by_label.keys())
    
    # 图2: 资金曲线
    ax2.plot(dates, equity_curve, label='Equity Curve', color='green', linewidth=1)
    ax2.set_title('Account Equity')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Equity (USD)')
    ax2.grid(True)
    ax2.legend()
    
    # 优化布局
    plt.tight_layout()
    
    # 显示图表
    plt.show()
