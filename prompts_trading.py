"""
Prompt 构建模块 - 完整交易版本
从 NOFX 项目提取的最新 System Prompt 和 User Prompt 构建逻辑
支持完整交易决策（开单、止盈、止损），但仅作为文本输出，不对接交易所
"""

from datetime import datetime
from typing import Dict, List, Optional


def build_system_prompt(account_equity: float = 1000.0, btc_eth_leverage: int = 5, altcoin_leverage: int = 5) -> str:
    """
    构建 System Prompt（固定规则）
    直接从 NOFX decision/engine.go 的 buildSystemPrompt() 函数提取

    Args:
        account_equity: 账户净值（美元）
        btc_eth_leverage: BTC/ETH 杠杆倍数
        altcoin_leverage: 山寨币杠杆倍数

    Returns:
        System prompt 字符串
    """
    # 核心使命
    prompt = """你是专业的加密货币交易AI，在合约市场进行自主交易。

# 核心目标

最大化夏普比率（Sharpe Ratio）

夏普比率 = 平均收益 / 收益波动率

这意味着：
- 高质量交易（高胜率、大盈亏比）→ 提升夏普
- 稳定收益、控制回撤 → 提升夏普
- 耐心持仓、让利润奔跑 →  提升夏普
- 频繁交易、小盈小亏 → 增加波动，严重降低夏普
- 过度交易、手续费损耗 → 直接亏损
- 过早平仓、频繁进出 → 错失大行情

关键认知: 系统每3分钟扫描一次，但不意味着每次都要交易！
大多数时候应该是 `wait` 或 `hold`，只在极佳机会时才开仓。

# 硬约束（风险控制）

1. 风险回报比: 必须 ≥ 1:3（冒1%风险，赚3%+收益）
2. 最多持仓: 3个币种（质量>数量）
"""

    # 单币仓位约束
    prompt += f"3. 单币仓位: 山寨{account_equity*0.8:.0f}-{account_equity*1.5:.0f} U({altcoin_leverage}x杠杆) | BTC/ETH {account_equity*5:.0f}-{account_equity*10:.0f} U({btc_eth_leverage}x杠杆)\n"
    prompt += "4. 保证金: 总使用率 ≤ 90%\n\n"

    # 交易哲学 & 最佳实践
    prompt += """# 交易哲学 & 最佳实践

## 核心原则：

资金保全第一：保护资本比追求收益更重要

纪律胜于情绪：执行你的退出方案，不随意移动止损或目标

质量优于数量：少量高信念交易胜过大量低信念交易

适应波动性：根据市场条件调整仓位

尊重趋势：不要与强趋势作对

## 常见误区避免：

过度交易：频繁交易导致费用侵蚀利润

复仇式交易：亏损后立即加码试图"翻本"

分析瘫痪：过度等待完美信号，导致失机

忽视相关性：BTC常引领山寨币，须优先观察BTC

过度杠杆：放大收益同时放大亏损

#交易频率认知

量化标准:
- 优秀交易员：每天2-4笔 = 每小时0.1-0.2笔
- 过度交易：每小时>2笔 = 严重问题
- 最佳节奏：开仓后持有至少30-60分钟

自查:
如果你发现自己每个周期都在交易 → 说明标准太低
如果你发现持仓<30分钟就平仓 → 说明太急躁

# 开仓标准（严格）

只在强信号时开仓，不确定就观望。

你拥有的完整数据：
- 原始序列：3分钟价格序列(MidPrices数组) + 4小时K线序列
- 技术序列：EMA20序列、MACD序列、RSI7序列、RSI14序列
- 资金序列：成交量序列、持仓量(OI)序列、资金费率
- 筛选标记：AI500评分 / OI_Top排名（如果有标注）

分析方法（完全由你自主决定）：
- 自由运用序列数据，你可以做但不限于趋势分析、形态识别、支撑阻力、技术阻力位、斐波那契、波动带计算
- 多维度交叉验证（价格+量+OI+指标+序列形态）
- 用你认为最有效的方法发现高确定性机会
- 综合信心度 ≥ 75 才开仓

避免低质量信号：
- 单一维度（只看一个指标）
- 相互矛盾（涨但量萎缩）
- 横盘震荡
- 刚平仓不久（<15分钟）

# 夏普比率自我进化

每次你会收到夏普比率作为绩效反馈（周期级别）：

夏普比率 < -0.5 (持续亏损):
  → 停止交易，连续观望至少6个周期（18分钟）
  → 深度反思：
     • 交易频率过高？（每小时>2次就是过度）
     • 持仓时间过短？（<30分钟就是过早平仓）
     • 信号强度不足？（信心度<75）
夏普比率 -0.5 ~ 0 (轻微亏损):
  → 严格控制：只做信心度>80的交易
  → 减少交易频率：每小时最多1笔新开仓
  → 耐心持仓：至少持有30分钟以上

夏普比率 0 ~ 0.7 (正收益):
  → 维持当前策略

夏普比率 > 0.7 (优异表现):
  → 可适度扩大仓位

关键: 夏普比率是唯一指标，它会自然惩罚频繁交易和过度进出。

#决策流程

1. 分析夏普比率: 当前策略是否有效？需要调整吗？
2. 评估持仓: 趋势是否改变？是否该止盈/止损？
3. 寻找新机会: 有强信号吗？多空机会？
4. 输出决策: 思维链分析 + JSON

#输出格式

第一步: 思维链（纯文本）
简洁分析你的思考过程

第二步: JSON决策数组

```json
[
"""

    # 示例决策
    prompt += f"""  {{"symbol": "BTCUSDT", "action": "open_short", "leverage": {btc_eth_leverage}, "position_size_usd": {account_equity*5:.0f}, "stop_loss": 97000, "take_profit": 91000, "confidence": 85, "risk_usd": 300, "reasoning": "下跌趋势+MACD死叉"}},
  {{"symbol": "ETHUSDT", "action": "close_long", "reasoning": "止盈离场"}}
]
```

字段说明:
- `action`: open_long | open_short | close_long | close_short | hold | wait
- `confidence`: 0-100（开仓建议≥75）
- 开仓时必填: leverage, position_size_usd, stop_loss, take_profit, confidence, risk_usd, reasoning

---

记住:
- 目标是夏普比率，不是交易频率
- 宁可错过，不做低质量交易
- 风险回报比1:3是底线
"""

    return prompt


def build_user_prompt(
    market_data: Dict,
    runtime_minutes: int = 0,
    call_count: int = 0,
    account_info: Optional[Dict] = None,
    positions: Optional[List[Dict]] = None,
    sharpe_ratio: Optional[float] = None
) -> str:
    """
    构建 User Prompt（动态市场数据）
    对应 NOFX 的 buildUserPrompt() 函数

    Args:
        market_data: 市场数据字典（来自 market_data.py）
        runtime_minutes: 系统运行时长（分钟）
        call_count: AI 调用次数
        account_info: 账户信息（模拟）
        positions: 当前持仓列表（模拟）
        sharpe_ratio: 夏普比率（可选）

    Returns:
        格式化的 user prompt 字符串
    """
    lines = []

    # === 系统状态 ===
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"时间: {current_time} | 周期: #{call_count} | 运行: {runtime_minutes}分钟\n")

    # === BTC 市场概览 ===
    pc = market_data['price_changes']
    lines.append(f"BTC: ${market_data['current_price']:,.2f} (1h: {pc['1h']:+.2f}%, 4h: {pc['4h']:+.2f}%) | MACD: {market_data['current_macd']:.4f} | RSI: {market_data['current_rsi7']:.2f}\n")

    # === 账户信息 ===
    if account_info is None:
        # 默认模拟账户
        account_info = {
            'total_equity': 1000.0,
            'available_balance': 1000.0,
            'total_pnl_pct': 0.0,
            'margin_used_pct': 0.0,
            'position_count': 0
        }

    lines.append(f"账户: 净值{account_info['total_equity']:.2f} | 余额{account_info['available_balance']:.2f} ({account_info['available_balance']/account_info['total_equity']*100:.1f}%) | 盈亏{account_info['total_pnl_pct']:+.2f}% | 保证金{account_info['margin_used_pct']:.1f}% | 持仓{account_info['position_count']}个\n")

    # === 当前持仓 ===
    if positions and len(positions) > 0:
        lines.append("\n## 当前持仓\n")
        for i, pos in enumerate(positions, 1):
            lines.append(f"{i}. {pos['symbol']} {pos['side'].upper()} | 入场价{pos['entry_price']:.4f} 当前价{pos['mark_price']:.4f} | 盈亏{pos['unrealized_pnl_pct']:+.2f}% | 杠杆{pos['leverage']}x | 保证金{pos['margin_used']:.0f} | 强平价{pos['liquidation_price']:.4f}")

            # 持仓时长
            if 'holding_minutes' in pos:
                if pos['holding_minutes'] < 60:
                    lines.append(f" | 持仓时长{pos['holding_minutes']}分钟\n")
                else:
                    hours = pos['holding_minutes'] // 60
                    mins = pos['holding_minutes'] % 60
                    lines.append(f" | 持仓时长{hours}小时{mins}分钟\n")
            else:
                lines.append("\n")

            # 持仓的市场数据（简化版，只显示关键信息）
            lines.append(f"  当前价格: ${market_data['current_price']:,.2f} | EMA20: ${market_data['current_ema20']:.2f} | MACD: {market_data['current_macd']:.4f} | RSI(7): {market_data['current_rsi7']:.2f}\n\n")
    else:
        lines.append("\n当前持仓: 无\n")

    # === 候选币种（BTC 完整市场数据）===
    lines.append("\n## 候选币种 (1个)\n\n")
    lines.append("### 1. BTCUSDT\n\n")

    # 多时间框架数据（与监控版本相同）
    lines.append("**多时间框架数据**:\n\n")

    # 函数：格式化时间框架数据（简化版）
    def format_timeframe_brief(tf_data, emoji, name):
        """简化版时间框架展示"""
        current = tf_data['current']

        # EMA 趋势判断
        ema_trend = "↑ 上升" if current['price'] > current['ema20'] > current['ema50'] else \
                   "↓ 下降" if current['price'] < current['ema20'] < current['ema50'] else \
                   "↔ 震荡"

        # MACD 状态
        macd_status = "金叉" if current['macd'] > 0 else "死叉"

        # RSI 状态
        rsi_status = "超买" if current['rsi14'] > 70 else "超卖" if current['rsi14'] < 30 else "中性"

        return (
            f"{emoji} **{name}**: 价格${current['price']:,.2f} | "
            f"趋势{ema_trend} | MACD {macd_status} | RSI(14) {current['rsi14']:.1f} ({rsi_status})\n"
        )

    # 展示4个时间框架的关键信息
    lines.append(format_timeframe_brief(market_data['timeframe_3m'], "⚡", "3分钟"))
    lines.append(format_timeframe_brief(market_data['timeframe_15m'], "🔥", "15分钟"))
    lines.append(format_timeframe_brief(market_data['timeframe_1h'], "📊", "1小时"))
    lines.append(format_timeframe_brief(market_data['timeframe_4h'], "🌊", "4小时"))
    lines.append("\n")

    # 详细的技术指标数据（用于深度分析）
    lines.append("**详细技术指标** (用于深度分析):\n\n")

    for tf_key, tf_name in [('3m', '3分钟'), ('15m', '15分钟'), ('1h', '1小时'), ('4h', '4小时')]:
        tf_data = market_data[f'timeframe_{tf_key}']
        current = tf_data['current']

        lines.append(f"**{tf_name}级别** ({tf_data['data_points']}个数据点):\n")
        lines.append(f"  • 价格序列 (最近10个): {[f'{p:.2f}' for p in tf_data['prices'][-10:]]}\n")
        lines.append(f"  • EMA20: ${current['ema20']:,.2f} | EMA50: ${current['ema50']:,.2f}\n")
        lines.append(f"  • MACD: {current['macd']:.4f} | MACD柱状图: {[f'{v:.3f}' for v in tf_data['macd_hist'][-5:]]}\n")
        lines.append(f"  • RSI(7): {current['rsi7']:.2f} | RSI(14): {current['rsi14']:.2f} | RSI序列: {[f'{v:.1f}' for v in tf_data['rsi14'][-5:]]}\n")
        lines.append(f"  • ATR(14): {current['atr14']:.2f}\n")

        # 布林带
        bb_upper = tf_data['bb_upper'][-1]
        bb_lower = tf_data['bb_lower'][-1]
        bb_position = ((current['price'] - bb_lower) / (bb_upper - bb_lower) * 100) if bb_upper > bb_lower else 50
        lines.append(f"  • 布林带: 上轨${bb_upper:.2f} 下轨${bb_lower:.2f} | 价格位置{bb_position:.1f}%\n")

        # 成交量
        vol_ratio = (current['volume'] / current['volume_ma'] * 100) if current['volume_ma'] > 0 else 100
        vol_status = "放量" if vol_ratio > 120 else "缩量" if vol_ratio < 80 else "正常"
        lines.append(f"  • 成交量: {current['volume']:,.0f} ({vol_status}, {vol_ratio:.0f}% of MA)\n\n")

    # === 市场资金面 ===
    lines.append("**市场资金面**:\n")
    oi = market_data['open_interest']
    lines.append(f"  • 持仓量: {oi['latest']:,.0f} BTC\n")
    lines.append(f"  • 资金费率: {market_data['funding_rate']:.6f} ({market_data['funding_rate']*100:.4f}%)")

    # 资金费率解读
    if market_data['funding_rate'] > 0.0001:
        lines.append(f" → 做多资金费率偏高，市场看多情绪较强\n")
    elif market_data['funding_rate'] < -0.0001:
        lines.append(f" → 做空资金费率偏高，市场看空情绪较强\n")
    else:
        lines.append(f" → 资金费率接近中性，多空相对平衡\n")

    # === 夏普比率（如果有）===
    if sharpe_ratio is not None:
        lines.append(f"\n## 📊 夏普比率: {sharpe_ratio:.2f}\n")

    # === 请求AI分析 ===
    lines.append("\n---\n\n")
    lines.append("现在请分析并输出决策（思维链 + JSON）\n")

    return "".join(lines)


def format_trading_result(cot_trace: str, decisions: List[Dict], account_info: Dict) -> str:
    """
    格式化交易决策结果用于 Telegram 消息（HTML 格式）

    Args:
        cot_trace: 思维链分析文本
        decisions: AI 决策列表
        account_info: 账户信息

    Returns:
        HTML 格式的消息字符串
    """
    lines = []

    # 转义 HTML 特殊字符
    def escape_html(text):
        if not isinstance(text, str):
            text = str(text)
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    lines.append("🤖 <b>BTC 交易决策报告</b>\n")
    lines.append("━" * 40)
    lines.append("\n")

    # 账户信息
    lines.append(f"💰 <b>账户状态</b>:\n")
    lines.append(f"  • 净值: ${account_info['total_equity']:,.2f}\n")
    lines.append(f"  • 可用: ${account_info['available_balance']:,.2f} ({account_info['available_balance']/account_info['total_equity']*100:.1f}%)\n")
    lines.append(f"  • 盈亏: {account_info['total_pnl_pct']:+.2f}%\n")
    lines.append(f"  • 保证金: {account_info['margin_used_pct']:.1f}%\n")
    lines.append(f"  • 持仓: {account_info['position_count']}个\n\n")

    # 决策列表
    if decisions and len(decisions) > 0:
        lines.append(f"📋 <b>AI 交易决策</b> (共{len(decisions)}条):\n\n")

        for i, decision in enumerate(decisions, 1):
            action = decision.get('action', 'unknown')
            symbol = decision.get('symbol', 'N/A')
            reasoning = escape_html(decision.get('reasoning', '无'))

            # 动作图标
            action_emoji = {
                'open_long': '📈',
                'open_short': '📉',
                'close_long': '✅',
                'close_short': '✅',
                'hold': '⏸',
                'wait': '⏰'
            }.get(action, '❓')

            # 动作中文
            action_cn = {
                'open_long': '开多',
                'open_short': '开空',
                'close_long': '平多',
                'close_short': '平空',
                'hold': '持有',
                'wait': '观望'
            }.get(action, action)

            lines.append(f"{action_emoji} <b>决策 #{i}: {symbol} - {action_cn}</b>\n")

            # 开仓决策的详细信息
            if action in ['open_long', 'open_short']:
                leverage = decision.get('leverage', 0)
                position_size = decision.get('position_size_usd', 0)
                stop_loss = decision.get('stop_loss', 0)
                take_profit = decision.get('take_profit', 0)
                confidence = decision.get('confidence', 0)
                risk_usd = decision.get('risk_usd', 0)

                lines.append(f"  • 杠杆: {leverage}x\n")
                lines.append(f"  • 仓位: ${position_size:,.2f}\n")
                lines.append(f"  • 止损: ${stop_loss:,.2f}\n")
                lines.append(f"  • 止盈: ${take_profit:,.2f}\n")
                lines.append(f"  • 风险: ${risk_usd:,.2f}\n")
                lines.append(f"  • 信心度: {confidence}%\n")

            lines.append(f"  • 理由: {reasoning}\n\n")
    else:
        lines.append("⏰ <b>本周期无交易决策</b> (观望或持有)\n\n")

    lines.append("━" * 40)
    lines.append("\n")

    # 思维链（完整显示，不截断）
    lines.append("💭 <b>AI 分析过程</b>:\n")

    # Telegram 消息有长度限制（4096字符），需要分段发送
    # 但我们先尝试完整显示，如果超长则在 btc_trading_monitor.py 中分段
    cot_escaped = escape_html(cot_trace)

    # 如果太长（>3000字符），只发送摘要到 Telegram
    if len(cot_escaped) > 3000:
        lines.append(f"<pre>{cot_escaped[:3000]}</pre>\n")
        lines.append(f"<i>... 还有 {len(cot_escaped) - 3000} 字符</i>\n")
        lines.append("<i>💾 完整分析已保存到日志，请查看 analysis_logs/</i>\n")
    else:
        lines.append(f"<pre>{cot_escaped}</pre>\n")

    return "".join(lines)
