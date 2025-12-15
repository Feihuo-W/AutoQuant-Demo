#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 双均线策略实现
"""

from typing import Optional, List
from .base import BaseStrategy
from types_def import Bar, Signal, Direction


class DoubleMaStrategy(BaseStrategy):
    """
    双均线策略
    当短期均线上穿长期均线时，产生多头信号
    当短期均线下穿长期均线时，产生空头信号
    加入止损机制和RSI过滤，控制风险和避免追高
    """
    
    def __init__(self, short_period: int = 5, long_period: int = 20, stop_loss_pct: float = 0.03, rsi_period: int = 14, rsi_limit: float = 75.0, rsi_low_limit: float = 25.0, trailing_stop_pct: float = 0.05):
        """
        初始化双均线策略
        
        Args:
            short_period: 短期均线周期，默认为 5
            long_period: 长期均线周期，默认为 20
            stop_loss_pct: 止损百分比，默认为 0.03 (3%)
            rsi_period: RSI计算周期，默认为 14
            rsi_limit: RSI上限，高于此值不买入，默认为 75
            rsi_low_limit: RSI下限，低于此值不卖出，默认为 25
            trailing_stop_pct: 跟踪止损百分比，默认为 0.05 (5%)
        """
        self.short_period = short_period
        self.long_period = long_period
        self.stop_loss_pct = stop_loss_pct
        self.trailing_stop_pct = trailing_stop_pct
        self.rsi_period = rsi_period
        self.rsi_limit = rsi_limit
        self.rsi_low_limit = rsi_low_limit
        self.prices: List[float] = []
        
        # 使用EMA替代SMA
        self.last_short_ema: Optional[float] = None
        self.last_long_ema: Optional[float] = None
        
        # 新增：记录买入/卖出价格和持仓状态
        self.entry_price = 0.0
        self.is_holding = False
        self.current_direction: Optional[Direction] = None
        self.highest_price = 0.0  # 用于跟踪止损
        self.lowest_price = float('inf')  # 用于空头跟踪止损
        
        # 用于RSI计算的变量（使用EMA平滑）
        self.rsi_gains: List[float] = []
        self.rsi_losses: List[float] = []
        self.last_avg_gain: Optional[float] = None
        self.last_avg_loss: Optional[float] = None
    
    def calculate_sma(self, prices: List[float], period: int) -> float:
        """
        计算指定周期的简单移动平均线
        
        Args:
            prices: 价格列表
            period: 均线周期
            
        Returns:
            float: 移动平均值
        """
        return sum(prices[-period:]) / period
    
    def calculate_ema(self, prices: List[float], period: int, last_ema: Optional[float] = None) -> float:
        """
        计算指定周期的指数移动平均线
        
        Args:
            prices: 价格列表
            period: 均线周期
            last_ema: 上一期的EMA值，如果没有则使用SMA作为初始值
            
        Returns:
            float: EMA值
        """
        if len(prices) < period:
            return sum(prices) / len(prices)
        
        if last_ema is None:
            # 初始EMA使用SMA
            return self.calculate_sma(prices[-period:], period)
        
        # 计算平滑系数
        multiplier = 2 / (period + 1)
        current_price = prices[-1]
        
        # 计算EMA
        ema = (current_price - last_ema) * multiplier + last_ema
        return ema
    
    def calculate_rsi(self, prices: List[float], period: int) -> float:
        """
        计算指定周期的RSI指标（使用EMA平滑）
        
        Args:
            prices: 价格列表
            period: RSI计算周期
            
        Returns:
            float: RSI值
        """
        # 计算价格变化
        changes = []
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            changes.append(change)
        
        # 检查数据是否足够
        if len(changes) < period:
            return 50.0  # 默认值
        
        # 取最近period+1个变化（因为要计算初始平均值）
        recent_changes = changes[-period:]
        
        if self.last_avg_gain is None or self.last_avg_loss is None:
            # 初始计算使用SMA
            gains = [change for change in recent_changes if change > 0]
            losses = [-change for change in recent_changes if change < 0]
            
            avg_gain = sum(gains) / period if gains else 0.0
            avg_loss = sum(losses) / period if losses else 0.0
        else:
            # 使用EMA平滑
            last_change = recent_changes[-1]
            gain = last_change if last_change > 0 else 0.0
            loss = -last_change if last_change < 0 else 0.0
            
            multiplier = 2 / (period + 1)
            avg_gain = (self.last_avg_gain * (period - 1) + gain) / period
            avg_loss = (self.last_avg_loss * (period - 1) + loss) / period
        
        # 更新上一期的平均值
        self.last_avg_gain = avg_gain
        self.last_avg_loss = avg_loss
        
        # 计算RSI
        if avg_loss == 0:
            rsi = 100.0
        elif avg_gain == 0:
            rsi = 0.0
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def on_bar(self, bar: Bar) -> Optional[Signal]:
        """
        处理一根K线数据并生成交易信号
        
        Args:
            bar: K线数据
            
        Returns:
            Optional[Signal]: 交易信号，如果没有信号则返回 None
        """
        # 添加当前收盘价到价格列表
        self.prices.append(bar.close)
        
        # 检查数据是否足够计算均线
        if len(self.prices) < self.long_period:
            return None
        
        # 计算短期和长期EMA
        short_ema = self.calculate_ema(self.prices, self.short_period, self.last_short_ema)
        long_ema = self.calculate_ema(self.prices, self.long_period, self.last_long_ema)
        
        # 计算RSI
        rsi = self.calculate_rsi(self.prices, self.rsi_period)
        
        signal = None
        current_price = bar.close
        
        # 检查是否持仓
        if self.is_holding:
            # 更新最高价/最低价用于跟踪止损
            if self.current_direction == Direction.LONG:
                if current_price > self.highest_price:
                    self.highest_price = current_price
                
                # 检查多头止损条件：固定止损 + 跟踪止损
                stop_loss_price = self.entry_price * (1 - self.stop_loss_pct)
                trailing_stop_price = self.highest_price * (1 - self.trailing_stop_pct)
                
                if current_price < min(stop_loss_price, trailing_stop_price):
                    # 触发止损，产生卖出信号
                    signal = Signal(
                        symbol=bar.symbol,
                        timestamp=bar.timestamp,
                        direction=Direction.SHORT,
                        price=current_price
                    )
                    self.is_holding = False
                    self.current_direction = None
                    print(f"{bar.timestamp} - 多头触发止损卖出！ 买入价: {self.entry_price}, 现价: {current_price}")
            
            elif self.current_direction == Direction.SHORT:
                if current_price < self.lowest_price:
                    self.lowest_price = current_price
                
                # 检查空头止损条件：固定止损 + 跟踪止损
                stop_loss_price = self.entry_price * (1 + self.stop_loss_pct)
                trailing_stop_price = self.lowest_price * (1 + self.trailing_stop_pct)
                
                if current_price > max(stop_loss_price, trailing_stop_price):
                    # 触发止损，产生买入信号（平仓）
                    signal = Signal(
                        symbol=bar.symbol,
                        timestamp=bar.timestamp,
                        direction=Direction.LONG,
                        price=current_price
                    )
                    self.is_holding = False
                    self.current_direction = None
                    print(f"{bar.timestamp} - 空头触发止损买入！ 卖出价: {self.entry_price}, 现价: {current_price}")
        
        # 原有均线交叉逻辑 + RSI过滤
        if not signal and self.last_short_ema is not None and self.last_long_ema is not None:
            # 短期均线上穿长期均线 - 多头信号
            if self.last_short_ema <= self.last_long_ema and short_ema > long_ema:
                # RSI过滤，RSI < rsi_limit 才买入
                if rsi < self.rsi_limit and not self.is_holding:
                    signal = Signal(
                        symbol=bar.symbol,
                        timestamp=bar.timestamp,
                        direction=Direction.LONG,
                        price=current_price
                    )
                    # 记录买入价格和持仓状态
                    self.entry_price = current_price
                    self.is_holding = True
                    self.current_direction = Direction.LONG
                    self.highest_price = current_price
                    self.lowest_price = float('inf')
                    print(f"{bar.timestamp} - 产生买入信号！ RSI: {rsi:.2f}, 短期EMA: {short_ema:.2f}, 长期EMA: {long_ema:.2f}")
            
            # 短期均线下穿长期均线 - 空头信号
            elif self.last_short_ema >= self.last_long_ema and short_ema < long_ema:
                # RSI过滤，RSI > rsi_low_limit 才卖出
                if rsi > self.rsi_low_limit and not self.is_holding:
                    signal = Signal(
                        symbol=bar.symbol,
                        timestamp=bar.timestamp,
                        direction=Direction.SHORT,
                        price=current_price
                    )
                    # 记录卖出价格和持仓状态
                    self.entry_price = current_price
                    self.is_holding = True
                    self.current_direction = Direction.SHORT
                    self.lowest_price = current_price
                    self.highest_price = 0.0
                    print(f"{bar.timestamp} - 产生卖出信号！ RSI: {rsi:.2f}, 短期EMA: {short_ema:.2f}, 长期EMA: {long_ema:.2f}")
        
        # 添加RSI超买超卖信号
        if not signal and self.is_holding:
            if self.current_direction == Direction.LONG and rsi > 80:
                # RSI超买，产生卖出信号
                signal = Signal(
                    symbol=bar.symbol,
                    timestamp=bar.timestamp,
                    direction=Direction.SHORT,
                    price=current_price
                )
                self.is_holding = False
                self.current_direction = None
                print(f"{bar.timestamp} - RSI超买卖出！ RSI: {rsi:.2f}")
            elif self.current_direction == Direction.SHORT and rsi < 20:
                # RSI超卖，产生买入信号
                signal = Signal(
                    symbol=bar.symbol,
                    timestamp=bar.timestamp,
                    direction=Direction.LONG,
                    price=current_price
                )
                self.is_holding = False
                self.current_direction = None
                print(f"{bar.timestamp} - RSI超卖买入！ RSI: {rsi:.2f}")
        
        # 更新上一次的EMA值
        self.last_short_ema = short_ema
        self.last_long_ema = long_ema
        
        return signal
