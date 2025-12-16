# AutoQuant-Demo
# 📈 AutoQuant - 智能量化交易回测系统

> **Powered by Trae | AI 驱动的量化开发实践**

AutoQuant 是一个基于 Python 的轻量级量化交易回测框架。本项目旨在通过自动化脚本获取金融数据，并验证经典交易策略（如均线策略、RSI 动量策略）在历史行情中的表现。

本项目全流程采用 **字节跳动 Trae (AI IDE)** 辅助开发，探索了 "AI Native" 的编程新范式。

---

## 🚀 功能特性 (Features)

- **📊 数据获取**：集成 `yfinance` 接口，支持美股/A股/加密货币的历史数据自动拉取。
- **🧠 策略引擎**：
  - **均线交叉 (MA Cross)**：捕捉金叉/死叉趋势信号。
  - **趋势跟踪**：基于价格突破的自动化交易逻辑。
- **💸 模拟回测**：
  - 支持设置初始资金（如 $100,000）。
  - 自动计算佣金与滑点。
  - **实时日志**：终端实时输出买入/卖出信号及当前持仓利润。
- **📈 可视化报表**：自动生成资金曲线图与交易点位标记。

---

## 🛠 技术栈 (Tech Stack)

- **开发工具**：[Trae IDE](https://www.trae.ai/) (AI Copilot & Builder)
- **核心语言**：Python 3.10+
- **依赖库**：
  - `backtrader` / `pandas`: 回测框架与数据处理
  - `yfinance`: 雅虎财经数据接口
  - `matplotlib`: 绘图支持

---

## 💻 快速开始 (Quick Start)

### 1. 环境准备
确保你的电脑已安装 Python。

### 2. 安装依赖
```bash
pip install pandas yfinance matplotlib backtrader
```


- Author:FeiHuo
- Date: 2025-12-13
