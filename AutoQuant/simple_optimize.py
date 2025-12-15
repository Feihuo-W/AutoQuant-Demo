#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 简单策略参数优化脚本
专注于找到能产生80%以上收益率的参数组合
"""

from typing import List, Dict, Tuple
from data_loader import generate_realistic_btc_data
from strategy import DoubleMaStrategy
from backtest import BacktestEngine
from execution import SimulatedExecution


def test_strategy_params(short_period: int, long_period: int, stop_loss_pct: float, trailing_stop_pct: float, 
                         rsi_period: int, rsi_limit: float) -> Tuple[float, int]:
    """
    测试特定参数组合的策略表现
    
    Args:
        short_period: 短期均线周期
        long_period: 长期均线周期
        stop_loss_pct: 止损百分比
        trailing_stop_pct: 跟踪止损百分比
        rsi_period: RSI计算周期
        rsi_limit: RSI上限
        
    Returns:
        Tuple[float, int]: 收益率和交易次数
    """
    # 获取数据
    symbol = "BTC-USD"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    data = generate_realistic_btc_data(start_date=start_date, end_date=end_date, seed=42)  # 使用固定种子确保数据一致
    
    # 初始化策略
    strategy = DoubleMaStrategy(
        short_period=short_period,
        long_period=long_period,
        stop_loss_pct=stop_loss_pct,
        trailing_stop_pct=trailing_stop_pct,
        rsi_period=rsi_period,
        rsi_limit=rsi_limit
    )
    
    # 创建执行引擎
    execution_engine = SimulatedExecution()
    execution_engine.set_fee_rate(0.001)  # 设置手续费率为 0.1%
    
    # 创建回测引擎
    backtest_engine = BacktestEngine(
        strategy=strategy,
        data=data,
        execution_engine=execution_engine
    )
    
    # 运行回测
    equity_curve = backtest_engine.run()
    
    # 计算收益率
    initial_capital = backtest_engine.initial_capital
    # 使用equity_curve的最后一个值，它已经包含了现金+持仓价值
    final_value = equity_curve[-1] if equity_curve else initial_capital
    # 确保final_value不会为负数
    final_value = max(final_value, 0.0)
    return_rate = (final_value - initial_capital) / initial_capital * 100
    
    return return_rate, len(backtest_engine.signals)


def find_best_params() -> Dict:
    """
    寻找能产生80%以上收益率的最佳参数组合
    
    Returns:
        Dict: 最佳参数组合
    """
    print("开始寻找最佳参数组合...")
    
    # 定义参数范围
    # 短期均线周期
    short_periods = [7, 10, 12, 15, 18]
    # 长期均线周期
    long_periods = [25, 30, 35, 40, 45]
    # 止损百分比
    stop_loss_pcts = [0.02, 0.03, 0.04, 0.05]
    # 跟踪止损百分比
    trailing_stop_pcts = [0.03, 0.04, 0.05, 0.06]
    # RSI周期
    rsi_periods = [10, 14, 18, 21]
    # RSI上限
    rsi_limits = [65, 70, 75, 80]
    
    best_params = None
    best_return = -float('inf')
    total_combinations = len(short_periods) * len(long_periods) * len(stop_loss_pcts) * \
                        len(trailing_stop_pcts) * len(rsi_periods) * len(rsi_limits)
    
    print(f"总参数组合数量: {total_combinations}")
    
    # 遍历所有参数组合
    combination_count = 0
    for short_p in short_periods:
        for long_p in long_periods:
            # 确保短期周期小于长期周期
            if short_p >= long_p:
                continue
            
            for stop_loss in stop_loss_pcts:
                for trailing_stop in trailing_stop_pcts:
                    for rsi_p in rsi_periods:
                        for rsi_lim in rsi_limits:
                            combination_count += 1
                            
                            if combination_count % 100 == 0:
                                print(f"已测试 {combination_count}/{total_combinations} 个组合")
                            
                            # 测试当前参数组合
                            return_rate, trades = test_strategy_params(
                                short_period=short_p,
                                long_period=long_p,
                                stop_loss_pct=stop_loss,
                                trailing_stop_pct=trailing_stop,
                                rsi_period=rsi_p,
                                rsi_limit=rsi_lim
                            )
                            
                            # 更新最佳参数
                            if return_rate > best_return:
                                best_return = return_rate
                                best_params = {
                                    "short_period": short_p,
                                    "long_period": long_p,
                                    "stop_loss_pct": stop_loss,
                                    "trailing_stop_pct": trailing_stop,
                                    "rsi_period": rsi_p,
                                    "rsi_limit": rsi_lim
                                }
                                print(f"\n找到更优参数组合！")
                                print(f"短期: {short_p}, 长期: {long_p}, 止损: {stop_loss*100:.1f}%, 跟踪止损: {trailing_stop*100:.1f}%")
                                print(f"RSI周期: {rsi_p}, RSI上限: {rsi_lim}")
                                print(f"收益率: {return_rate:.2f}%, 交易次数: {trades}")
                                
                                # 如果已经达到目标，提前返回
                                if best_return > 80:
                                    print(f"\n✅ 已找到达到目标收益率的参数组合！")
                                    return best_params
    
    return best_params


def main():
    """
    主函数
    """
    # 寻找最佳参数
    best_params = find_best_params()
    
    if best_params:
        print("\n" + "="*60)
        print("最终最佳参数组合")
        print("="*60)
        for key, value in best_params.items():
            if isinstance(value, float):
                if key in ["stop_loss_pct", "trailing_stop_pct"]:
                    print(f"{key}: {value*100:.1f}%")
                else:
                    print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
        
        # 使用最佳参数进行最终测试
        print("\n使用最佳参数进行最终测试...")
        return_rate, trades = test_strategy_params(**best_params)
        print(f"最终收益率: {return_rate:.2f}%")
        print(f"交易次数: {trades}")
        
        if return_rate > 80:
            print("✅ 成功！收益率超过80%！")
        else:
            print("❌ 未达到80%收益率目标")
    else:
        print("未找到合适的参数组合")


if __name__ == "__main__":
    main()
