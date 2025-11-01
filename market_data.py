"""
市场数据获取和技术指标计算模块
使用 CCXT 获取 Binance 数据，并计算与 NOFX 项目相同的技术指标
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import talib


class MarketData:
    """市场数据获取和处理类"""

    def __init__(self, exchange_id='binance'):
        """初始化交易所连接"""
        proxy_url = 'http://127.0.0.1:7890'

        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}  # 使用合约市场
        })
        self.exchange.proxies = {
            'http': proxy_url,
            'https': proxy_url,
        }

    def get_btc_complete_data(self) -> Dict:
        """
        获取 BTC 完整市场数据 - 多时间框架分析

        时间框架覆盖：
        - 3分钟：超短期趋势（最近 2 小时）
        - 15分钟：短期趋势（最近 10 小时）
        - 1小时：中短期趋势（最近 2.5 天）
        - 4小时：中长期趋势（最近 10 天）

        返回结构与 NOFX 的 market.Data 结构一致
        """
        symbol = 'BTC/USDT'

        # 获取多时间框架 K 线数据
        print("  获取 3分钟 K线 (40根 = 2小时)...")
        klines_3m = self._fetch_klines(symbol, '3m', limit=40)

        print("  获取 15分钟 K线 (40根 = 10小时)...")
        klines_15m = self._fetch_klines(symbol, '15m', limit=40)

        print("  获取 1小时 K线 (60根 = 2.5天)...")
        klines_1h = self._fetch_klines(symbol, '1h', limit=60)

        print("  获取 4小时 K线 (60根 = 10天)...")
        klines_4h = self._fetch_klines(symbol, '4h', limit=60)

        # 计算当前指标（基于 3 分钟最新数据）
        current_price = klines_3m['close'].iloc[-1]
        current_ema20 = self._calculate_ema(klines_3m['close'], 20)
        current_macd = self._calculate_macd(klines_3m['close'])
        current_rsi7 = self._calculate_rsi(klines_3m['close'], 7)

        # 计算各时间框架的价格变化百分比
        price_change_15m = self._calculate_price_change(klines_15m['close'], periods=1)   # 1 个 15分钟前
        price_change_1h = self._calculate_price_change(klines_1h['close'], periods=1)     # 1 个 1小时前
        price_change_4h = self._calculate_price_change(klines_4h['close'], periods=1)     # 1 个 4小时前
        price_change_24h = self._calculate_price_change(klines_1h['close'], periods=24)   # 24 个 1小时前

        # 获取持仓量数据
        oi_data = self._get_open_interest(symbol)

        # 获取资金费率
        funding_rate = self._get_funding_rate(symbol)

        # 计算各时间框架的技术指标序列
        print("  计算技术指标...")
        series_3m = self._calculate_timeframe_series(klines_3m, "3m")
        series_15m = self._calculate_timeframe_series(klines_15m, "15m")
        series_1h = self._calculate_timeframe_series(klines_1h, "1h")
        series_4h = self._calculate_timeframe_series(klines_4h, "4h")

        return {
            'symbol': 'BTCUSDT',
            'current_price': current_price,
            'price_changes': {
                '15m': price_change_15m,
                '1h': price_change_1h,
                '4h': price_change_4h,
                '24h': price_change_24h
            },
            'current_ema20': current_ema20,
            'current_macd': current_macd,
            'current_rsi7': current_rsi7,
            'open_interest': oi_data,
            'funding_rate': funding_rate,
            # 多时间框架数据
            'timeframe_3m': series_3m,
            'timeframe_15m': series_15m,
            'timeframe_1h': series_1h,
            'timeframe_4h': series_4h,
            'timestamp': datetime.now().isoformat()
        }

    def _fetch_klines(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """
        获取 K 线数据

        Args:
            symbol: 交易对符号，如 'BTC/USDT'
            timeframe: 时间框架，如 '3m', '4h'
            limit: 获取数量

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"获取 K 线数据失败: {e}")
            raise

    def _calculate_ema(self, close_prices: pd.Series, period: int) -> float:
        """计算 EMA（指数移动平均线）"""
        ema_values = talib.EMA(close_prices.values, timeperiod=period)
        return float(ema_values[-1]) if not np.isnan(ema_values[-1]) else 0.0

    def _calculate_macd(self, close_prices: pd.Series) -> float:
        """计算 MACD"""
        macd, signal, hist = talib.MACD(close_prices.values,
                                        fastperiod=12,
                                        slowperiod=26,
                                        signalperiod=9)
        return float(macd[-1]) if not np.isnan(macd[-1]) else 0.0

    def _calculate_rsi(self, close_prices: pd.Series, period: int) -> float:
        """计算 RSI（相对强弱指标）"""
        rsi_values = talib.RSI(close_prices.values, timeperiod=period)
        return float(rsi_values[-1]) if not np.isnan(rsi_values[-1]) else 0.0

    def _calculate_atr(self, df: pd.DataFrame, period: int) -> float:
        """计算 ATR（平均真实波幅）"""
        atr_values = talib.ATR(df['high'].values,
                               df['low'].values,
                               df['close'].values,
                               timeperiod=period)
        return float(atr_values[-1]) if not np.isnan(atr_values[-1]) else 0.0

    def _calculate_price_change(self, close_prices: pd.Series, periods: int) -> float:
        """
        计算价格变化百分比

        Args:
            close_prices: 收盘价序列
            periods: 回溯周期数

        Returns:
            价格变化百分比
        """
        if len(close_prices) < periods + 1:
            return 0.0

        current_price = close_prices.iloc[-1]
        past_price = close_prices.iloc[-(periods + 1)]

        if past_price > 0:
            return ((current_price - past_price) / past_price) * 100
        return 0.0

    def _get_open_interest(self, symbol: str) -> Dict:
        """
        获取持仓量数据

        Returns:
            {'latest': float, 'average': float}
        """
        try:
            # 使用 CCXT 标准方法获取持仓量
            oi_data = self.exchange.fetch_open_interest(symbol)
            latest_oi = float(oi_data['openInterestAmount']) if 'openInterestAmount' in oi_data else 0.0

            return {
                'latest': latest_oi,
                'average': latest_oi  # 简化处理，可以后续优化计算平均值
            }
        except Exception as e:
            print(f"获取持仓量失败: {e}")
            return {'latest': 0.0, 'average': 0.0}

    def _get_funding_rate(self, symbol: str) -> float:
        """获取资金费率"""
        try:
            # 使用 CCXT 标准方法获取资金费率
            funding_rate = self.exchange.fetch_funding_rate(symbol)
            return float(funding_rate['fundingRate']) if 'fundingRate' in funding_rate else 0.0
        except Exception as e:
            print(f"获取资金费率失败: {e}")
            return 0.0

    def _calculate_intraday_series(self, klines_3m: pd.DataFrame) -> Dict:
        """
        计算日内序列数据（3 分钟数据）
        对应 NOFX 的 IntradayData

        Returns:
            包含各种技术指标序列的字典
        """
        close_prices = klines_3m['close'].values

        # 计算各指标序列
        ema20_values = talib.EMA(close_prices, timeperiod=20)
        macd_values, _, _ = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
        rsi7_values = talib.RSI(close_prices, timeperiod=7)
        rsi14_values = talib.RSI(close_prices, timeperiod=14)

        return {
            'mid_prices': close_prices.tolist()[-20:],  # 最近 20 个价格点
            'ema20_values': [float(v) if not np.isnan(v) else 0 for v in ema20_values[-20:]],
            'macd_values': [float(v) if not np.isnan(v) else 0 for v in macd_values[-20:]],
            'rsi7_values': [float(v) if not np.isnan(v) else 0 for v in rsi7_values[-20:]],
            'rsi14_values': [float(v) if not np.isnan(v) else 0 for v in rsi14_values[-20:]]
        }

    def _calculate_longer_term_data(self, klines_4h: pd.DataFrame) -> Dict:
        """
        计算长期数据（4 小时数据）
        对应 NOFX 的 LongerTermData

        Returns:
            包含长期技术指标的字典
        """
        close_prices = klines_4h['close'].values

        # 计算 EMA
        ema20 = self._calculate_ema(klines_4h['close'], 20)
        ema50 = self._calculate_ema(klines_4h['close'], 50)

        # 计算 ATR
        atr3 = self._calculate_atr(klines_4h, 3)
        atr14 = self._calculate_atr(klines_4h, 14)

        # 计算成交量
        current_volume = klines_4h['volume'].iloc[-1]
        average_volume = klines_4h['volume'].mean()

        # 计算 MACD 和 RSI 序列
        macd_values, _, _ = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
        rsi14_values = talib.RSI(close_prices, timeperiod=14)

        return {
            'ema20': ema20,
            'ema50': ema50,
            'atr3': atr3,
            'atr14': atr14,
            'current_volume': float(current_volume),
            'average_volume': float(average_volume),
            'macd_values': [float(v) if not np.isnan(v) else 0 for v in macd_values[-10:]],
            'rsi14_values': [float(v) if not np.isnan(v) else 0 for v in rsi14_values[-10:]]
        }

    def _calculate_timeframe_series(self, klines: pd.DataFrame, timeframe: str) -> Dict:
        """
        计算单个时间框架的完整技术指标序列（统一处理）

        Args:
            klines: K线数据 DataFrame
            timeframe: 时间框架标识 ("3m", "15m", "1h", "4h")

        Returns:
            包含该时间框架所有技术指标的字典
        """
        close_prices = klines['close'].values
        high_prices = klines['high'].values
        low_prices = klines['low'].values
        volumes = klines['volume'].values

        # 决定返回多少个数据点（短周期返回更多）
        if timeframe == "3m":
            data_points = 30  # 30个点 = 90分钟
        elif timeframe == "15m":
            data_points = 24  # 24个点 = 6小时
        elif timeframe == "1h":
            data_points = 24  # 24个点 = 1天
        else:  # 4h
            data_points = 20  # 20个点 = 3.3天

        # 计算技术指标序列
        ema20_values = talib.EMA(close_prices, timeperiod=20)
        ema50_values = talib.EMA(close_prices, timeperiod=50)
        macd_values, macd_signal, macd_hist = talib.MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
        rsi7_values = talib.RSI(close_prices, timeperiod=7)
        rsi14_values = talib.RSI(close_prices, timeperiod=14)
        atr14_values = talib.ATR(high_prices, low_prices, close_prices, timeperiod=14)

        # 布林带
        upper_band, middle_band, lower_band = talib.BBANDS(close_prices, timeperiod=20, nbdevup=2, nbdevdn=2)

        # 成交量均线
        volume_ma = talib.SMA(volumes, timeperiod=20)

        # 转换为 Python 列表，处理 NaN
        def to_list(arr, n):
            """转换数组为列表，取最后 n 个点"""
            return [float(v) if not np.isnan(v) else 0 for v in arr[-n:]]

        return {
            'timeframe': timeframe,
            'data_points': data_points,
            # 价格数据
            'prices': to_list(close_prices, data_points),
            'highs': to_list(high_prices, data_points),
            'lows': to_list(low_prices, data_points),
            # 均线
            'ema20': to_list(ema20_values, data_points),
            'ema50': to_list(ema50_values, data_points),
            # MACD
            'macd': to_list(macd_values, data_points),
            'macd_signal': to_list(macd_signal, data_points),
            'macd_hist': to_list(macd_hist, data_points),
            # RSI
            'rsi7': to_list(rsi7_values, data_points),
            'rsi14': to_list(rsi14_values, data_points),
            # ATR
            'atr14': to_list(atr14_values, data_points),
            # 布林带
            'bb_upper': to_list(upper_band, data_points),
            'bb_middle': to_list(middle_band, data_points),
            'bb_lower': to_list(lower_band, data_points),
            # 成交量
            'volumes': to_list(volumes, data_points),
            'volume_ma': to_list(volume_ma, data_points),
            # 当前值（最新一根K线的指标值）
            'current': {
                'price': float(close_prices[-1]),
                'ema20': float(ema20_values[-1]) if not np.isnan(ema20_values[-1]) else 0,
                'ema50': float(ema50_values[-1]) if not np.isnan(ema50_values[-1]) else 0,
                'macd': float(macd_values[-1]) if not np.isnan(macd_values[-1]) else 0,
                'rsi7': float(rsi7_values[-1]) if not np.isnan(rsi7_values[-1]) else 0,
                'rsi14': float(rsi14_values[-1]) if not np.isnan(rsi14_values[-1]) else 0,
                'atr14': float(atr14_values[-1]) if not np.isnan(atr14_values[-1]) else 0,
                'volume': float(volumes[-1]),
                'volume_ma': float(volume_ma[-1]) if not np.isnan(volume_ma[-1]) else 0
            }
        }


def format_market_data_for_display(data: Dict) -> str:
    """
    格式化市场数据用于显示（多时间框架版本）

    Args:
        data: 市场数据字典（来自 get_btc_complete_data()）

    Returns:
        格式化后的字符串
    """
    lines = []

    # 基础信息
    lines.append(f"**当前价格**: ${data['current_price']:.2f}")
    pc = data['price_changes']
    lines.append(f"**15分钟涨跌**: {pc['15m']:+.2f}%")
    lines.append(f"**1小时涨跌**: {pc['1h']:+.2f}%")
    lines.append(f"**4小时涨跌**: {pc['4h']:+.2f}%")
    lines.append(f"**24小时涨跌**: {pc['24h']:+.2f}%")
    lines.append("")

    # 技术指标（3分钟当前值）
    lines.append("**技术指标 (3分钟当前值)**:")
    lines.append(f"  • EMA20: ${data['current_ema20']:.2f}")
    lines.append(f"  • MACD: {data['current_macd']:.4f}")
    lines.append(f"  • RSI(7): {data['current_rsi7']:.2f}")
    lines.append("")

    # 多时间框架概览
    lines.append("**多时间框架数据**:")
    for tf_key, tf_name in [('3m', '3分钟'), ('15m', '15分钟'), ('1h', '1小时'), ('4h', '4小时')]:
        tf_data = data[f'timeframe_{tf_key}']
        current = tf_data['current']
        lines.append(f"  • {tf_name}: 价格 ${current['price']:.2f} | RSI(14) {current['rsi14']:.1f} | {tf_data['data_points']}个数据点")
    lines.append("")

    # 持仓量和资金费率
    oi = data['open_interest']
    lines.append(f"**持仓量**: {oi['latest']:,.0f} BTC")
    lines.append(f"**资金费率**: {data['funding_rate']:.6f} ({data['funding_rate']*100:.4f}%)")
    lines.append("")

    return "\n".join(lines)
