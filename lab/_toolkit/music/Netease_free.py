"""
File: Netease_free.py
Project: routine
Created: 2024-11-05 06:39:43
Author: Victor Cheng
Email: hi@victor42.work
Description: 从网易云音乐歌单下载非VIP歌曲

1. 打开网易云音乐歌单页面（如：https://music.163.com/#/playlist?id=xxxxxx）
2. 按F12打开开发者工具
3. 使用元素选择器选中歌曲列表区域
4. 右键点击选中的元素 → Copy → Copy outerHTML
5. 将复制的HTML代码保存到 music/m_list.html 文件中
6. 运行本脚本：python Netease_free.py
7. 非VIP歌曲会自动下载到指定目录，VIP歌曲会保存到 music/m_list.txt
"""

import os
import sys
import argparse

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(current_dir))

from utils.basic import get_param_value
from utils.music import (
    html_content_2_netease_songlist, sanitize_file_names,
    download_netease_free, format_music_names_for_qq_importing,
    format_music_names_for_netease_importing,
)
from utils.path import platform_type, PATH_DOWNLOADS_FROM_WIN, PATH_DOWNLOADS


def main():
    parser = argparse.ArgumentParser(
        description="从网易云音乐歌单下载非VIP歌曲",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--html-path", help="HTML文件路径（默认：m_list.html）")
    parser.add_argument("--output", "-o", help="输出文件夹路径（默认：Netease_free）")
    parser.add_argument(
        "--target-type",
        "-t",
        choices=["q", "n"],
        help="导入目标：q=QQ音乐，n=网易云音乐",
    )

    args = parser.parse_args()

    HTML_PATH = get_param_value(
        args, "html_path", script_default=os.path.join(current_dir, "m_list.html")
    )

    if not os.path.exists(HTML_PATH):
        print(f"错误：HTML文件不存在: {HTML_PATH}")
        sys.exit(1)

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    default_output = (
        PATH_DOWNLOADS_FROM_WIN if platform_type == "wsl" else PATH_DOWNLOADS
    )
    output = get_param_value(
        args,
        "output",
        script_default=os.path.join(default_output, "Netease_free"),
    )

    MUSIC_FOLDER = output
    if not os.path.exists(MUSIC_FOLDER):
        os.makedirs(MUSIC_FOLDER)

    result_dict = html_content_2_netease_songlist(html_content)
    result_dict = sanitize_file_names(result_dict)

    error_dict = {}
    for id, attr in result_dict.items():
        download_netease_free(
            id,
            name=attr[0],
            author=attr[1],
            music_folder=MUSIC_FOLDER,
            error_dict=error_dict,
        )

    if error_dict:
        choice_dst = get_param_value(
            args,
            "target_type",
            prompt_text="歌曲要导入到哪个平台（q为QQ音乐，n为网易云音乐）",
        )

        if choice_dst == "q":
            formatted_error_names = format_music_names_for_qq_importing(
                [f"{attr[1]} - {attr[0]}" for attr in error_dict.values()]
            )
        elif choice_dst == "n":
            formatted_error_names = format_music_names_for_netease_importing(
                [f"{attr[1]} - {attr[0]}" for attr in error_dict.values()]
            )
        else:
            print("Invalid choice")
            sys.exit(1)

        TXT_PATH = os.path.join(current_dir, "m_list.txt")
        with open(TXT_PATH, "w", encoding="utf-8") as txt_file:
            for name in formatted_error_names:
                txt_file.write(name + "\n")
        print("-" * 20)
        print(f"VIP songs not downloaded, names in:\n{TXT_PATH}")


if __name__ == "__main__":
    main()
