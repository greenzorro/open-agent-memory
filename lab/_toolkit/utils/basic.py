"""
File: basic.py
Project: routine
Created: 2024-11-05 12:57:35
Author: Victor Cheng
Email: hi@victor42.work
Description: 
"""

import os
import shutil
import subprocess
import re
from typing import Optional
from PIL import Image
import pillow_avif
from bs4 import BeautifulSoup
import zipfile
import rarfile
from .path import platform_type


def get_source_files(source_path, allowed_extensions=None, recursive=False):
    """Return source files from a file path or directory path.

    :param str source_path: Source file or directory path
    :param iterable allowed_extensions: Extensions with or without leading dots
    :param bool recursive: Whether to scan directories recursively
    :return list[str]: Sorted source file paths
    """
    if not os.path.exists(source_path):
        raise FileNotFoundError(f"源路径不存在: {source_path}")

    allowed = None
    if allowed_extensions is not None:
        allowed = {
            ext.lower().lstrip(".")
            for ext in allowed_extensions
        }

    def is_allowed(path):
        name = os.path.basename(path)
        if name.startswith(".") or not os.path.isfile(path):
            return False
        if allowed is None:
            return True
        return os.path.splitext(name)[1][1:].lower() in allowed

    if os.path.isfile(source_path):
        return [source_path] if is_allowed(source_path) else []

    files = []
    if recursive:
        for root, dirs, filenames in os.walk(source_path):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in filenames:
                path = os.path.join(root, filename)
                if is_allowed(path):
                    files.append(path)
    else:
        for filename in os.listdir(source_path):
            path = os.path.join(source_path, filename)
            if is_allowed(path):
                files.append(path)

    return sorted(files)


def sanitize_file_name_string(input_string):
    """从字符串中去除不能作为文件名的字符

    :param str input_string: 输入的字符串
    :return str: 清理后的字符串
    """
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '.', ',']
    for char in invalid_chars:
        input_string = input_string.replace(char, ' ')
    # 把多个连续的空格替换单个空格
    result = ' '.join(input_string.split())
    return result


# 狭义中文字符范围
NARROW_CHINESE = [
    ('\u4e00', '\u9fff'),  # 基本汉字
    ('\u3000', '\u303f'),  # 中文标点符号
    ('\u2014', '\u2014'),  # 破折号
    ('\u2018', '\u2019'),  # 中文引号
    ('\u201c', '\u201d'),  # 中文双引号
    ('\u2026', '\u2026'),  # 省略号
    ('\uff01', '\uff01'),  # 感叹号
    ('\uff08', '\uff09'),  # 括号
    ('\uff0c', '\uff0c'),  # 逗号
    ('\uff1a', '\uff1a'),  # 冒号
    ('\uff1b', '\uff1b'),  # 分号
    ('\uff5e', '\uff5e'),  # 全角波浪号
    ('\uffe5', '\uffe5'),  # 人民币符号
    ('\uff1f', '\uff1f'),  # 问号
    ('\ufe43', '\ufe44'),  # 中文竖方引号
    ('\ufe4f', '\ufe4f'),  # 叠字符号
    ('\uff00', '\uffef'),  # 全角字符
]

# 广义中文字符范围
BROAD_CHINESE = NARROW_CHINESE + [
    ('\u0030', '\u0039'),  # 阿拉伯数字
    ('\u0020', '\u0020'),  # 半角空格
    ('\u002d', '\u002d'),  # 减号
    ('\u002b', '\u002b'),  # 加号
    ('\u003c', '\u003e'),  # 小于大于号
    ('\u003d', '\u003d'),  # 等号
    ('\u002a', '\u002a'),  # 星号
    ('\u002f', '\u002f'),  # 斜杠
    ('\u00d7', '\u00d7'),  # 乘号
    ('\u00f7', '\u00f7'),  # 除号
    ('\u0025', '\u0025'),  # 百分号
]


def contain_chinese(input_str, mode='any', range_chinese='narrow'):
    """判断字符串中是否包含中文字符（包括中文标点符号）

    :param str input_str: 输入的字符串
    :param str mode: 匹配模式，'any' 表示任意匹配，'all' 表示全部匹配
    :param str range_chinese: 字符范围，'narrow' 表示狭义中文字符，'broad' 表示广义中文字符
    :return bool: 根据模式和字符范围判断是否包含中文字符或中文标点符号，返回True或False
    :raises ValueError: 如果mode或range_chinese参数不合法，则抛出异常
    """
    # 去除不可见字符
    input_str = ''.join(c for c in input_str if c.isprintable())
    
    if range_chinese == 'narrow':
        range_chinese = NARROW_CHINESE
    elif range_chinese == 'broad':
        range_chinese = BROAD_CHINESE
    else:
        raise ValueError("range_chinese参数只能为'narrow'或'broad'")

    if mode == 'any':
        for char in input_str:
            for char_start, char_end in range_chinese:
                if char_start <= char <= char_end:
                    return True
        return False
    elif mode == 'all':
        for char in input_str:
            if not any(char_start <= char <= char_end for char_start, char_end in range_chinese):
                return False
        return True
    else:
        raise ValueError("mode参数只能为'any'或'all'")


def contain_non_chinese(input_str, mode='any', range_chinese='narrow'):
    """判断字符串中是否包含中文字符（包括中文标点符号）以外的字符

    :param str input_str: 输入的字符串
    :param str mode: 匹配模式，'any' 表示任意匹配，'all' 表示全部匹配
    :param str range_chinese: 字符范围，'narrow' 表示狭义中文字符，'broad' 表示广义中文字符
    :return bool: 根据模式和字符范围判断是否包含中文字符以外的字符，返回True或False
    :raises ValueError: 如果mode或range_chinese参数不合法，则抛出异常
    """
    # 去除不可见字符
    input_str = ''.join(c for c in input_str if c.isprintable())
    
    if range_chinese == 'narrow':
        range_chinese = NARROW_CHINESE
    elif range_chinese == 'broad':
        range_chinese = BROAD_CHINESE
    else:
        raise ValueError("range_chinese参数只能为'narrow'或'broad'")

    if mode == 'any':
        for char in input_str:
            if all(char < char_start or char > char_end for char_start, char_end in range_chinese):
                return True
        return False
    elif mode == 'all':
        for char in input_str:
            if not all(char < char_start or char > char_end for char_start, char_end in range_chinese):
                return False
        return True
    else:
        raise ValueError("mode参数只能为'any'或'all'")


def html_table_2_csv_content(html_content):
    """将HTML字符串中的<table>转换为CSV内容

    :param str html_content: 源HTML字符串
    :return list: CSV文件的行列表
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 找到第一个table
    table = soup.find('table')
    csv_content = []

    if table:
        rows = table.find_all('tr')
        for row in rows:
            columns = row.find_all(['th', 'td'])
            csv_content.append([column.get_text(strip=True) for column in columns])
    else:
        print('No <table> found in HTML content')

    return csv_content


def plan_flattened_destinations(source_paths, dst_path, dst_extension=None):
    """为扁平化输出生成无重名覆盖的确定性目标路径。"""
    used_names = set()
    plan = []

    for source_path in source_paths:
        filename = os.path.basename(source_path)
        if dst_extension is not None:
            stem = os.path.splitext(filename)[0]
            filename = f"{stem}.{dst_extension.lower().lstrip('.')}"

        stem, extension = os.path.splitext(filename)
        candidate = filename
        suffix = 2
        while candidate.casefold() in used_names:
            candidate = f"{stem}_{suffix}{extension}"
            suffix += 1

        used_names.add(candidate.casefold())
        plan.append((source_path, os.path.join(dst_path, candidate)))

    return plan


def plan_folder_ungroup(src_path, dst_path):
    """列出文件夹解组将执行的复制计划。"""
    source_files = []
    for root, dirs, files in os.walk(src_path):
        dirs.sort()
        for filename in sorted(files):
            source_files.append(os.path.join(root, filename))
    return plan_flattened_destinations(source_files, dst_path)


def folder_ungroup(src_path, dst_path):
    """把文件里的文件夹拆开，取出全部文件

    :param str src_path: 源文件夹路径
    :param str dst_path: 目标文件夹路径
    """
    if not os.path.exists(dst_path):
        os.makedirs(dst_path)

    for src_file_path, dst_file_path in plan_folder_ungroup(src_path, dst_path):
        shutil.copy(src_file_path, dst_file_path)


def open_installer(file_path):
    """打开安装文件

    :param str file_path: 安装文件的路径
    :raises RuntimeError: 在WSL环境下不支持

    注意：此函数在WSL环境下不支持，因为需要图形界面来运行安装程序。
    WSL环境下会抛出RuntimeError异常。"""
    # 参数验证
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"安装文件未找到: {file_path}")
    
    # 获取文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()

    # 检查是否在WSL环境
    if platform_type == 'wsl':
        raise RuntimeError(f"WSL环境下不支持打开安装文件，请切换到Windows环境运行: {file_path}")

    # 如果是Windows系统
    if os.name == 'nt':
        if file_ext in ['.exe', '.msi']:
            try:
                os.startfile(file_path)
            except Exception as e:
                raise RuntimeError(f"无法打开安装文件 {file_path}: {e}")
        else:
            raise ValueError(f'Windows系统不支持的安装文件格式: {file_ext}')

    # 如果是Mac系统
    elif os.name == 'posix':
        if file_ext in ['.dmg', '.pkg']:
            try:
                subprocess.run(['open', file_path], check=True)
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"无法打开安装文件 {file_path}: {e}")
            except FileNotFoundError:
                raise RuntimeError("系统未找到 'open' 命令，请确保在macOS系统上运行")
        else:
            raise ValueError(f'macOS系统不支持的安装文件格式: {file_ext}')

    else:
        raise RuntimeError(f'不支持的操作系统: {os.name}')


def unarchive_file(file_path):
    """原地解压缩文件

    :param str file_path: 要解压的文件路径
    """

    # 获取文件名和扩展名
    file_name, file_ext = os.path.splitext(file_path)
    file_ext = file_ext.lower()
    if file_ext not in {'.zip', '.rar'}:
        raise ValueError(f'不支持的压缩文件格式: {file_ext}')

    # Windows、Linux 与 WSL 使用 Python 解压库，避免依赖桌面命令。
    if os.name == 'nt' or platform_type in {'linux', 'wsl'}:
        if file_ext == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(file_name)
        else:
            with rarfile.RarFile(file_path, 'r') as rar_ref:
                rar_ref.extractall(file_name)

    # macOS 的 ditto 对中文文件名编码兼容更好；RAR 交给 The Unarchiver。
    elif platform_type == 'mac':
        if file_ext == '.zip':
            cmd = ['ditto', '-x', '-k', file_path, file_name]
        else:
            cmd = ['open', '-a', 'The Unarchiver', file_path]
        subprocess.run(cmd, check=True)

    else:
        raise RuntimeError(f'不支持的操作系统: {platform_type}')


def rename_by_name_list(name_list, src_folder, dst_folder):
    """按名称列表批量重命名文件

    :param list name_list: 新文件名列表（不含扩展名）
    :param str src_folder: 原始文件夹路径
    :param str dst_folder: 目标文件夹路径
    """
    # 清理name_list中的非法字符
    name_list = [sanitize_file_name_string(name) for name in name_list]

    # 遍历原始文件存入list
    src_files = []
    for filename in os.listdir(src_folder):
        # 忽略隐藏文件和文件夹
        if filename.startswith('.'):
            continue
        src_path = os.path.join(src_folder, filename)
        if not os.path.isfile(src_path):
            continue
        src_files.append(src_path)

    # 判断文件数量与名称数量是否匹配
    if len(src_files) != len(name_list):
        print(f'There are {len(src_files)} files and {len(name_list)} names. They do not match.')
        return

    # 按文件名数字顺序排列
    src_files.sort(key=lambda x: int(re.findall(r'\d+', os.path.splitext(os.path.basename(x))[0])[-1]))

    # 批量重命名
    for i, src_path in enumerate(src_files):
        # 获取文件名和扩展名
        filename, ext = os.path.splitext(os.path.basename(src_path))
        # 获取新文件名
        new_filename = name_list[i] + ext
        # 拼接新文件路径
        dst_path = os.path.join(dst_folder, new_filename)
        # 复制文件
        shutil.copy(src_path, dst_path)

        # 打印输出结果
        if os.path.exists(dst_path):
            print(f'{src_path} renamed to {dst_path}')
        else:
            print(f'Failed to rename {src_path}')


VIDEO_FORMATS = {'mp4', 'avi', 'wmv', 'mov', 'flv', 'm4a', 'mkv', 'webm', 'm4v'}
AUDIO_FORMATS = {'mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a', 'opus'}
IMAGE_FORMATS = {'jpg', 'jpeg', 'jfif', 'png', 'bmp', 'gif', 'tiff', 'webp', 'avif'}
JPEG_FORMATS = {'jpg', 'jpeg', 'jfif'}

VIDEO_CODEC_OPTIONS = {
    'mp4': ['-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-c:a', 'aac', '-b:a', '192k'],
    'mov': ['-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-c:a', 'aac', '-b:a', '192k'],
    'm4v': ['-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-c:a', 'aac', '-b:a', '192k'],
    'mkv': ['-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-c:a', 'aac', '-b:a', '192k'],
    'avi': ['-c:v', 'mpeg4', '-q:v', '5', '-c:a', 'libmp3lame', '-q:a', '2'],
    'webm': ['-c:v', 'libvpx-vp9', '-crf', '32', '-b:v', '0', '-c:a', 'libopus', '-b:a', '128k'],
    'flv': ['-c:v', 'libx264', '-preset', 'slow', '-crf', '24', '-c:a', 'aac', '-b:a', '160k'],
    'wmv': ['-c:v', 'wmv2', '-c:a', 'wmav2'],
}

AUDIO_CODEC_OPTIONS = {
    'mp3': ['-vn', '-c:a', 'libmp3lame', '-q:a', '2'],
    'wav': ['-vn', '-c:a', 'pcm_s16le'],
    'flac': ['-vn', '-c:a', 'flac'],
    'aac': ['-vn', '-c:a', 'aac', '-b:a', '192k'],
    'm4a': ['-vn', '-c:a', 'aac', '-b:a', '192k'],
    'ogg': ['-vn', '-c:a', 'libvorbis', '-q:a', '5'],
    'opus': ['-vn', '-c:a', 'libopus', '-b:a', '128k'],
}


def convert_format(src_path, dst_path, dst_format):
    """文件格式转换

    :param str src_path: 源文件路径
    :param str dst_path: 目标文件路径
    :param str dst_format: 目标格式
    """
    # 参数验证
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"源文件未找到: {src_path}")
    
    if not dst_format or not isinstance(dst_format, str):
        raise ValueError(f"目标格式必须是非空字符串，当前值: {dst_format}")
    
    # 确保目标目录存在
    dst_dir = os.path.dirname(dst_path)
    if dst_dir and not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    
    src_format = os.path.splitext(src_path)[1][1:].lower()
    dst_format = dst_format.lower().lstrip('.')
    
    try:
        # 相同格式，或 JPEG/JFIF 的等价扩展名之间转换时，直接复制文件，
        # 避免仅为修改扩展名而重新编码、损失图像质量或元数据。
        if src_format == dst_format or (
            src_format in JPEG_FORMATS and dst_format in JPEG_FORMATS
        ):
            shutil.copy(src_path, dst_path)
            print(f'{src_path} copied to {dst_path}')
            return
        
        # 处理视频文件的转换
        if src_format in VIDEO_FORMATS:
            if dst_format == 'gif':
                # 视频→GIF动图：使用ffmpeg提取帧序列生成GIF
                result = subprocess.run(['ffmpeg', '-i', src_path,
                                       '-vf', 'fps=15,scale=480:-1:flags=lanczos',
                                       '-c:v', 'gif', dst_path],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"视频转GIF失败: {result.stderr}")
            elif dst_format in AUDIO_FORMATS:
                result = subprocess.run(['ffmpeg', '-i', src_path, *AUDIO_CODEC_OPTIONS[dst_format], dst_path],
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    raise RuntimeError(f"视频转音频失败: {result.stderr}")
            elif dst_format in VIDEO_CODEC_OPTIONS:
                result = subprocess.run(['ffmpeg', '-i', src_path, *VIDEO_CODEC_OPTIONS[dst_format], dst_path],
                                      capture_output=True, text=True)
            else:
                raise ValueError(f"不支持的视频目标格式: {dst_format}")
            if result.returncode != 0:
                raise RuntimeError(f"视频格式转换失败: {result.stderr}")
        
        # 处理音频文件的转换
        elif src_format in AUDIO_FORMATS:
            if dst_format not in AUDIO_CODEC_OPTIONS:
                raise ValueError(f"不支持的音频目标格式: {dst_format}")
            result = subprocess.run(['ffmpeg', '-i', src_path, *AUDIO_CODEC_OPTIONS[dst_format], dst_path],
                                  capture_output=True, text=True)
            if result.returncode != 0:
                raise RuntimeError(f"音频格式转换失败: {result.stderr}")
        
        # 处理图片文件的转换
        elif src_format in IMAGE_FORMATS:
            # 检查目标格式是否支持
            if dst_format not in IMAGE_FORMATS:
                raise ValueError(f"不支持的图片目标格式: {dst_format}")
            
            try:
                with Image.open(src_path) as img:
                    # 只有 JPEG/JFIF 不支持 alpha 或调色板模式；其他目标格式
                    # 保留原始模式，避免 PNG/WebP/AVIF 等格式丢失透明通道。
                    if dst_format in JPEG_FORMATS and img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    img.save(dst_path)
            except Exception as img_e:
                raise RuntimeError(f"图片格式转换失败: {img_e}")
        
        else:
            raise ValueError(f"不支持的源文件格式: {src_format}")
        
        # 验证转换结果
        if not os.path.exists(dst_path):
            raise RuntimeError(f"转换失败，目标文件未生成: {dst_path}")
        
        # 打印转换结果
        print(f'{src_path} converted to {dst_path}')
        
    except FileNotFoundError:
        raise
    except ValueError:
        raise
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f'转换过程中发生未预期的错误: {e}')


def get_latest_file_by_extension(directory: str, extension: str) -> Optional[str]:
    """
    获取目录中指定扩展名的最新文件

    Args:
        directory: 目录路径
        extension: 文件扩展名（如'.xls'）

    Returns:
        Optional[str]: 最新文件路径，如未找到则返回None
    """
    if not os.path.exists(directory):
        return None

    files = []
    for filename in os.listdir(directory):
        if filename.lower().endswith(extension.lower()):
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                files.append((filepath, os.path.getmtime(filepath)))

    if not files:
        return None

    # 按修改时间排序，返回最新的文件
    files.sort(key=lambda x: x[1], reverse=True)
    return files[0][0]


def get_any_latest_file(directory: str) -> Optional[str]:
    """
    获取目录中最新修改的任何文件

    Args:
        directory: 目录路径

    Returns:
        Optional[str]: 最新文件路径，如未找到则返回None
    """
    if not os.path.exists(directory):
        return None

    files = []
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            files.append((filepath, os.path.getmtime(filepath)))

    if not files:
        return None

    # 按修改时间排序，返回最新的文件
    files.sort(key=lambda x: x[1], reverse=True)
    return files[0][0]


def extract_number_from_filename(filename: str) -> int:
    """从文件名中提取数字部分，用于排序

    Args:
        filename: 文件名

    Returns:
        int: 提取的数字，如果没有数字返回999999
    """
    # 移除文件扩展名
    name_without_ext = os.path.splitext(filename)[0]
    
    # 查找文件名中的数字部分
    numbers = re.findall(r'\d+', name_without_ext)
    
    if numbers:
        # 取第一个数字（最前面一段纯数字的部分）
        return int(numbers[0])
    else:
        # 如果没有数字，返回一个很大的数确保排在最后
        return 999999


def get_param_value(args, arg_name, script_default=None, prompt_text=None):
    """获取参数值，按优先级：
    1. 命令行参数
    2. 脚本提供的默认值
    3. 用户输入（可选）

    Args:
        args: argparse 解析后的参数对象
        arg_name: 参数名称
        script_default: 脚本预先计算好的默认值
        prompt_text: 提供此参数才询问用户

    Returns:
        参数值

    设计理念：
    - 基建只做一件事：参数优先级判断
    - 脚本负责计算默认值（可以是复杂、异步、依赖状态的逻辑）
    - prompt_text 是可选的：不提供 = 不问用户，直接用默认值
    """
    # 优先级1：命令行参数
    value = getattr(args, arg_name, None)
    if value is not None:
        return value

    # 优先级2：脚本默认值
    if script_default is not None:
        return script_default

    # 优先级3：用户输入（可选）
    if prompt_text is not None:
        return input(prompt_text + ": ")

    return None
