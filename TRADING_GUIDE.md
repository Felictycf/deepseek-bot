# BTC 交易决策监控机器人 - 使用指南

## 📋 项目说明

这是基于 NOFX 项目的完整交易决策系统，使用 DeepSeek AI 进行 BTC 市场分析和交易决策。

### 🎯 主要功能

- ✅ 使用 NOFX 最新的 System Prompt 和 User Prompt
- ✅ **完整交易决策**：开多、开空、止盈、止损、持有、观望
- ✅ **多时间框架分析**：3分钟、15分钟、1小时、4小时
- ✅ **风险管理**：风险回报比 ≥ 1:3，杠杆控制，仓位管理
- ✅ **夏普比率优化**：AI 根据夏普比率自我进化
- ✅ **模拟账户**：跟踪虚拟账户盈亏（不对接交易所）
- ✅ **图表推送**：自动生成 TradingView 图表
- ✅ **Telegram 通知**：实时推送交易决策

### 🆚 与原版 deepseek_bot 的区别

| 特性 | 原版 (btc_monitor.py) | 交易版 (btc_trading_monitor.py) |
|------|---------------------|--------------------------------|
| 功能定位 | 纯市场分析 | 完整交易决策系统 |
| System Prompt | 分析型 prompt | NOFX 交易型 prompt |
| AI 输出 | 市场状态、趋势预测 | 具体交易指令（开单/止盈/止损） |
| 决策格式 | JSON 分析结果 | JSON 交易决策数组 |
| 账户管理 | 无 | 模拟账户跟踪 |
| 风险控制 | 无 | 风险回报比、杠杆、仓位管理 |
| 夏普比率 | 无 | 持续跟踪和优化 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装 TA-Lib（技术指标库）
# macOS
brew install ta-lib

# Ubuntu/Debian
sudo apt-get install libta-lib0-dev

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 配置文件

使用现有的 `config.json`，或参考 `config.json.example`：

```json
{
  "deepseek_api_key": "sk-your-deepseek-api-key",
  "deepseek_base_url": "https://api.siliconflow.cn/v1",
  "deepseek_model": "deepseek-ai/DeepSeek-V3.1",
  "telegram_bot_token": "YOUR_BOT_TOKEN",
  "telegram_chat_id": "YOUR_CHAT_ID",
  "chart_api_key": "YOUR_CHART_API_KEY",
  "chart_interval": "1h",
  "analysis_interval_minutes": 5,
  "initial_balance": 1000.0,
  "btc_eth_leverage": 5,
  "altcoin_leverage": 5
}
```

**新增配置项说明**：
- `initial_balance`: 模拟账户初始资金（美元）
- `btc_eth_leverage`: BTC/ETH 的最大杠杆倍数
- `altcoin_leverage`: 山寨币的最大杠杆倍数

### 3. 运行

```bash
cd deepseek_bot
python btc_trading_monitor.py
```

---

## 📊 AI 决策格式

### System Prompt 核心要点

AI 遵循以下交易原则（来自 NOFX）：

1. **核心目标**：最大化夏普比率（高质量交易 > 高频交易）
2. **硬约束**：
   - 风险回报比 ≥ 1:3
   - 最多持仓 3 个币种
   - 单币仓位限制（山寨 800-1500U @ 5x，BTC/ETH 5000-10000U @ 5x）
   - 保证金使用率 ≤ 90%

3. **交易频率认知**：
   - 优秀交易员：每天 2-4 笔
   - 过度交易：每小时 >2 笔
   - 最佳节奏：持仓至少 30-60 分钟

4. **夏普比率自我进化**：
   - 夏普 < -0.5：停止交易，观望 18 分钟
   - 夏普 -0.5 ~ 0：只做信心度 >80 的交易
   - 夏普 0 ~ 0.7：维持当前策略
   - 夏普 > 0.7：可适度扩大仓位

### User Prompt 包含的数据

1. **系统状态**：时间、周期、运行时长
2. **BTC 市场**：当前价格、涨跌幅、MACD、RSI
3. **账户信息**：净值、余额、盈亏、保证金使用率
4. **当前持仓**（如果有）：
   - 币种、方向（多/空）
   - 入场价、当前价、盈亏
   - 杠杆、保证金、强平价
   - 持仓时长
5. **候选币种**：BTC 完整市场数据
   - 4 个时间框架（3m, 15m, 1h, 4h）
   - 技术指标序列（EMA, MACD, RSI, ATR, 布林带）
   - 成交量、持仓量、资金费率
6. **夏普比率**：历史表现反馈

### AI 决策输出格式

AI 会返回以下格式：

```
[思维链分析]

当前市场处于...
BTC 4小时级别显示...
建议操作...

[JSON 决策数组]

[
  {
    "symbol": "BTCUSDT",
    "action": "open_long",
    "leverage": 5,
    "position_size_usd": 5000,
    "stop_loss": 68000,
    "take_profit": 74000,
    "confidence": 85,
    "risk_usd": 300,
    "reasoning": "4小时EMA金叉+MACD转正+RSI从超卖反弹"
  }
]
```

**决策字段说明**：

- `symbol`: 交易对（BTCUSDT、ETHUSDT 等）
- `action`: 操作类型
  - `open_long`: 开多
  - `open_short`: 开空
  - `close_long`: 平多
  - `close_short`: 平空
  - `hold`: 持有（已有仓位）
  - `wait`: 观望（无操作）
- `leverage`: 杠杆倍数（开仓时必填）
- `position_size_usd`: 仓位大小（美元，开仓时必填）
- `stop_loss`: 止损价格（开仓时必填）
- `take_profit`: 止盈价格（开仓时必填）
- `confidence`: 信心度 0-100（开仓建议 ≥75）
- `risk_usd`: 最大美元风险（开仓时必填）
- `reasoning`: 决策理由

---

## 📱 Telegram 推送格式

机器人会推送以下内容到 Telegram：

```
🤖 BTC 交易决策报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💰 账户状态:
  • 净值: $1,000.00
  • 可用: $1,000.00 (100.0%)
  • 盈亏: +0.00%
  • 保证金: 0.0%
  • 持仓: 0个

📋 AI 交易决策 (共1条):

📈 决策 #1: BTCUSDT - 开多
  • 杠杆: 5x
  • 仓位: $5,000.00
  • 止损: $68,000.00
  • 止盈: $74,000.00
  • 风险: $300.00
  • 信心度: 85%
  • 理由: 4小时EMA金叉+MACD转正+RSI从超卖反弹

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💭 AI 分析过程:
当前BTC处于4小时级别的上升趋势...
（完整分析已保存到日志）
```

同时附带 TradingView 图表图片。

---

## 📂 文件说明

### 核心文件

- **`btc_trading_monitor.py`**: 主程序（支持交易决策）
- **`prompts_trading.py`**: NOFX 风格的 System/User Prompt 构建器
- **`market_data.py`**: 市场数据获取（CCXT + TA-Lib）
- **`deepseek_client.py`**: DeepSeek API 客户端

### 配置和数据

- **`config.json`**: 配置文件
- **`analysis_logs/`**: 分析日志（JSON Lines 格式）
- **`btc_chart_*.png`**: 生成的图表

### 与原版对比

| 文件 | 原版 | 交易版 | 说明 |
|------|------|--------|------|
| 主程序 | `btc_monitor.py` | `btc_trading_monitor.py` | 交易版支持决策输出 |
| Prompt | `prompts.py` | `prompts_trading.py` | 交易版使用 NOFX prompt |
| 市场数据 | `market_data.py` | `market_data.py` | 共用 |
| AI 客户端 | `deepseek_client.py` | `deepseek_client.py` | 共用 |

---

## 🔍 工作流程

1. **获取市场数据**：4 个时间框架的完整技术指标
2. **构建 Prompts**：
   - System Prompt：NOFX 交易规则和风险控制
   - User Prompt：市场数据 + 账户状态 + 持仓 + 夏普比率
3. **调用 DeepSeek AI**：获取交易决策
4. **解析决策**：提取思维链和 JSON 决策数组
5. **生成图表**：TradingView 图表
6. **推送 Telegram**：决策报告 + 图表
7. **保存日志**：JSONL 格式

---

## ⚠️ 重要说明

### 1. 这是模拟系统

- **不对接交易所**：所有决策仅作为文本输出
- **模拟账户**：盈亏跟踪是虚拟的
- **无实际交易**：不会执行任何真实订单

### 2. 仅供学习和研究

- 加密货币交易有高风险
- AI 决策不保证盈利
- 请勿盲目跟单

### 3. 如何使用决策

- **学习参考**：了解专业交易员的分析思路
- **信号提示**：结合自己的判断后手动下单
- **策略回测**：记录决策并分析历史表现

---

## 📊 查看日志

分析日志保存在 `analysis_logs/YYYY-MM-DD.jsonl`：

```bash
# 查看今天的决策日志
cat analysis_logs/$(date +%Y-%m-%d).jsonl | jq .

# 提取所有决策
cat analysis_logs/*.jsonl | jq '.decisions' | jq -s 'flatten'

# 统计决策类型
cat analysis_logs/*.jsonl | jq -r '.decisions[].action' | sort | uniq -c
```

---

## 🛠 故障排查

### 1. AI 没有返回决策

可能原因：
- 市场处于观望期（正常现象）
- JSON 格式错误（检查日志中的 CoT 思维链）

解决方案：
- 等待下一个周期
- 查看完整的 AI 响应

### 2. Telegram 推送失败

检查：
- `telegram_bot_token` 是否正确
- `telegram_chat_id` 是否正确
- 网络连接是否正常

### 3. 图表生成失败

检查：
- `chart_api_key` 是否有效
- API 配额是否用完
- 网络连接是否正常

---

## 💡 使用建议

1. **初次运行**：
   - 先设置较短的分析间隔（如 5 分钟）观察 AI 表现
   - 查看前几次决策的质量和推理过程

2. **调整参数**：
   - 根据风险偏好调整 `btc_eth_leverage` 和 `altcoin_leverage`
   - 增加 `initial_balance` 以获得更大的仓位建议

3. **长期运行**：
   - 使用 `nohup` 或 `screen` 在后台运行
   - 定期查看夏普比率变化
   - 分析 AI 的进化过程

---

## 📈 下一步扩展

如果你想实际对接交易所：

1. 参考 NOFX 主项目的 `trader/` 目录
2. 实现 Binance/Hyperliquid 的 API 对接
3. 添加真实的仓位管理和订单执行
4. 集成完整的风险控制系统

**重要**：实盘交易前务必充分测试！

---

## 📞 支持

- 项目主仓库：[NOFX](https://github.com/your-repo/nofx)
- Telegram 开发者社区：[@nofx_dev_community](https://t.me/nofx_dev_community)

---

**最后更新**：2025-11-01
**版本**：Trading Decision Bot v1.0
