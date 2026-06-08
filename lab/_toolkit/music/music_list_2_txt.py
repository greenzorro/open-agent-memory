"""
File: music_list_2_txt.py
Project: routine
Created: 2024-11-29 08:25:50
Author: Victor Cheng
Email: hi@victor42.work
Description: 把歌单列表保存成QQ或网易云歌单导入所需格式

1. 打开歌单页面（QQ音乐或网易云音乐）
2. 按F12打开开发者工具
3. 使用元素选择器选中歌曲列表区域
4. 右键点击选中的元素 → Copy → Copy outerHTML
5. 将复制的HTML代码保存到 music/m_list.html 文件中
6. 运行本脚本：python music_list_2_txt.py
7. 生成 music/m_list.txt（可导入到目标平台的格式）

支持的歌单类型：
- 网易云音乐歌单页：https://music.163.com/#/playlist?id=xxxxxx
- QQ音乐歌单页：https://y.qq.com/musicmac/v6/playlist/detail.html?id=xxxxxx
"""

import os
import sys
import argparse

current_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.dirname(current_dir))

from utils.basic import get_param_value
from utils.music import (
    html_content_2_QQ_songlist, html_content_2_netease_songlist,
    sanitize_file_names, format_music_names_for_qq_importing,
    format_music_names_for_netease_importing,
)

SELF_PATH = os.path.dirname(__file__)


def main():
    parser = argparse.ArgumentParser(
        description="HTML歌单转换为导入格式txt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--source-type",
        "-s",
        choices=["q", "n"],
        help="HTML来源：q=QQ音乐歌单页，n=网易云音乐歌单页",
    )
    parser.add_argument(
        "--target-type",
        "-t",
        choices=["q", "n"],
        help="导入目标：q=QQ音乐，n=网易云音乐",
    )
    parser.add_argument("--html-path", help="HTML文件路径（默认：m_list.html）")
    parser.add_argument("--output", "-o", help="TXT文件路径（默认：m_list.txt）")

    args = parser.parse_args()

    HTML_PATH = get_param_value(
        args, "html_path", script_default=os.path.join(current_dir, "m_list.html")
    )
    TXT_PATH = get_param_value(
        args, "output", script_default=os.path.join(current_dir, "m_list.txt")
    )

    if not os.path.exists(HTML_PATH):
        print(f"错误：HTML文件不存在: {HTML_PATH}")
        sys.exit(1)

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html_content = f.read()

    choice_src = get_param_value(
        args,
        "source_type",
        prompt_text="HTML歌曲列表来自哪个页面（q为QQ音乐歌单页面，n为网易云音乐歌单页面）",
    )

    if choice_src == "q":
        result_dict = html_content_2_QQ_songlist(html_content)
    elif choice_src == "n":
        result_dict = html_content_2_netease_songlist(html_content)
    else:
        print("Invalid choice")
        sys.exit(1)

    result_dict = sanitize_file_names(result_dict)

    file_names = [f"{value[1]} - {value[0]}" for value in result_dict.values()]

    choice_dst = get_param_value(
        args,
        "target_type",
        prompt_text="歌曲要导入到哪个平台（q为QQ音乐，n为网易云音乐）",
    )

    if choice_dst == "q":
        formatted_names = format_music_names_for_qq_importing(file_names)
    elif choice_dst == "n":
        formatted_names = format_music_names_for_netease_importing(file_names)
    else:
        print("Invalid choice")
        sys.exit(1)

    with open(TXT_PATH, "w", encoding="utf-8") as txt_file:
        for name in formatted_names:
            txt_file.write(name + "\n")
    print(f"{TXT_PATH} created")


if __name__ == "__main__":
    main()
