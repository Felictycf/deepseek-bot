import requests
import json
import os

# 替换为您的实际API密钥
API_KEY = "Csevz22MfE5PGn4BY2WQP9o76MtFBXik493P12ZG"

# API 端点
API_URL = "https://api.chart-img.com/v2/tradingview/advanced-chart"

# 请求头
headers = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

# 请求体 (以ETH为例，包含MACD, RSI, Volume)
payload = {
    "symbol": "BINANCE:EthUSDT",
    "interval": "1h",
    "theme": "dark",
    "width": 800,
    "height": 600,
    "studies": [
        {
            "name": "Volume",
            "forceOverlay": True
        },
        {
            "name": "MACD"
        },
        {
            "name": "Relative Strength Index"
        }
    ]
}

# 输出文件名
output_filename = "eth_chart_python.png"

print(f"正在请求 {API_URL}...")

try:
    # 发送POST请求
    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    # 检查响应状态码
    if response.status_code == 200:
        # 成功，将二进制内容写入文件
        with open(output_filename, "wb") as f:
            f.write(response.content)
        print(f"图表已成功生成并保存为 {output_filename}")
    else:
        # 失败，打印错误信息
        print(f"API请求失败，状态码: {response.status_code}")
        try:
            # 尝试解析JSON错误信息
            error_data = response.json()
            print(f"错误详情: {error_data}")
        except json.JSONDecodeError:
            # 如果不是JSON，则打印原始文本
            print(f"错误详情: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"发生网络错误: {e}")

# 打印用于生成BTC图表的payload (如果用户需要)
btc_payload = payload.copy()
btc_payload["symbol"] = "BINANCE:BTCUSDT"
print("\n---")
print("用于生成BTC图表的请求体示例:")
print(json.dumps(btc_payload, indent=2))
print("---")
