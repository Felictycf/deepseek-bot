"""
快速测试 Telegram 消息发送和图表生成
"""

from btc_monitor import BTCMonitor


def test_telegram_and_chart():
    """测试 Telegram 发送和图表生成"""
    print("\n" + "=" * 60)
    print("🧪 测试 Telegram 和图表功能")
    print("=" * 60 + "\n")

    try:
        # 创建监控器
        monitor = BTCMonitor('config.json')

        # 测试消息格式化（模拟 AI 返回结果）
        print("📝 测试消息格式化...")
        test_json_result = {
            'market_state': '震荡整理',
            'summary': 'BTC 短期震荡，等待方向选择',
            'short_term_trend': '1小时内可能在 109,000 - 111,000 区间震荡',
            'mid_term_trend': '4小时级别保持横盘，等待突破',
            'key_levels': {
                'support': 109000,
                'resistance': 111000
            },
            'key_signals': [
                'MACD 在零轴附近震荡',
                'RSI 处于中性区域 (45-55)',
                '成交量萎缩'
            ],
            'risk_warning': '震荡行情，避免追涨杀跌',
            'confidence': 70
        }

        test_cot = """
当前 BTC 处于明显的震荡整理阶段：

1. 短期动量（3分钟）：
   - 价格在 EMA20 附近来回震荡
   - MACD 在零轴附近反复横跳
   - RSI(7) 在 45-55 区间波动

2. 中期趋势（4小时）：
   - 横盘整理，方向不明
   - 成交量明显萎缩
   - 等待方向选择
"""

        from nofx.deepseek_bot2.temp.prompts import format_analysis_result
        message = format_analysis_result(test_cot, test_json_result)

        print("✓ 消息格式化成功\n")
        print("📋 格式化后的消息:")
        print("-" * 60)
        print(message)
        print("-" * 60)
        print()

        # 测试图表生成
        print("📈 测试图表生成...")
        chart_path = monitor._generate_chart()
        if chart_path:
            print(f"✓ 图表生成成功: {chart_path}\n")
        else:
            print("⚠️ 图表生成失败（可能是 API 配置问题）\n")

        # 测试 Telegram 发送
        print("📤 测试 Telegram 消息发送...")
        success = monitor._send_to_telegram(message, chart_path)

        if success:
            print("✓ Telegram 消息发送成功！\n")
            print("✅ 所有测试通过！")
            print("\n请检查你的 Telegram 接收消息")
        else:
            print("❌ Telegram 消息发送失败")
            print("\n可能的原因：")
            print("  1. Bot Token 或 Chat ID 不正确")
            print("  2. 网络连接问题")
            print("  3. 消息格式仍有问题")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60 + "\n")


if __name__ == '__main__':
    test_telegram_and_chart()
