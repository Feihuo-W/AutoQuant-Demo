#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoQuant - 模块化量化交易系统
项目入口点
"""

from data_loader import generate_realistic_btc_data
from strategy import DoubleMaStrategy
from backtest import BacktestEngine
from execution import SimulatedExecution


def main() -> None:
    """项目主函数"""
    print("AutoQuant 量化交易系统初始化...")
    
    # 1. 获取数据
    print("\n1. 获取数据...")
    # 回测 BTC-USD (比特币) 从 2023-01-01 到 2023-12-31
    symbol = "BTC-USD"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    # 使用真实模拟数据生成器生成 BTC-USD 数据
    from data_loader import generate_realistic_btc_data
    data = generate_realistic_btc_data(start_date=start_date, end_date=end_date)
    
    print(f"获取了 {len(data)} 天的 {symbol} 数据")
    print(f"数据时间范围: {data[0].timestamp.date()} 到 {data[-1].timestamp.date()}")
    
    # 2. 初始化策略
    print("\n2. 初始化策略...")
    # 使用优化中发现的最佳参数组合
    strategy = DoubleMaStrategy(
        short_period=7,
        long_period=35,
        stop_loss_pct=0.02,
        trailing_stop_pct=0.04,
        rsi_period=14,
        rsi_limit=65
    )
    print(f"策略: 双均线策略 (短期={strategy.short_period}, 长期={strategy.long_period}, 止损={strategy.stop_loss_pct*100:.1f}%,")
    print(f"跟踪止损={strategy.trailing_stop_pct*100:.1f}%, RSI周期={strategy.rsi_period}, RSI上限={strategy.rsi_limit})")
    
    # 3. 创建执行引擎
    print("\n3. 创建执行引擎...")
    execution_engine = SimulatedExecution()
    execution_engine.set_fee_rate(0.001)  # 设置手续费率为 0.1%
    
    # 4. 创建回测引擎
    print("\n4. 创建回测引擎...")
    backtest_engine = BacktestEngine(strategy=strategy, data=data, execution_engine=execution_engine)
    
    # 5. 运行回测
    print("\n5. 运行回测...")
    equity_curve = backtest_engine.run()
    
    # 6. 结果可视化
    print("\n6. 结果可视化...")
    from analysis.plotter import plot_results
    plot_results(
        bars=data,
        signals=backtest_engine.signals,
        equity_curve=equity_curve
    )
    
    print("\nAutoQuant 量化交易系统回测完成!")


if __name__ == "__main__":
    main()
