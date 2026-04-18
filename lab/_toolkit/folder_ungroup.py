"""
File: folder_ungroup.py
Project: open-agent-memory
Created: 2026-01-23 06:00:26
Author: Victor Cheng
Email: your_email@example.com
Description: 把文件里的文件夹拆开，取出全部文件
"""

import os
import sys
import argparse
from utils import *


def main():
    parser = argparse.ArgumentParser(
        description="把文件里的文件夹拆开，取出全部文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--source", "-s", help="源文件夹路径")
    parser.add_argument(
        "--output", "-o", help="输出文件夹路径（默认：PATH_DOWNLOADS/Ungrouped）"
    )

    args = parser.parse_args()

    SRC_FOLDER = get_param_value(args, "source", prompt_text="源文件夹路径")

    if not os.path.exists(SRC_FOLDER):
        print(f"错误：源路径不存在: {SRC_FOLDER}")
        sys.exit(1)

    default_output = os.path.join(PATH_DOWNLOADS, "Ungrouped")
    DST_FOLDER = get_param_value(args, "output", script_default=default_output)

    if not os.path.exists(DST_FOLDER):
        os.makedirs(DST_FOLDER)

    folder_ungroup(SRC_FOLDER, DST_FOLDER)
    print(f"ungrouped to:\n{DST_FOLDER}")


if __name__ == "__main__":
    main()
