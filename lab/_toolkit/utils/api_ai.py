"""
File: api_ai.py
Project: routine
Created: 2025-03-21 05:14:06
Author: Victor Cheng
Email: hi@victor42.work
Description:
"""
import os
import json
import time
import logging
import requests
import functools
from pathlib import Path
from .path import PATH_DOWNLOADS
logger = logging.getLogger(__name__)

class APIError(RuntimeError):
    """API错误基类"""
    pass

class NetworkError(APIError):
    """网络错误 - 可重试"""
    pass

class RateLimitError(APIError):
    """配额限流错误 (429) - 可重试"""
    pass

class InvalidResponseError(APIError):
    """无法从API响应中提取有效内容 - 不可重试"""
    pass
keys_file_path = Path(__file__).parent / 'keys.json'
try:
    with open(keys_file_path, 'r') as f:
        keys = json.load(f)
        GEMINI_API_KEY = keys.get('GEMINI_API_KEY', '')
        DEEPSEEK_API_KEY = keys.get('DEEPSEEK_API_KEY', '')
        KIMI_API_KEY = keys.get('KIMI_API_KEY', '')
        OPENROUTER_API_KEY = keys.get('OPENROUTER_API_KEY', '')
        GROQ_API_KEY = keys.get('GROQ_API_KEY', '')
        CEREBRAS_API_KEY = keys.get('CEREBRAS_API_KEY', '')
        REPLICATE_API_TOKEN = keys.get('REPLICATE_API_TOKEN')
        if REPLICATE_API_TOKEN:
            os.environ['REPLICATE_API_TOKEN'] = REPLICATE_API_TOKEN
except Exception:
    GEMINI_API_KEY = ''
    DEEPSEEK_API_KEY = ''
    KIMI_API_KEY = ''
    OPENROUTER_API_KEY = ''
    GROQ_API_KEY = ''
    CEREBRAS_API_KEY = ''
    REPLICATE_API_TOKEN = None

def retry_with_backoff(max_retries=3, base_delay=3, rate_limit_delay=60, retry_on_network=True, retry_on_rate_limit=True):
    """
    API 重试装饰器 - 指数退避策略

    错误分类：
    - NetworkError：延迟 = base_delay * (2 ** attempt)  → 3s, 6s, 12s
    - RateLimitError：延迟 = rate_limit_delay * (2 ** attempt)  → 60s, 120s, 240s
    - 其他错误（安全阻止等）：不重试，直接抛出
    """

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (NetworkError, RateLimitError) as e:
                    is_network = isinstance(e, NetworkError)
                    is_rate_limit = isinstance(e, RateLimitError)
                    should_retry = False
                    delay = 0
                    retry_type = ''
                    if is_network and retry_on_network:
                        should_retry = True
                        delay = base_delay * 2 ** attempt
                        retry_type = '网络错误'
                    elif is_rate_limit and retry_on_rate_limit:
                        should_retry = True
                        delay = rate_limit_delay * 2 ** attempt
                        retry_type = '配额限流'
                    if not should_retry:
                        raise
                    if attempt < max_retries - 1:
                        logger.warning(f'{retry_type}，{delay}秒后重试 ({attempt + 1}/{max_retries})...')
                        time.sleep(delay)
                    else:
                        logger.error(f'{retry_type}重试{max_retries}次后仍失败')
                        raise
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=3, rate_limit_delay=60)
def ask_groq(prompt, model='qwen/qwen3-32b', delay=0):
    """调用 Groq API 获取 AI 回复

    参数:
        prompt (str): 要发送的提示内容
        model (str): 使用的模型名称，默认为 'qwen/qwen3-32b'
        delay (int): 请求间隔秒数，默认为 0

    返回:
        str: AI 的回复内容

    异常:
        ValueError: 当 API 密钥缺失或提示内容无效时
        NetworkError: 当网络请求失败时（会自动重试）
        RateLimitError: 当API返回429状态码时（会自动重试）
        InvalidResponseError: 当无法从API响应中提取有效内容时（不重试）
    """
    if not prompt or not isinstance(prompt, str) or (not prompt.strip()):
        raise ValueError('prompt must be a non-empty string')
    if not GROQ_API_KEY:
        raise RuntimeError('GROQ_API_KEY is not configured in keys.json')
    if delay > 0:
        time.sleep(delay)
    url = 'https://api.groq.com/openai/v1/chat/completions'
    request_data = {'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 8192, 'temperature': 0.7}
    headers = {'Authorization': f'Bearer {GROQ_API_KEY}', 'Content-Type': 'application/json'}
    try:
        response = requests.post(url, json=request_data, headers=headers, timeout=60)
    except requests.RequestException as e:
        raise RuntimeError(f'网络请求失败: {e}') from e
    if response.status_code != 200:
        raise RuntimeError(f'API 请求失败，状态码: {response.status_code}, 响应: {response.text}')
    response_data = response.json()
    reply = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
    if reply:
        return reply
    else:
        raise InvalidResponseError('无法从 API 响应中提取回复内容')

@retry_with_backoff(max_retries=3, base_delay=3, rate_limit_delay=60)
def ask_cerebras(prompt, model='qwen-3-32b', delay=0):
    """调用 Cerebras API 获取 AI 回复

    参数:
        prompt (str): 要发送的提示内容
        model (str): 使用的模型名称，默认为 'qwen-3-32b'
        delay (int): 请求间隔秒数，默认为 0

    返回:
        str: AI 的回复内容

    异常:
        ValueError: 当 API 密钥缺失或提示内容无效时
        NetworkError: 当网络请求失败时（会自动重试）
        RateLimitError: 当API返回429状态码时（会自动重试）
        InvalidResponseError: 当无法从API响应中提取有效内容时（不重试）
    """
    if not prompt or not isinstance(prompt, str) or (not prompt.strip()):
        raise ValueError('prompt must be a non-empty string')
    if not CEREBRAS_API_KEY:
        raise RuntimeError('CEREBRAS_API_KEY is not configured in keys.json')
    if delay > 0:
        time.sleep(delay)
    url = 'https://api.cerebras.ai/v1/chat/completions'
    request_data = {'model': model, 'messages': [{'role': 'user', 'content': prompt}], 'max_tokens': 8192, 'temperature': 0.7, 'top_p': 0.95, 'stream': False}
    headers = {'Authorization': f'Bearer {CEREBRAS_API_KEY}', 'Content-Type': 'application/json', 'User-Agent': 'Python/CerebrasSDK'}
    try:
        response = requests.post(url, json=request_data, headers=headers, timeout=60)
    except requests.RequestException as e:
        raise RuntimeError(f'网络请求失败: {e}') from e
    if response.status_code != 200:
        raise RuntimeError(f'API 请求失败，状态码: {response.status_code}, 响应: {response.text}')
    response_data = response.json()
    reply = response_data.get('choices', [{}])[0].get('message', {}).get('content', '')
    if reply:
        return reply
    else:
        raise InvalidResponseError('无法从 API 响应中提取回复内容')