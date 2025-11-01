"""
API 连接测试脚本
验证市场数据获取是否正常工作
"""

from nofx.deepseek_bot2.temp.market_data import MarketData
import json


def test_api_connections():
    """测试所有 API 连接"""
    print("\n" + "=" * 60)
    print("🧪 API 连接测试")
    print("=" * 60 + "\n")

    try:
        # 1. 初始化市场数据
        print("📊 正在初始化 CCXT Binance 连接...")
        market_data = MarketData()
        print("✓ CCXT 初始化成功\n")

        # 2. 测试 K 线数据获取
        print("📈 测试 K 线数据获取...")
        try:
            klines_3m = market_data._fetch_klines('BTC/USDT', '3m', limit=10)
            print(f"✓ 3分钟 K 线获取成功: {len(klines_3m)} 条数据")
            print(f"  最新价格: ${klines_3m['close'].iloc[-1]:,.2f}\n")
        except Exception as e:
            print(f"❌ K 线获取失败: {e}\n")

        # 3. 测试持仓量获取
        print("💰 测试持仓量获取...")
        try:
            oi_data = market_data._get_open_interest('BTC/USDT')
            print(f"✓ 持仓量获取成功")
            print(f"  持仓量: {oi_data['latest']:,.0f} BTC\n")
        except Exception as e:
            print(f"❌ 持仓量获取失败: {e}\n")

        # 4. 测试资金费率获取
        print("📊 测试资金费率获取...")
        try:
            funding_rate = market_data._get_funding_rate('BTC/USDT')
            print(f"✓ 资金费率获取成功")
            print(f"  资金费率: {funding_rate:.6f} ({funding_rate*100:.4f}%)\n")
        except Exception as e:
            print(f"❌ 资金费率获取失败: {e}\n")

        # 5. 测试完整数据获取
        print("🎯 测试完整市场数据获取...")
        try:
            btc_data = market_data.get_btc_complete_data()
            print(f"✓ 完整数据获取成功\n")

            # 显示摘要
            print("📋 数据摘要:")
            print(f"  当前价格: ${btc_data['current_price']:,.2f}")
            print(f"  1小时涨跌: {btc_data['price_change_1h']:+.2f}%")
            print(f"  4小时涨跌: {btc_data['price_change_4h']:+.2f}%")
            print(f"  EMA20: ${btc_data['current_ema20']:,.2f}")
            print(f"  MACD: {btc_data['current_macd']:.4f}")
            print(f"  RSI(7): {btc_data['current_rsi7']:.2f}")
            print(f"  持仓量: {btc_data['open_interest']['latest']:,.0f}")
            print(f"  资金费率: {btc_data['funding_rate']:.6f}")
            print()

            # 保存到文件
            with open('test_data.json', 'w', encoding='utf-8') as f:
                json.dump(btc_data, f, indent=2, ensure_ascii=False)
            print("💾 完整数据已保存到 test_data.json\n")

        except Exception as e:
            print(f"❌ 完整数据获取失败: {e}\n")
            import traceback
            traceback.print_exc()

        print("=" * 60)
        print("✅ API 测试完成")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_api_connections()
