"""
DeepSeek API 客户端
改编自 NOFX 的 mcp/client.go
支持调用 DeepSeek API 进行市场分析
"""

import requests
import json
import time
from typing import Dict, Tuple, Optional


class DeepSeekClient:
    """DeepSeek API 客户端"""

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1",
                 model: str = "deepseek-chat", timeout: int = 120):
        """
        初始化 DeepSeek 客户端

        Args:
            api_key: DeepSeek API 密钥
            base_url: API 基础 URL
            model: 模型名称
            timeout: 超时时间（秒）
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout

    def call_with_messages(self, system_prompt: str, user_prompt: str,
                          max_retries: int = 3) -> str:
        """
        使用 system + user prompt 调用 AI API（带重试）
        对应 NOFX 的 CallWithMessages() 函数

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            max_retries: 最大重试次数

        Returns:
            AI 响应文本

        Raises:
            Exception: API 调用失败
        """
        last_error = None

        for attempt in range(1, max_retries + 1):
            if attempt > 1:
                print(f"⚠️  AI API调用失败，正在重试 ({attempt}/{max_retries})...")

            try:
                result = self._call_once(system_prompt, user_prompt)
                if attempt > 1:
                    print("✓ AI API重试成功")
                return result
            except Exception as e:
                last_error = e
                # 检查是否可重试
                if not self._is_retryable_error(e):
                    raise

                # 重试前等待
                if attempt < max_retries:
                    wait_time = attempt * 2
                    print(f"⏳ 等待{wait_time}秒后重试...")
                    time.sleep(wait_time)

        raise Exception(f"重试{max_retries}次后仍然失败: {last_error}")

    def _call_once(self, system_prompt: str, user_prompt: str) -> str:
        """
        单次调用 AI API（内部使用）

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词

        Returns:
            AI 响应文本
        """
        # 构建 messages 数组
        messages = []

        # 添加 system message
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })

        # 添加 user message
        messages.append({
            "role": "user",
            "content": user_prompt
        })

        # 构建请求体
        request_body = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.5,  # 降低temperature以提高JSON格式稳定性
            "max_tokens": 2000
        }

        # 创建HTTP请求
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        # 发送请求
        response = requests.post(
            url,
            headers=headers,
            json=request_body,
            timeout=self.timeout
        )

        # 检查响应状态
        if response.status_code != 200:
            raise Exception(f"API返回错误 (status {response.status_code}): {response.text}")

        # 解析响应
        result = response.json()

        if 'choices' not in result or len(result['choices']) == 0:
            raise Exception("API返回空响应")

        return result['choices'][0]['message']['content']

    def _is_retryable_error(self, error: Exception) -> bool:
        """
        判断错误是否可重试

        Args:
            error: 异常对象

        Returns:
            是否可重试
        """
        error_str = str(error).lower()
        retryable_errors = [
            'timeout',
            'connection',
            'temporary',
            'network',
            'eof'
        ]
        return any(retryable in error_str for retryable in retryable_errors)


def parse_ai_response(ai_response: str) -> Tuple[str, Optional[Dict]]:
    """
    解析 AI 响应，提取思维链和 JSON 结果
    改编自 NOFX 的 parseFullDecisionResponse() 函数

    Args:
        ai_response: AI 原始响应

    Returns:
        (cot_trace, json_result) 元组
        - cot_trace: 思维链分析文本
        - json_result: 解析后的 JSON 字典，如果解析失败则为 None
    """
    # 提取思维链（JSON 之前的内容）
    cot_trace = _extract_cot_trace(ai_response)

    # 提取 JSON
    try:
        json_result = _extract_json(ai_response)
        return cot_trace, json_result
    except Exception as e:
        print(f"⚠️ JSON解析失败: {e}")
        return cot_trace, None


def _extract_cot_trace(response: str) -> str:
    """
    提取思维链分析
    对应 NOFX 的 extractCoTTrace() 函数

    Args:
        response: AI 响应文本

    Returns:
        思维链文本
    """
    # 查找 JSON 对象的开始位置
    json_start = response.find('{')

    if json_start > 0:
        # 思维链是 JSON 之前的内容
        return response[:json_start].strip()

    # 如果找不到 JSON，整个响应都是思维链
    return response.strip()


def _extract_json(response: str) -> Dict:
    """
    提取 JSON 结果
    对应 NOFX 的 extractDecisions() 函数

    Args:
        response: AI 响应文本

    Returns:
        解析后的 JSON 字典

    Raises:
        Exception: JSON 解析失败
    """
    # 查找 JSON 对象
    json_start = response.find('{')
    if json_start == -1:
        raise Exception("无法找到JSON对象起始")

    # 从 { 开始，匹配括号找到对应的 }
    json_end = _find_matching_brace(response, json_start)
    if json_end == -1:
        raise Exception("无法找到JSON对象结束")

    json_content = response[json_start:json_end + 1].strip()

    # 修复常见的 JSON 格式错误（替换中文引号）
    json_content = _fix_json_quotes(json_content)

    # 解析 JSON
    try:
        result = json.loads(json_content)
        return result
    except json.JSONDecodeError as e:
        raise Exception(f"JSON解析失败: {e}\nJSON内容: {json_content}")


def _find_matching_brace(s: str, start: int) -> int:
    """
    查找匹配的右花括号
    对应 NOFX 的 findMatchingBracket() 函数

    Args:
        s: 字符串
        start: 左花括号的位置

    Returns:
        右花括号的位置，如果找不到返回 -1
    """
    if start >= len(s) or s[start] != '{':
        return -1

    depth = 0
    for i in range(start, len(s)):
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i

    return -1


def _fix_json_quotes(json_str: str) -> str:
    """
    修复 JSON 中的中文引号
    对应 NOFX 的 fixMissingQuotes() 函数

    Args:
        json_str: JSON 字符串

    Returns:
        修复后的 JSON 字符串
    """
    # 替换中文引号为英文引号
    replacements = {
        '\u201c': '"',  # "
        '\u201d': '"',  # "
        '\u2018': "'",  # '
        '\u2019': "'"   # '
    }

    for old, new in replacements.items():
        json_str = json_str.replace(old, new)

    return json_str
