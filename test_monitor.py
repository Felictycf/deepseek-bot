"""
BTC 盯盘机器人 - 单次测试脚本
用于测试系统是否正常工作，只运行一次分析
"""

from btc_monitor import BTCMonitor


def test_single_run():
    """测试单次运行"""
    print("\n" + "=" * 60)
    print("🧪 BTC 盯盘机器人 - 单次测试")
    print("=" * 60 + "\n")

    try:
        # 创建监控器
        monitor = BTCMonitor('config.json')

        # 运行单次分析
        result = monitor.run_analysis()

        # 输出结果
        print("\n" + "=" * 60)
        print("📋 测试结果总结")
        print("=" * 60 + "\n")

        if result.get('success'):
            print("✅ 测试成功！\n")

            # 显示市场数据
            market_data = result['market_data']
            print(f"📊 市场数据:")
            print(f"  当前价格: ${market_data['current_price']:,.2f}")
            print(f"  1小时涨跌: {market_data['price_change_1h']:+.2f}%")
            print(f"  4小时涨跌: {market_data['price_change_4h']:+.2f}%")
            print()

            # 显示 AI 分析结果
            json_result = result.get('json_result', {})
            if json_result:
                print(f"🤖 AI 分析:")
                print(f"  市场状态: {json_result.get('market_state', 'N/A')}")
                print(f"  短期趋势: {json_result.get('short_term_trend', 'N/A')}")
                print(f"  信心度: {json_result.get('confidence', 0)}%")
                print()

            # 显示图表
            if result.get('chart_path'):
                print(f"📈 图表已生成: {result['chart_path']}")
            else:
                print(f"⚠️  图表生成失败或未配置")
            print()

            print("✓ 所有组件工作正常！")
            print("\n可以运行 python btc_monitor.py 启动持续监控")

        else:
            print(f"❌ 测试失败: {result.get('error', '未知错误')}")

    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60 + "\n")


if __name__ == '__main__':
    test_single_run()
