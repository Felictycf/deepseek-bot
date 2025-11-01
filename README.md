# BTC 盯盘机器人

从 NOFX 项目提取 prompt 逻辑，用于 BTC 市场分析和盯盘。

## 功能特点

- ✅ 使用与 NOFX 相同的 system prompt 和 user prompt 结构
- ✅ 通过 CCXT 获取 Binance 市场数据
- ✅ 计算完整的技术指标（EMA, MACD, RSI, ATR 等）
- ✅ DeepSeek AI 深度市场分析
- ✅ 自动生成 BTC 图表
- ✅ Telegram Bot 推送分析结果
- ✅ 每 5 分钟自动运行（可配置）

## 快速开始

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

### 2. 配置

复制配置文件模板：

```bash
cp config.json.example config.json
```

编辑 `config.json`，填入你的 API 密钥：

```json
{
  "deepseek_api_key": "sk-your-deepseek-api-key-here",
  "telegram_bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "telegram_chat_id": "YOUR_TELEGRAM_CHAT_ID",
  "chart_api_key": "YOUR_CHART_API_KEY",
  "analysis_interval_minutes": 5
}
```

**获取 API 密钥：**

- **DeepSeek API**: [https://platform.deepseek.com](https://platform.deepseek.com)
- **Telegram Bot**: 通过 [@BotFather](https://t.me/BotFather) 创建机器人
- **Chart API**: [https://chart-img.com](https://chart-img.com)（可选）

### 3. 运行

```bash
python btc_monitor.py
```

## 项目结构

```
deepseek_bot/
├── market_data.py          # 市场数据获取（CCXT + 技术指标）
├── prompts.py              # System Prompt & User Prompt 构建
├── deepseek_client.py      # DeepSeek API 客户端
├── btc_monitor.py          # 主程序（监控循环）
├── config.json.example     # 配置文件模板
├── requirements.txt        # Python 依赖
├── README.md              # 本文件
└── analysis_logs/         # 分析日志（自动创建）
```

## 数据结构

### 市场数据（对应 NOFX 的 market.Data）

```python
{
  'symbol': 'BTCUSDT',
  'current_price': 95000.0,
  'price_change_1h': 1.5,
  'price_change_4h': -0.8,
  'current_ema20': 94800.0,
  'current_macd': 125.34,
  'current_rsi7': 68.5,
  'open_interest': {'latest': 150000.0, 'average': 148000.0},
  'funding_rate': 0.0001,
  'intraday_series': {
    'mid_prices': [...],      # 最近20个3分钟价格
    'ema20_values': [...],
    'macd_values': [...],
    'rsi7_values': [...],
    'rsi14_values': [...]
  },
  'longer_term_context': {
    'ema20': 94500.0,
    'ema50': 93000.0,
    'atr3': 1200.0,
    'atr14': 1500.0,
    'current_volume': 25000.0,
    'average_volume': 23000.0,
    'macd_values': [...],      # 最近10个4小时MACD
    'rsi14_values': [...]      # 最近10个4小时RSI
  }
}
```

### AI 分析结果

```python
{
  'market_state': '上涨趋势',
  'short_term_trend': '1小时内可能继续上涨至96000',
  'mid_term_trend': '4小时保持震荡',
  'key_levels': {
    'support': 94000,
    'resistance': 96500
  },
  'confidence': 75,
  'key_signals': [
    'MACD金叉',
    'RSI突破70'
  ],
  'risk_warning': '注意96500阻力位',
  'summary': 'BTC短期看涨，关注阻力位'
}
```

## 使用说明

### 运行模式

**1. 单次分析**（测试用）：

修改 `btc_monitor.py`，注释掉循环部分，只运行一次 `run_analysis()`。

**2. 持续监控**（推荐）：

直接运行 `python btc_monitor.py`，每 5 分钟自动分析一次。

### Telegram 推送

配置 Telegram Bot 后，每次分析会自动推送：
1. 格式化的分析结果文本
2. BTC 图表图片（如果配置了 Chart API）

### 日志记录

所有分析结果会保存到 `analysis_logs/YYYY-MM-DD.jsonl`，格式为 JSON Lines（每行一个 JSON）。

**查看日志：**

```bash
# 查看今天的分析日志
cat analysis_logs/$(date +%Y-%m-%d).jsonl | jq .

# 统计分析次数
wc -l analysis_logs/$(date +%Y-%m-%d).jsonl
```

## 与 NOFX 的对应关系

| NOFX 组件 | 本项目组件 | 说明 |
|-----------|------------|------|
| `market/data.go` | `market_data.py` | 市场数据获取 |
| `decision/engine.go` | `prompts.py` | Prompt 构建 |
| `mcp/client.go` | `deepseek_client.py` | AI API 客户端 |
| `trader/auto_trader.go` | `btc_monitor.py` | 主循环逻辑 |

## 注意事项

1. **TA-Lib 依赖**：必须先安装系统级的 TA-Lib 库
2. **API 费用**：DeepSeek API 按调用收费（~$0.14/1M tokens）
3. **网络要求**：需要访问 Binance API 和 DeepSeek API
4. **数据延迟**：使用公共 API，数据可能有 1-2 秒延迟
5. **仅分析**：本项目不包含交易逻辑，仅用于市场分析

## 故障排查

**1. TA-Lib 安装失败**

```bash
# macOS
brew install ta-lib
pip install TA-Lib

# Linux（Ubuntu）
sudo apt-get install libta-lib0-dev
pip install TA-Lib
```

**2. CCXT 无法连接 Binance**

检查网络连接，可能需要代理。

**3. DeepSeek API 超时**

增加 `timeout` 配置或检查网络。

**4. Telegram 消息发送失败**

检查 `bot_token` 和 `chat_id` 是否正确。

## 许可证

MIT License - 与 NOFX 项目保持一致
