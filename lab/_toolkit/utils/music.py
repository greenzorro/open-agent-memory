"""
File: music.py
Project: routine
Created: 2024-11-05 12:41:38
Author: Victor Cheng
Email: hi@victor42.work
Description: 
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from .basic import sanitize_file_name_string

def _is_safe_path(path, base_path):
    """检查路径是否安全，防止路径遍历攻击
    
    :param str path: 要检查的路径
    :param str base_path: 基础路径
    :return bool: 路径是否安全
    """
    # 获取绝对路径并规范化
    abs_path = os.path.abspath(path)
    abs_base = os.path.abspath(base_path)
    
    # 检查路径是否在基础路径下
    return abs_path.startswith(abs_base + os.sep) or abs_path == abs_base

def _sanitize_filename(filename):
    """进一步清理文件名，防止路径遍历
    
    :param str filename: 原始文件名
    :return str: 安全的文件名
    """
    # 移除路径分隔符
    filename = filename.replace('/', '_').replace('\\', '_')
    # 移除潜在的路径遍历字符
    filename = filename.replace('..', '_')
    # 移除Windows保留字
    windows_reserved = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                       'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                       'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    name_part = os.path.splitext(filename)[0].upper()
    if name_part in windows_reserved:
        filename = f'_{filename}'
    
    return filename

def sanitize_file_names(result_dict):
    """清理歌曲文件名中的非法字符

    :param dict result_dict: 包含歌曲信息的字典
    :return dict: 清理后的歌曲信息字典
    """
    for key, value in result_dict.items():
        value[0] = sanitize_file_name_string(value[0])
        value[1] = sanitize_file_name_string(value[1])
    return result_dict

def html_content_2_QQ_playlist(html_content):
    """解析QQ音乐播放页面HTML，提取歌曲信息

    :param str html_content: HTML内容
    :return dict: 包含歌曲信息的字典
    """
    try:
        # 创建一个空字典
        result_dict = {}
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(html_content, 'html.parser')
        # 找到歌曲列表
        song_list = soup.find('ul', class_='songlist__list')
        if song_list is None:
            return result_dict
        song_list = song_list.find_all('li')
        # 遍历歌曲列表
        for song in song_list:
            try:
                number_elem = song.find(class_="songlist__number")
                name_elem = song.find(class_="songlist__songname_txt")
                author_elem = song.find(class_="playlist__author")
                
                # 检查必要元素是否存在
                if not all([number_elem, name_elem, author_elem]):
                    continue
                    
                res_number = number_elem.text.strip()
                
                # 检查歌曲名称元素
                name_link = name_elem.find('a')
                if not name_link:
                    continue
                res_name = name_link.text.strip()
                res_author = author_elem.text.strip()
                
                result_dict[res_number] = [res_name, res_author]
                
            except (AttributeError, Exception):
                # 如果某个歌曲解析失败，跳过继续处理下一个
                continue

        # 返回结果字典
        return result_dict
        
    except Exception as e:
        print(f'Error parsing QQ playlist HTML: {e}')
        return {}

def html_content_2_QQ_songlist(html_content):
    """解析QQ音乐歌单页面HTML，提取歌曲信息
    通过这个链接可以获得QQ音乐完整歌单
    https://y.qq.com/musicmac/v6/playlist/detail.html?id={id}

    :param str html_content: HTML内容
    :return dict: 包含歌曲信息的字典
    """
    try:
        # 创建一个空字典
        result_dict = {}
        # 创建BeautifulSoup对象
        soup = BeautifulSoup(html_content, 'html.parser')
        # 找到歌曲列表
        song_list_box = soup.find('div', id='songlist_box')
        if song_list_box is None:
            return result_dict
            
        song_list = song_list_box.find_all('li', class_='songlist__li')
        # 遍历歌曲列表
        i = 1
        for song in song_list:
            try:
                name_elem = song.find(class_="mod_songname__name")
                author_elem = song.find(class_="songlist__singer")
                
                # 检查必要元素是否存在
                if not all([name_elem, author_elem]):
                    continue
                    
                res_name = name_elem.text.strip()
                res_author = author_elem.text.strip()
                result_dict[i] = [res_name, res_author]
                i += 1
                
            except (AttributeError, Exception):
                # 如果某个歌曲解析失败，跳过继续处理下一个
                continue

        # 返回结果字典
        return result_dict
        
    except Exception as e:
        print(f'Error parsing QQ songlist HTML: {e}')
        return {}

def html_content_2_netease_playlist(html_content):
    """解析网易云音乐播放页面HTML，提取歌曲信息

    :param str html_content: HTML内容
    :return dict: 包含歌曲信息的字典
    """
    try:
        # 创建一个空字典
        result_dict = {}
        # 使用BeautifulSoup解析HTML内容
        soup = BeautifulSoup(html_content, 'html.parser')
        # 找到歌曲列表
        song_list = soup.find('ul', class_='f-cb')
        if song_list is None:
            return result_dict
            
        song_list = song_list.find_all('li')
        # 遍历歌曲列表
        for song in song_list:
            try:
                # 检查是否有data-id属性
                if not song.has_attr('data-id'):
                    continue
                    
                res_id = song['data-id']
                
                name_elem = song.find(class_="col-2")
                author_elem = song.find(class_="col-4")
                
                # 检查必要元素是否存在
                if not all([name_elem, author_elem]):
                    continue
                    
                res_name = name_elem.text.strip()
                
                # 检查作者信息结构
                author_span = author_elem.find('span')
                if not author_span:
                    continue
                    
                author_link = author_span.find('a')
                if not author_link:
                    continue
                    
                res_author = author_link.text.strip()
                result_dict[res_id] = [res_name, res_author]
                
            except (AttributeError, Exception):
                # 如果某个歌曲解析失败，跳过继续处理下一个
                continue

        # 返回结果字典
        return result_dict
        
    except Exception as e:
        print(f'Error parsing NetEase playlist HTML: {e}')
        return {}

def html_content_2_netease_songlist(html_content):
    """解析网易云音乐歌单页面HTML，提取歌曲信息

    :param str html_content: HTML内容
    :return dict: 包含歌曲信息的字典
    """
    # 创建一个空字典
    result_dict = {}
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'html.parser')
    # 找到所有的<tr>标签
    tr_list = soup.find_all('tr')
    # 遍历<tr>标签列表
    for tr in tr_list:
        # 找到第一个带有data-res-id属性的子元素
        res_id = tr.find(attrs={"data-res-id": True})
        # 如果找到了data-res-id属性
        if res_id:
            # 查找并删除所有class名为soil的元素
            for soil in tr.find_all(class_='soil'):
                soil.decompose()
            res_name_element = tr.find('a', href=re.compile(r'song\?id='))
            if res_name_element:
                res_name_b = res_name_element.find('b')
                if res_name_b:
                    res_name = res_name_b.text.replace('\n', '')
                else:
                    continue
            else:
                continue
                
            res_author_element = tr.find('a', href=re.compile(r'artist\?id='))
            if res_author_element and res_author_element.parent:
                res_author = res_author_element.parent.text.replace('\n', '')
            else:
                continue
                
            result_dict[res_id['data-res-id']] = [res_name, res_author]

    # 返回结果字典
    return result_dict

def download_netease_free(id, name, author, music_folder, error_dict):
    """通过ID下载网易云音乐的免费歌曲

    :param str id: 歌曲ID
    :param str name: 歌曲名称
    :param str author: 歌手名称
    :param str music_folder: 音乐文件保存路径
    :param dict error_dict: 用于存储下载失败的歌曲信息的字典
    """
    try:
        print(f'Trying to download: {author} - {name}')
        
        # 清理输入参数，防止路径遍历攻击
        safe_name = _sanitize_filename(name)
        safe_author = _sanitize_filename(author)
        
        # 通过这个id拼接出一个url
        url = f'https://music.163.com/song/media/outer/url?id={id}'
        
        # 使用requests库发送一个get请求，获取重定向后的url
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f'Network error while checking URL: {e}')
            error_dict[id] = [name, author]
            return
        
        new_url = response.url
        
        # 判断new_url里是否包含"404"
        if '404' not in new_url:
            try:
                response = requests.get(new_url, timeout=30, stream=True)
                response.raise_for_status()
                
                # 根据Content-Type确定文件扩展名
                content_type = response.headers.get('Content-Type', '')
                if 'audio/mpeg' in content_type:
                    file_extension = '.mp3'
                elif 'audio/wav' in content_type:
                    file_extension = '.wav'
                elif 'audio/ogg' in content_type:
                    file_extension = '.ogg'
                elif 'audio/flac' in content_type:
                    file_extension = '.flac'
                elif 'audio/aac' in content_type:
                    file_extension = '.aac'
                elif 'audio/x-m4a' in content_type:
                    file_extension = '.m4a'
                else:
                    # 非音频文件类型，记录错误
                    print(f'Unsupported content type: {content_type}')
                    error_dict[id] = [name, author]
                    return
                
                # 拼接文件保存路径
                filename = f'{safe_author} - {safe_name}{file_extension}'
                file_path = os.path.join(music_folder, filename)
                
                # 检查路径安全性
                if not _is_safe_path(file_path, music_folder):
                    print(f'Path traversal attempt detected: {file_path}')
                    error_dict[id] = [name, author]
                    return
                
                # 确保目录存在
                os.makedirs(music_folder, exist_ok=True)
                
                # 以二进制写入文件
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                print(f'Downloaded: {safe_author} - {safe_name}{file_extension}')
                
            except requests.exceptions.RequestException as e:
                print(f'Network error during download: {e}')
                error_dict[id] = [name, author]
            except (IOError, OSError) as e:
                print(f'File system error: {e}')
                error_dict[id] = [name, author]
            except Exception as e:
                print(f'Unexpected error during download: {e}')
                error_dict[id] = [name, author]
        else:
            print(f'Song not found (404): {author} - {name}')
            error_dict[id] = [name, author]
            
    except Exception as e:
        print(f'Unexpected error in download_netease_free: {e}')
        error_dict[id] = [name, author]

def format_music_names_for_qq_importing(file_names):
    """格式化音乐文件名，用于QQ音乐歌单导入

    :param list file_names: 文件名列表，格式为["歌手 - 歌名.后缀"]
    :return list: 格式化后的文件名列表，格式为["歌手《歌名》"]
    """
    result = []
    for name in file_names:
        try:
            parts = name.split(' - ', 1)  # 只分割第一个分隔符
            if len(parts) == 2:
                # 提取歌名部分，去除文件扩展名
                song_part = parts[1]
                song_name = os.path.splitext(song_part)[0]
                formatted = f'{parts[0]}《{song_name}》'
                result.append(formatted)
            else:
                # 如果格式不正确，跳过或保持原样
                result.append(name)
        except (IndexError, Exception):
            # 如果处理失败，保持原样
            result.append(name)
    return result

def format_music_names_for_netease_importing(file_names):
    """格式化音乐文件名，用于网易云音乐歌单导入

    :param list file_names: 文件名列表，格式为["歌手 - 歌名.后缀"]
    :return list: 格式化后的文件名列表，格式为["歌名 - 歌手"]
    """
    result = []
    for name in file_names:
        try:
            parts = name.split(' - ', 1)  # 只分割第一个分隔符
            if len(parts) == 2:
                # 提取歌名部分，去除文件扩展名
                song_part = parts[1]
                song_name = os.path.splitext(song_part)[0]
                formatted = f'{song_name} - {parts[0]}'
                result.append(formatted)
            else:
                # 如果格式不正确，跳过或保持原样
                result.append(name)
        except (IndexError, Exception):
            # 如果处理失败，保持原样
            result.append(name)
    return result
