"""
File: path.py
Project: agent-workspace
Created: 2024-11-02
Author: Agent Vik
Email: agent-vik@victor42.work
Description: 云端脱敏版路径配置系统 (Cloud-Safe Abstraction)
Environment: env: cloud
"""

import os
import platform

def get_platform():
    """云端环境默认为 linux 兼容模式"""
    return 'linux'

def _is_cloud_runtime() -> bool:
    """仅在真正的云端沙盒里才允许自愈建目录。

    本地误 import 本模块时不得创建 ~/Drive。
    判定顺序：显式环境变量 > Darwin/Windows/WSL 排除，其余 Linux 视为 cloud。
    """
    explicit = (os.environ.get('AGENT_WORKSPACE_ENV')
                or os.environ.get('AGENT_ENV')
                or '').strip().lower()
    if explicit in ('cloud', 'local'):
        return explicit == 'cloud'

    system = platform.system()
    if system in ('Darwin', 'Windows'):
        return False

    if system == 'Linux':
        try:
            with open('/proc/version', 'r') as f:
                version_info = f.read().lower()
            if 'microsoft' in version_info or 'wsl' in version_info:
                return False
        except FileNotFoundError:
            pass
        return True

    return False

# 获取当前平台 (Cloud 模式下始终为 linux)
platform_type = get_platform()

# 虚拟用户名，防止泄露本地真实用户名
windows_username = 'agent-vik'

# 系统路径
HOME = os.path.expanduser('~')
# 云端沙盒通常只有 /tmp 可写，优先使用 /tmp 作为下载缓冲
PATH_DOWNLOADS = "/tmp"
PATH_DOWNLOADS_FROM_WIN = "/tmp"

# 根据平台配置基础路径 (云端采用 HOME/Drive 结构模拟本地挂载)
DRIVE_ROOT = os.path.join(HOME, 'Drive')
BASE_PATH = DRIVE_ROOT
BASE_PATH_ONEDRIVE = DRIVE_ROOT
BASE_PATH_SYNC = DRIVE_ROOT

# 常用路径 (保持变量名与 routine 一致，确保工具链兼容)
BASE_PATH_WORKSPACE = os.path.join(BASE_PATH, 'workspace')
BASE_PATH_SCREENSHOTS = os.path.join(BASE_PATH, 'screenshots')
BASE_PATH_NOTEBOOK = os.path.join(BASE_PATH, 'notebook')
BASE_PATH_APP_DATA = os.path.join(BASE_PATH, 'app_data')

# 开发路径定义 (指向云端代码存放处)
BASE_PATH_CODING = os.path.join(HOME, 'coding')

# 日常工具集根目录：本模块所在的 _toolkit（与 routine/utils/path.py 共用变量名）
BASE_PATH_TOOLKIT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# 环境自愈：仅 cloud 才 makedirs，避免本机误用污染 ~/Drive
if _is_cloud_runtime():
    for p in [BASE_PATH, BASE_PATH_WORKSPACE, BASE_PATH_SCREENSHOTS, BASE_PATH_NOTEBOOK, PATH_DOWNLOADS]:
        try:
            os.makedirs(p, exist_ok=True)
        except Exception:
            pass
