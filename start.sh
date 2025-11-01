#!/bin/bash

# BTC 盯盘机器人启动脚本

echo "🚀 BTC 盯盘机器人启动脚本"
echo "======================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3"
    echo "请先安装 Python 3.8+"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "⚠️  警告: 未找到 config.json"
    echo "正在从模板创建..."
    cp config.json.example config.json
    echo "✓ 已创建 config.json"
    echo ""
    echo "请编辑 config.json 填入你的 API 密钥，然后重新运行此脚本"
    exit 1
fi

# 检查依赖
echo "📦 检查 Python 依赖..."
if ! python3 -c "import ccxt, pandas, talib" &> /dev/null; then
    echo "⚠️  缺少依赖，正在安装..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo ""
        echo "❌ 依赖安装失败"
        echo ""
        echo "请先手动安装 TA-Lib:"
        echo "  macOS: brew install ta-lib"
        echo "  Ubuntu: sudo apt-get install libta-lib0-dev"
        echo ""
        echo "然后运行: pip3 install -r requirements.txt"
        exit 1
    fi
fi
echo "✓ 依赖检查完成"
echo ""

# 启动程序
echo "🤖 启动 BTC 盯盘机器人..."
echo ""
python3 btc_monitor.py
