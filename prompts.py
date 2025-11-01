"""
Prompt 构建模块 - 多时间框架版本
从 NOFX 项目提取的 System Prompt 和 User Prompt 构建逻辑
专门用于 BTC 盯盘分析（无交易逻辑，仅分析）

增强版：支持 3分钟、15分钟、1小时、4小时 四个时间框架
"""

from datetime import datetime
from typing import Dict, List


def build_system_prompt() -> str:
    """
    构建 System Prompt（固定规则）
    改编自 NOFX 的 buildSystemPrompt() 函数
    针对盯盘分析场景优化（移除交易相关的指令）
    """
    prompt = """你是专业的加密货币市场分析AI，专注于 BTC 多时间框架市场分析和趋势预测。

# 🎯 核心任务

你的任务是：
1. **多时间框架分析**：结合 3分钟、15分钟、1小时、4小时 四个时间框架进行综合分析
2. **识别关键信号**：找出重要的技术指标信号和趋势共振
3. **预测短中期趋势**：基于多时间框架数据判断未来走势
4. **风险提示**：标注潜在的风险点和关键价位

**重要**: 这是纯分析任务，你不需要给出交易建议，只需要客观分析市场状态。

---

# 📊 你拥有的完整多时间框架数据

你拥有 **4个时间框架** 的完整数据：

1. **3分钟级别** (超短期)：
   - 30个数据点 = 90分钟历史
   - 用于：超短期动量、快速反转信号

2. **15分钟级别** (短期)：
   - 24个数据点 = 6小时历史
   - 用于：短期趋势、日内关键价位

3. **1小时级别** (中短期)：
   - 24个数据点 = 1天历史
   - 用于：日内趋势、支撑阻力位

4. **4小时级别** (中长期)：
   - 20个数据点 = 3.3天历史
   - 用于：中期趋势、大级别支撑阻力

**每个时间框架都包含**：
- 价格序列（开、高、低、收）
- EMA20、EMA50 均线序列
- MACD（快线、慢线、柱状图）序列
- RSI(7)、RSI(14) 序列
- ATR(14) 波动率序列
- 布林带（上轨、中轨、下轨）
- 成交量及成交量均线

---

# 🔍 多时间框架分析方法

**趋势共振分析**：
- 多个时间框架趋势方向一致 = 强趋势
- 短周期与长周期趋势相反 = 可能反转或回调
- 观察各周期的 EMA20/EMA50 排列

**支撑阻力识别**：
- 长周期（4h）的关键价位更重要
- 多周期重合的价位 = 强支撑/阻力
- 结合布林带上下轨

**动量分析**：
- 短周期（3m/15m）的 RSI 用于判断超买超卖
- 长周期（1h/4h）的 MACD 用于判断趋势强度
- 观察 MACD 柱状图的变化

**背离识别**：
- 价格创新高/新低，但指标不创 = 背离
- 多周期同时出现背离 = 强信号

**布林带分析**：
- 价格位置（上轨/中轨/下轨）
- 布林带宽度（收缩/扩张）

---

# 📋 分析流程

1. **多时间框架趋势判断**：
   - 4h：当前大趋势方向
   - 1h：日内趋势方向
   - 15m：短期走势方向
   - 3m：即时动量方向

2. **趋势一致性检查**：
   - 所有周期同向 = 强趋势，顺势而为
   - 短期与长期相反 = 可能回调/反转

3. **关键信号识别**：
   - 金叉/死叉（哪个周期？）
   - 突破关键均线
   - RSI 超买超卖
   - 背离信号

4. **支撑阻力位标注**：
   - 基于多周期重合的关键价位
   - 布林带上下轨

5. **趋势预测**：
   - 短期（15m-1h）：可能走势
   - 中期（4h）：大趋势方向

---

# 📤 输出格式

**第一步: 思维链分析（简洁清晰的文本）**

用简洁的语言分析，包括：
- 各时间框架趋势状态
- 多周期共振/背离情况
- 关键技术信号
- 趋势预测依据
- 风险提示

**第二步: JSON格式的结构化总结**

```json
{
  "market_state": "上涨趋势 | 下跌趋势 | 震荡整理 | 趋势转折",
  "timeframe_analysis": {
    "3m": "趋势描述",
    "15m": "趋势描述",
    "1h": "趋势描述",
    "4h": "趋势描述"
  },
  "trend_resonance": "多周期共振 | 短期回调 | 趋势分歧",
  "short_term_trend": "未来1-2小时走势预测",
  "mid_term_trend": "未来4-6小时走势预测",
  "key_levels": {
    "support": 支撑位价格,
    "resistance": 阻力位价格
  },
  "confidence": 75,
  "key_signals": [
    "信号1",
    "信号2"
  ],
  "risk_warning": "风险提示",
  "summary": "一句话总结"
}
```

---

**记住**:
- 优先分析长周期（4h/1h）确定大趋势
- 用短周期（15m/3m）寻找入场/出场时机
- 多周期共振 = 高概率方向
- 标注不确定性和风险
"""
    return prompt


def build_user_prompt(market_data: Dict, runtime_minutes: int = 0, call_count: int = 0) -> str:
    """
    构建 User Prompt（动态市场数据 - 多时间框架版本）

    Args:
        market_data: 市场数据字典（来自 market_data.py）
        runtime_minutes: 系统运行时长（分钟）
        call_count: AI 调用次数

    Returns:
        格式化的 user prompt 字符串
    """
    lines = []

    # === 系统状态 ===
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"**时间**: {current_time} | **周期**: #{call_count} | **运行**: {runtime_minutes}分钟\n")

    # === BTC 市场概览 ===
    lines.append("## 📊 BTC 市场概览\n")
    lines.append(f"**当前价格**: ${market_data['current_price']:,.2f}\n")

    # 多时间框架价格变化
    pc = market_data['price_changes']
    lines.append("**多时间框架涨跌**:")
    lines.append(f"  • 15分钟: {pc['15m']:+.2f}%")
    lines.append(f"  • 1小时: {pc['1h']:+.2f}%")
    lines.append(f"  • 4小时: {pc['4h']:+.2f}%")
    lines.append(f"  • 24小时: {pc['24h']:+.2f}%\n")

    # === 多时间框架技术分析 ===
    lines.append("## 📈 多时间框架技术分析\n")
    lines.append("你拥有完整的4个时间框架数据，可以进行全面的趋势共振分析：\n")

    # 函数：格式化时间框架数据
    def format_timeframe(tf_data, emoji, name, description):
        """格式化单个时间框架的数据"""
        tf_lines = []
        tf_lines.append(f"### {emoji} {name} - {description}\n")

        current = tf_data['current']

        # 当前关键指标
        tf_lines.append(f"**当前值** (最新K线):")
        tf_lines.append(f"  • 价格: ${current['price']:,.2f}")

        # EMA 趋势判断
        ema_trend = "↑ 上升" if current['price'] > current['ema20'] > current['ema50'] else \
                   "↓ 下降" if current['price'] < current['ema20'] < current['ema50'] else \
                   "↔ 震荡"
        tf_lines.append(f"  • EMA趋势: {ema_trend} (EMA20: ${current['ema20']:,.2f} | EMA50: ${current['ema50']:,.2f})")

        # MACD 状态
        macd_status = "金叉" if current['macd'] > 0 else "死叉"
        tf_lines.append(f"  • MACD: {current['macd']:.4f} ({macd_status})")

        # RSI 状态
        rsi_status = "超买" if current['rsi14'] > 70 else "超卖" if current['rsi14'] < 30 else "中性"
        tf_lines.append(f"  • RSI(7): {current['rsi7']:.2f} | RSI(14): {current['rsi14']:.2f} ({rsi_status})")

        tf_lines.append(f"  • ATR(14): {current['atr14']:.2f} (波动率)")

        # 成交量
        vol_ratio = (current['volume'] / current['volume_ma'] * 100) if current['volume_ma'] > 0 else 100
        vol_status = "放量" if vol_ratio > 120 else "缩量" if vol_ratio < 80 else "正常"
        tf_lines.append(f"  • 成交量: {current['volume']:,.0f} ({vol_status}, {vol_ratio:.0f}% of MA)")
        tf_lines.append("")

        # 布林带位置
        bb_upper = tf_data['bb_upper'][-1]
        bb_lower = tf_data['bb_lower'][-1]
        bb_position = ((current['price'] - bb_lower) / (bb_upper - bb_lower) * 100) if bb_upper > bb_lower else 50
        bb_width = ((bb_upper - bb_lower) / current['price'] * 100) if current['price'] > 0 else 0

        bb_pos_desc = "接近上轨" if bb_position > 80 else "接近下轨" if bb_position < 20 else "中间位置"
        tf_lines.append(f"**布林带**:")
        tf_lines.append(f"  • 上轨: ${bb_upper:.2f} | 下轨: ${bb_lower:.2f}")
        tf_lines.append(f"  • 价格位置: {bb_position:.1f}% ({bb_pos_desc})")
        tf_lines.append(f"  • 带宽: {bb_width:.2f}%")
        tf_lines.append("")

        # 序列数据（最近10个点）
        n = min(10, len(tf_data['prices']))
        tf_lines.append(f"**序列数据** (最近{n}个点，共{tf_data['data_points']}个点可用):")
        tf_lines.append(f"  • 价格: {[f'{p:.2f}' for p in tf_data['prices'][-n:]]}")
        tf_lines.append(f"  • MACD柱: {[f'{v:.3f}' for v in tf_data['macd_hist'][-n:]]}")
        tf_lines.append(f"  • RSI(14): {[f'{v:.1f}' for v in tf_data['rsi14'][-n:]]}")
        tf_lines.append("")

        return "\n".join(tf_lines)

    # 展示各时间框架（按从短到长的顺序）
    lines.append(format_timeframe(market_data['timeframe_3m'], "⚡", "3分钟级别", "超短期 (覆盖90分钟, 30个数据点)"))
    lines.append(format_timeframe(market_data['timeframe_15m'], "🔥", "15分钟级别", "短期 (覆盖6小时, 24个数据点)"))
    lines.append(format_timeframe(market_data['timeframe_1h'], "📊", "1小时级别", "中短期 (覆盖1天, 24个数据点)"))
    lines.append(format_timeframe(market_data['timeframe_4h'], "🌊", "4小时级别", "中长期 (覆盖3.3天, 20个数据点)"))

    # === 市场资金面 ===
    lines.append("## 💰 市场资金面\n")
    oi = market_data['open_interest']
    lines.append(f"**持仓量**: {oi['latest']:,.0f} BTC")
    lines.append(f"**资金费率**: {market_data['funding_rate']:.6f} ({market_data['funding_rate']*100:.4f}%)")

    # 资金费率解读
    if market_data['funding_rate'] > 0.0001:
        lines.append(f"  → 做多资金费率偏高，市场看多情绪较强")
    elif market_data['funding_rate'] < -0.0001:
        lines.append(f"  → 做空资金费率偏高，市场看空情绪较强")
    else:
        lines.append(f"  → 资金费率接近中性，多空相对平衡")
    lines.append("")

    # === 请求AI分析 ===
    lines.append("---\n")
    lines.append("**请基于以上4个时间框架的完整数据，进行深度多时间框架分析：**")
    lines.append("")
    lines.append("1. **多周期趋势判断**: 各时间框架分别处于什么趋势？")
    lines.append("2. **趋势共振分析**: 多个周期是否共振？还是出现背离？")
    lines.append("3. **关键技术信号**: 哪个周期出现了什么重要信号？")
    lines.append("4. **支撑阻力位**: 基于多周期分析，标注关键价位")
    lines.append("5. **短中期预测**: 未来1-2小时和4-6小时的可能走势")
    lines.append("6. **风险提示**: 潜在风险点和不确定性")
    lines.append("")
    lines.append("**输出格式**: 思维链分析 + JSON结构化总结（包含 timeframe_analysis 字段）\n")

    return "\n".join(lines)


def format_analysis_result(cot_trace: str, json_result: Dict) -> str:
    """
    格式化分析结果用于 Telegram 消息（HTML 格式）

    Args:
        cot_trace: 思维链分析文本
        json_result: 结构化分析结果（JSON）

    Returns:
        HTML 格式的消息字符串
    """
    lines = []

    # 转义 HTML 特殊字符
    def escape_html(text):
        if not isinstance(text, str):
            text = str(text)
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    lines.append("🤖 <b>BTC 多时间框架分析报告</b>\n")
    lines.append("━" * 40)
    lines.append("")

    # 一句话总结
    if 'summary' in json_result:
        summary = escape_html(json_result['summary'])
        lines.append(f"📌 <b>总结</b>: {summary}\n")

    # 市场状态
    if 'market_state' in json_result:
        state_emoji = {
            "上涨趋势": "📈",
            "下跌趋势": "📉",
            "震荡整理": "↔️",
            "趋势转折": "🔄"
        }
        emoji = state_emoji.get(json_result['market_state'], "📊")
        market_state = escape_html(json_result['market_state'])
        lines.append(f"{emoji} <b>市场状态</b>: {market_state}\n")

    # 多时间框架分析
    if 'timeframe_analysis' in json_result:
        tfa = json_result['timeframe_analysis']
        lines.append("⏱ <b>多时间框架趋势</b>:")
        if '3m' in tfa:
            lines.append(f"  • 3分钟: {escape_html(tfa['3m'])}")
        if '15m' in tfa:
            lines.append(f"  • 15分钟: {escape_html(tfa['15m'])}")
        if '1h' in tfa:
            lines.append(f"  • 1小时: {escape_html(tfa['1h'])}")
        if '4h' in tfa:
            lines.append(f"  • 4小时: {escape_html(tfa['4h'])}")
        lines.append("")

    # 趋势共振
    if 'trend_resonance' in json_result:
        resonance = escape_html(json_result['trend_resonance'])
        lines.append(f"🔄 <b>趋势共振</b>: {resonance}\n")

    # 趋势预测
    if 'short_term_trend' in json_result:
        trend = escape_html(json_result['short_term_trend'])
        lines.append(f"⏰ <b>短期(1-2h)</b>: {trend}")
    if 'mid_term_trend' in json_result:
        trend = escape_html(json_result['mid_term_trend'])
        lines.append(f"⏳ <b>中期(4-6h)</b>: {trend}\n")

    # 关键价位
    if 'key_levels' in json_result:
        levels = json_result['key_levels']
        lines.append("🎯 <b>关键价位</b>:")
        if 'resistance' in levels:
            lines.append(f"  • 阻力位: ${levels['resistance']:,.2f}")
        if 'support' in levels:
            lines.append(f"  • 支撑位: ${levels['support']:,.2f}")
        lines.append("")

    # 关键信号
    if 'key_signals' in json_result and json_result['key_signals']:
        lines.append("⚡ <b>关键信号</b>:")
        for signal in json_result['key_signals']:
            signal_text = escape_html(signal)
            lines.append(f"  • {signal_text}")
        lines.append("")

    # 风险提示
    if 'risk_warning' in json_result:
        warning = escape_html(json_result['risk_warning'])
        lines.append(f"⚠️ <b>风险提示</b>: {warning}\n")

    # 信心度
    if 'confidence' in json_result:
        confidence = json_result['confidence']
        confidence_level = "高" if confidence >= 80 else "中" if confidence >= 60 else "低"
        lines.append(f"📊 <b>分析信心度</b>: {confidence}% ({confidence_level})\n")

    lines.append("━" * 40)
    lines.append("")

    # 思维链（限制长度）
    lines.append("💭 <b>AI 分析过程</b>:")
    cot_preview = cot_trace[:400] if len(cot_trace) > 400 else cot_trace
    cot_escaped = escape_html(cot_preview)
    lines.append(f"<pre>{cot_escaped}</pre>")
    if len(cot_trace) > 400:
        lines.append("<i>... (完整分析已保存到日志)</i>")

    return "\n".join(lines)
