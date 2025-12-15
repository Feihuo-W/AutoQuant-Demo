#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 回测引擎
"""

from typing import List, Optional
from strategy.base import BaseStrategy
from execution.base import ExecutionEngine
from types_def import Bar, Signal, Direction


class BacktestEngine:
    """
    回测引擎类
    用于运行策略回测并计算收益
    """
    
    def __init__(self, strategy: BaseStrategy, data: List[Bar], execution_engine: ExecutionEngine):
        """
        初始化回测引擎
        
        Args:
            strategy: 策略实例
            data: K线数据列表
            execution_engine: 执行引擎实例
        """
        self.strategy = strategy
        self.data = data
        self.execution_engine = execution_engine
        self.signals: List[Signal] = []
        
        # 回测参数
        self.initial_capital = 100000.0  # 初始资金
        self.current_capital = self.initial_capital  # 当前资金
        self.position = 0.0  # 当前持仓数量
        self.current_direction: Optional[Direction] = None  # 当前持仓方向
        
    def run(self) -> List[float]:
        """
        运行回测
        
        Returns:
            List[float]: 每日资金余额列表
        """
        print(f"开始回测...")
        print(f"初始资金: {self.initial_capital}")
        print(f"总K线数量: {len(self.data)}")
        
        # 记录每日资金余额
        daily_equity = []
        
        # 遍历每一根K线
        for bar in self.data:
            # 调用策略的on_bar方法获取信号
            signal = self.strategy.on_bar(bar)
            
            # 如果有信号，记录并处理
            if signal:
                self.signals.append(signal)
                self._execute_signal(signal, bar.close)
            
            # 计算当前总资产（现金 + 持仓价值）
            current_equity = self.current_capital
            if self.position != 0:
                current_equity += self.position * bar.close
            
            # 记录每日资金余额
            daily_equity.append(current_equity)
        
        # 计算最终收益
        # 确保current_capital始终为正数
        self.current_capital = max(self.current_capital, 0.0)
        
        # 正确计算最终价值
        final_value = self.current_capital
        if self.position != 0 and len(self.data) > 0:
            final_price = self.data[-1].close
            
            if self.current_direction == Direction.LONG:
                # 多头持仓：持仓价值 = 持仓数量 * 收盘价
                position_value = self.position * final_price
                final_value += position_value
            elif self.current_direction == Direction.SHORT:
                # 空头持仓：
                # 1. 我们已经收到了卖空的资金 (包含在current_capital中)
                # 2. 需要计算：(卖空价格 - 最终收盘价) * 持仓数量 = 空头利润
                # 3. 最终价值 = 现有资金 + 空头利润
                short_profit = (self.entry_price - final_price) * abs(self.position)
                final_value += short_profit
        
        # 确保final_value不会为负数
        final_value = max(final_value, 0.0)
        
        total_trades = len(self.signals)
        return_rate = (final_value - self.initial_capital) / self.initial_capital * 100
        
        # 打印回测结果
        print(f"\n回测结果:")
        print(f"总交易次数: {total_trades}")
        print(f"最终资金余额: {final_value:.2f}")
        print(f"收益率: {return_rate:.2f}%")
        
        return daily_equity
    
    def _execute_signal(self, signal: Signal, price: float) -> None:
        """
        执行交易信号
        
        Args:
            signal: 交易信号
            price: 交易价格
        """
        # 确保价格有效
        if price <= 0:
            print(f"{signal.timestamp} - 无效价格: {price}，跳过交易")
            return
        
        # 确保current_capital始终为正数
        self.current_capital = max(self.current_capital, 0.0)
        
        # 添加缺失的entry_price属性
        if not hasattr(self, 'entry_price'):
            self.entry_price = 0.0
        
        print(f"\n===== 交易执行开始 =====")
        print(f"当前状态: 资金={self.current_capital:.2f}, 持仓={self.position:.4f}, 方向={self.current_direction}")
        print(f"收到信号: {signal.direction.value} @ {price}")
        
        # 处理交易信号
        if signal.direction == Direction.LONG:
            if self.current_direction == Direction.SHORT:
                # 平仓空头：买入资产归还
                close_quantity = abs(self.position)  # 空头持仓为负数，取绝对值确保正数
                
                # 计算所需资金
                required_capital = close_quantity * price
                print(f"平仓空头需要资金: {required_capital:.2f}, 当前资金: {self.current_capital:.2f}")
                
                # 确保有足够资金平仓
                if required_capital > self.current_capital:
                    print(f"{signal.timestamp} - 资金不足，无法平仓空头")
                    return
                
                # 使用执行引擎执行平仓订单（数量始终为正）
                order = self.execution_engine.execute_order(signal, close_quantity)
                if order and order.status.value == "filled":
                    # 空头平仓：
                    # 1. 支付资金购买资产归还
                    self.current_capital -= required_capital
                    # 2. 计算利润（卖价 - 买价）* 数量
                    profit = close_quantity * (self.entry_price - price)
                    # 3. 添加利润到资金
                    self.current_capital += profit
                    # 4. 清空持仓
                    self.position = 0.0
                    self.current_direction = None
                    print(f"{signal.timestamp} - 平仓空头！ 卖价: {self.entry_price}, 现价: {price}, 利润: {profit:.2f}")
            elif self.current_direction is None:
                # 开仓多头：买入资产
                # 计算可购买的数量，确保不超过当前资金
                quantity = self.current_capital / price
                # 确保数量为正数
                quantity = max(quantity, 0.0)
                
                if quantity <= 0:
                    print(f"{signal.timestamp} - 资金不足，无法开仓多头")
                    return
                
                # 计算所需资金
                required_capital = quantity * price
                print(f"开仓多头需要资金: {required_capital:.2f}, 当前资金: {self.current_capital:.2f}")
                
                # 使用执行引擎执行开仓订单（数量始终为正）
                order = self.execution_engine.execute_order(signal, quantity)
                if order and order.status.value == "filled":
                    # 开仓多头：
                    # 1. 支付资金购买资产
                    self.current_capital -= required_capital
                    # 2. 更新持仓（正数表示多头）
                    self.position = quantity
                    self.current_direction = Direction.LONG
                    self.entry_price = price
                    print(f"{signal.timestamp} - 开仓多头！ 价格: {price}, 数量: {quantity:.4f}")
        
        elif signal.direction == Direction.SHORT:
            if self.current_direction == Direction.LONG:
                # 平仓多头：卖出资产
                close_quantity = self.position  # 多头持仓为正数
                
                # 使用执行引擎执行平仓订单（数量始终为正）
                order = self.execution_engine.execute_order(signal, close_quantity)
                if order and order.status.value == "filled":
                    # 平仓多头：
                    # 1. 卖出资产获得资金
                    proceeds = close_quantity * price
                    # 2. 添加资金
                    self.current_capital += proceeds
                    # 3. 清空持仓
                    self.position = 0.0
                    self.current_direction = None
                    # 4. 计算利润（现价 - 买价）* 数量
                    profit = close_quantity * (price - self.entry_price)
                    print(f"{signal.timestamp} - 平仓多头！ 买价: {self.entry_price}, 现价: {price}, 利润: {profit:.2f}")
            elif self.current_direction is None:
                # 开仓空头：卖出资产（卖空）
                # 计算可卖空的数量，确保不超过当前资金的保证金（1倍杠杆）
                quantity = self.current_capital / price
                # 确保数量为正数
                quantity = max(quantity, 0.0)
                
                if quantity <= 0:
                    print(f"{signal.timestamp} - 资金不足，无法开仓空头")
                    return
                
                # 使用执行引擎执行开仓订单（数量始终为正）
                order = self.execution_engine.execute_order(signal, quantity)
                if order and order.status.value == "filled":
                    # 开仓空头：
                    # 1. 卖出资产获得资金
                    proceeds = quantity * price
                    # 2. 添加资金
                    self.current_capital += proceeds
                    # 3. 更新持仓（负数表示空头）
                    self.position = -quantity
                    self.current_direction = Direction.SHORT
                    self.entry_price = price
                    print(f"{signal.timestamp} - 开仓空头！ 价格: {price}, 数量: {quantity:.4f}")
        
        # 确保current_capital始终为正数
        self.current_capital = max(self.current_capital, 0.0)
        
        # 确保position计算正确
        if abs(self.position) < 0.0001:  # 防止微小持仓
            self.position = 0.0
            self.current_direction = None
        
        print(f"执行后状态: 资金={self.current_capital:.2f}, 持仓={self.position:.4f}, 方向={self.current_direction}")
        print(f"===== 交易执行结束 =====")
        
        print(f"{signal.timestamp} - 执行信号: {signal.direction.value} @ {price}")
