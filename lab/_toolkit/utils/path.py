"""
File: path.py
Project: open-agent-memory
Created: 2024-11-02
Author: Agent Vik
Email: your_email@example.com
Description: 通用路径配置系统 - 用户可根据需要自定义
"""

import os
import platform


def get_platform():
    """检测当前运行平台"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "mac"
    else:
        return "linux"


platform_type = get_platform()

HOME = os.path.expanduser("~")
PATH_DOWNLOADS = os.path.join(HOME, "Downloads")
PATH_DOWNLOADS_FROM_WIN = PATH_DOWNLOADS
