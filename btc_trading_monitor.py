"""
BTC 交易决策监控机器人
整合市场数据获取、DeepSeek AI 交易决策分析、图表生成和 Telegram 推送
支持完整的开单、止盈、止损决策（文本输出，不对接交易所）
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, Optional, List

from market_data import MarketData
from prompts_trading import build_system_prompt, build_user_prompt, format_trading_result
from deepseek_client import DeepSeekClient


class BTCTradingMonitor:
    """BTC 交易决策监控器"""

    def __init__(self, config_path: str = 'config.json'):
        """
        初始化监控器

        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = self._load_config(config_path)

        # 初始化市场数据获取器
        self.market_data = MarketData()

        # 初始化 DeepSeek 客户端
        self.deepseek_client = DeepSeekClient(
            api_key=self.config['deepseek_api_key'],
            base_url=self.config.get('deepseek_base_url', 'https://api.deepseek.com/v1'),
            model=self.config.get('deepseek_model', 'deepseek-chat')
        )

        # Telegram Bot 配置
        self.telegram_bot_token = self.config.get('telegram_bot_token')
        self.telegram_chat_id = self.config.get('telegram_chat_id')

        # Chart API 配置
        self.chart_api_key = self.config.get('chart_api_key')
        self.chart_api_url = self.config.get('chart_api_url', 'https://api.chart-img.com/v2/tradingview/advanced-chart')

        # 模拟账户配置
        self.initial_balance = self.config.get('initial_balance', 1000.0)
        self.btc_eth_leverage = self.config.get('btc_eth_leverage', 5)
        self.altcoin_leverage = self.config.get('altcoin_leverage', 5)

        # 运行统计
        self.start_time = datetime.now()
        self.call_count = 0

        # 模拟账户状态
        self.account = {
            'total_equity': self.initial_balance,
            'available_balance': self.initial_balance,
            'total_pnl': 0.0,
            'total_pnl_pct': 0.0,
            'margin_used': 0.0,
            'margin_used_pct': 0.0,
            'position_count': 0
        }

        # 模拟持仓
        self.positions = []

        # 历史交易记录（用于计算夏普比率）
        self.trade_history = []

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _calculate_sharpe_ratio(self) -> float:
        """
        计算夏普比率（简化版本）

        Returns:
            夏普比率
        """
        if len(self.trade_history) < 2:
            return 0.0

        # 提取收益率序列
        returns = [trade['pnl_pct'] for trade in self.trade_history if 'pnl_pct' in trade]

        if len(returns) < 2:
            return 0.0

        # 计算平均收益和标准差
        import statistics
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)

        # 夏普比率 = 平均收益 / 收益波动率
        if std_return == 0:
            return 0.0

        return mean_return / std_return

    def _parse_ai_decisions(self, ai_response: str) -> tuple:
        """
        解析 AI 响应，提取思维链和决策列表

        Args:
            ai_response: AI 的原始响应

        Returns:
            (cot_trace, decisions) 元组
        """
        # 提取思维链（JSON 之前的内容）
        json_start = ai_response.find('[')
        if json_start > 0:
            cot_trace = ai_response[:json_start].strip()
        else:
            cot_trace = ai_response
            return cot_trace, []

        # 提取 JSON 决策列表
        try:
            # 找到匹配的右括号
            bracket_count = 0
            json_end = -1
            for i in range(json_start, len(ai_response)):
                if ai_response[i] == '[':
                    bracket_count += 1
                elif ai_response[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        json_end = i + 1
                        break

            if json_end == -1:
                print("  ⚠️ 无法找到完整的 JSON 数组")
                return cot_trace, []

            json_str = ai_response[json_start:json_end].strip()

            # 修复中文引号
            json_str = json_str.replace('"', '"').replace('"', '"')
            json_str = json_str.replace(''', "'").replace(''', "'")

            decisions = json.loads(json_str)
            return cot_trace, decisions

        except json.JSONDecodeError as e:
            print(f"  ⚠️ JSON 解析失败: {e}")
            print(f"  JSON 内容: {ai_response[json_start:json_start+200]}...")
            return cot_trace, []

    def run_analysis(self) -> Dict:
        """
        执行一次完整的交易决策分析

        Returns:
            分析结果字典
        """
        print(f"\n{'='*60}")
        print(f"🔍 开始第 {self.call_count + 1} 次分析 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        # 1. 获取市场数据
        print("📊 正在获取 BTC 市场数据...")
        try:
            btc_data = self.market_data.get_btc_complete_data()
            print(f"✓ 市场数据获取成功")
            print(f"  当前价格: ${btc_data['current_price']:,.2f}")
            print(f"  15分钟涨跌: {btc_data['price_changes']['15m']:+.2f}%")
            print(f"  1小时涨跌: {btc_data['price_changes']['1h']:+.2f}%")
            print(f"  4小时涨跌: {btc_data['price_changes']['4h']:+.2f}%\n")
        except Exception as e:
            print(f"❌ 市场数据获取失败: {e}")
            return {'success': False, 'error': str(e)}

        # 2. 构建 Prompts
        print("🔨 正在构建 AI 交易决策提示词...")
        runtime_minutes = int((datetime.now() - self.start_time).total_seconds() / 60)
        self.call_count += 1

        # 计算夏普比率
        sharpe_ratio = self._calculate_sharpe_ratio()

        system_prompt = build_system_prompt(
            account_equity=self.account['total_equity'],
            btc_eth_leverage=self.btc_eth_leverage,
            altcoin_leverage=self.altcoin_leverage
        )

        user_prompt = build_user_prompt(
            market_data=btc_data,
            runtime_minutes=runtime_minutes,
            call_count=self.call_count,
            account_info=self.account,
            positions=self.positions,
            sharpe_ratio=sharpe_ratio
        )
        print("✓ 提示词构建完成\n")

        # 3. 调用 DeepSeek AI 分析
        print("🤖 正在调用 DeepSeek AI 进行交易决策分析...")
        try:
            ai_response = self.deepseek_client.call_with_messages(system_prompt, user_prompt)
            print("✓ AI 分析完成\n")
        except Exception as e:
            print(f"❌ AI 调用失败: {e}")
            return {'success': False, 'error': str(e)}

        # 4. 解析 AI 响应
        print("📝 正在解析 AI 交易决策...")
        cot_trace, decisions = self._parse_ai_decisions(ai_response)

        # 打印完整的 AI 分析过程
        print("\n" + "="*60)
        print("💭 AI 完整分析过程:")
        print("="*60)
        print(cot_trace)
        print("="*60 + "\n")

        if not decisions or len(decisions) == 0:
            print("  ⚠️ 本周期无具体交易决策（观望或持有）")
            decisions = []
        else:
            print(f"✓ 解析成功，共 {len(decisions)} 条决策")
            for i, decision in enumerate(decisions, 1):
                action = decision.get('action', 'unknown')
                symbol = decision.get('symbol', 'N/A')
                print(f"  {i}. {symbol}: {action}")

        print()

        # 5. 生成图表
        print("📈 正在生成 BTC 图表...")
        chart_path = self._generate_chart()
        if chart_path:
            print(f"✓ 图表生成成功: {chart_path}\n")
        else:
            print("⚠️ 图表生成失败\n")

        # 6. 发送到 Telegram
        if self.telegram_bot_token and self.telegram_chat_id:
            print("📤 正在发送到 Telegram...")
            message = format_trading_result(cot_trace, decisions, self.account)
            success = self._send_to_telegram(message, chart_path)
            if success:
                print("✓ Telegram 消息发送成功\n")
            else:
                print("❌ Telegram 消息发送失败\n")
        else:
            print("⚠️ 未配置 Telegram，跳过发送\n")

        # 7. 保存结果
        result = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'market_data': {
                'current_price': btc_data['current_price'],
                'price_changes': btc_data['price_changes']
            },
            'account': self.account,
            'positions': self.positions,
            'sharpe_ratio': sharpe_ratio,
            'cot_trace': cot_trace,
            'decisions': decisions,
            'chart_path': chart_path
        }

        self._save_analysis_log(result)

        print(f"{'='*60}")
        print(f"✅ 第 {self.call_count} 次分析完成")
        print(f"💰 账户净值: ${self.account['total_equity']:,.2f} | 盈亏: {self.account['total_pnl_pct']:+.2f}%")
        print(f"📊 夏普比率: {sharpe_ratio:.2f}")
        print(f"{'='*60}\n")

        return result

    def _generate_chart(self) -> Optional[str]:
        """
        生成 BTC 图表

        Returns:
            图表文件路径，失败返回 None
        """
        if not self.chart_api_key:
            print("  未配置 Chart API，跳过图表生成")
            return None

        try:
            # 构建请求体
            payload = {
                "symbol": "BINANCE:BTCUSDT",
                "interval": self.config.get('chart_interval', '1h'),
                "theme": "dark",
                "width": 800,
                "height": 600,
                "studies": [
                    {"name": "Volume", "forceOverlay": True},
                    {"name": "MACD"},
                    {"name": "Relative Strength Index"}
                ]
            }

            headers = {
                "x-api-key": self.chart_api_key,
                "Content-Type": "application/json"
            }

            # 发送请求
            response = requests.post(
                self.chart_api_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                # 保存图表
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                chart_path = f"btc_chart_{timestamp}.png"
                with open(chart_path, 'wb') as f:
                    f.write(response.content)
                return chart_path
            else:
                print(f"  Chart API 错误 {response.status_code}: {response.text[:200]}")
                return None

        except Exception as e:
            print(f"  图表生成异常: {e}")
            return None

    def _send_to_telegram(self, message: str, chart_path: Optional[str] = None) -> bool:
        """
        发送消息到 Telegram

        Args:
            message: 消息文本
            chart_path: 图表文件路径（可选）

        Returns:
            是否发送成功
        """
        try:
            # 发送文本消息（使用 HTML 模式）
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, json=data, timeout=10)

            if response.status_code != 200:
                print(f"  文本消息发送失败: {response.text}")
                # 尝试不使用格式化
                print(f"  尝试发送纯文本...")
                data['parse_mode'] = None
                response = requests.post(url, json=data, timeout=10)
                if response.status_code != 200:
                    print(f"  纯文本发送也失败: {response.text}")
                    return False

            # 发送图片（如果有）
            if chart_path and os.path.exists(chart_path):
                url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendPhoto"
                with open(chart_path, 'rb') as photo:
                    files = {'photo': photo}
                    data = {'chat_id': self.telegram_chat_id}
                    response = requests.post(url, data=data, files=files, timeout=30)

                if response.status_code != 200:
                    print(f"  图片发送失败: {response.text}")
                    return False

            return True

        except Exception as e:
            print(f"  Telegram 发送异常: {e}")
            return False

    def _save_analysis_log(self, result: Dict):
        """
        保存分析日志

        Args:
            result: 分析结果
        """
        try:
            # 创建日志目录
            log_dir = 'analysis_logs'
            os.makedirs(log_dir, exist_ok=True)

            # 保存为 JSON Lines 格式
            log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.jsonl")

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        except Exception as e:
            print(f"⚠️ 日志保存失败: {e}")

    def run_loop(self, interval_minutes: int = 5):
        """
        持续运行监控循环

        Args:
            interval_minutes: 分析间隔（分钟）
        """
        print(f"\n🚀 BTC 交易决策监控机器人启动")
        print(f"📊 分析间隔: {interval_minutes} 分钟")
        print(f"🤖 AI 模型: {self.config.get('deepseek_model', 'deepseek-chat')}")
        print(f"💰 初始资金: ${self.initial_balance:,.2f}")
        print(f"⚡ 杠杆配置: BTC/ETH {self.btc_eth_leverage}x | 山寨 {self.altcoin_leverage}x")
        if self.telegram_bot_token:
            print(f"📱 Telegram 推送: 已启用")
        else:
            print(f"📱 Telegram 推送: 未配置")
        print(f"\n按 Ctrl+C 停止运行\n")

        try:
            while True:
                # 执行分析
                result = self.run_analysis()

                # 等待下一次分析
                wait_seconds = interval_minutes * 60
                next_time = datetime.fromtimestamp(time.time() + wait_seconds).strftime('%H:%M:%S')
                print(f"⏰ 等待 {interval_minutes} 分钟后进行下一次分析...")
                print(f"   下次分析时间: {next_time}\n")

                time.sleep(wait_seconds)

        except KeyboardInterrupt:
            print("\n\n👋 收到停止信号，正在退出...")
            print(f"📊 总共完成 {self.call_count} 次分析")
            print(f"💰 最终账户净值: ${self.account['total_equity']:,.2f}")
            print(f"📈 总盈亏: {self.account['total_pnl_pct']:+.2f}%")
            print("感谢使用 BTC 交易决策监控机器人！\n")


def main():
    """主函数"""
    # 读取配置文件路径
    config_path = os.getenv('CONFIG_PATH', 'config.json')

    try:
        # 创建监控器
        monitor = BTCTradingMonitor(config_path)

        # 启动监控循环
        interval = monitor.config.get('analysis_interval_minutes', 5)
        monitor.run_loop(interval_minutes=interval)

    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        print("\n请先创建 config.json 配置文件！")
        print("参考 config.json.example 进行配置\n")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
