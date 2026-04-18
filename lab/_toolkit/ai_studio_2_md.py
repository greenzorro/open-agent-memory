"""
File: ai_studio_2_md.py
Project: open-agent-memory
Created: 2025-11-01 10:24:26
Author: Victor Cheng
Email: your_email@example.com
Description: 将AI Studio导出的JSON聊天记录转换为Markdown格式
"""

import os
import sys
import argparse
import json
from utils import *


def extract_chat_from_json(json_file_path, include_thoughts=False):
    """从JSON文件中提取聊天记录

    :param str json_file_path: JSON文件路径
    :param bool include_thoughts: 是否包含思考过程
    :return list: 聊天记录列表，每个元素包含role和text
    """
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        chunks = data.get("chunkedPrompt", {}).get("chunks", [])

        chat_records = []
        for chunk in chunks:
            role = chunk.get("role", "")
            text = chunk.get("text", "").strip()

            should_include = role in ["user", "model"] and text
            if not include_thoughts:
                should_include = should_include and not chunk.get("isThought", False)

            if should_include:
                chat_records.append({"role": role, "text": text})

        return chat_records

    except Exception as e:
        print(f"读取JSON文件时出错: {e}")
        return []


def generate_markdown_content(chat_records):
    """生成markdown格式的聊天记录

    :param list chat_records: 聊天记录列表
    :return str: markdown格式的内容
    """
    markdown_lines = []
    round_count = 0

    for record in chat_records:
        role = record["role"]
        text = record["text"]

        if role == "user":
            round_count += 1
            lines = text.split("\n")
            if lines:
                quoted_lines = [f"> **用户**：{lines[0]}"]
                quoted_lines.extend(f"> {line}" for line in lines[1:])
                quoted_text = "\n".join(quoted_lines)
            else:
                quoted_text = "> **用户**："
            markdown_lines.append(
                f"# 💬💬💬 第{round_count}回合 💬💬💬\n\n{quoted_text}\n"
            )
        elif role == "model":
            markdown_lines.append(f"{text}\n")

    return "\n".join(markdown_lines)


def process_single_file(json_file_path, output_folder, include_thoughts=False):
    """处理单个JSON文件

    :param str json_file_path: JSON文件路径
    :param str output_folder: 输出目录路径
    :param bool include_thoughts: 是否包含思考过程
    :return bool: 处理是否成功
    """
    chat_records = extract_chat_from_json(json_file_path, include_thoughts)

    if not chat_records:
        print(f"文件 {os.path.basename(json_file_path)} 未找到有效的聊天记录")
        return False

    markdown_content = generate_markdown_content(chat_records)

    base_name = os.path.splitext(os.path.basename(json_file_path))[0]
    output_file_name = f"{base_name}.md"
    output_file_path = os.path.join(output_folder, output_file_name)

    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        print(
            f"✓ {os.path.basename(json_file_path)} -> {output_file_name} (共 {len(chat_records)} 条记录)"
        )
        return True

    except Exception as e:
        print(f"✗ 写入文件 {output_file_name} 时出错: {e}")
        return False


def is_json_file(filename):
    """判断文件是否为JSON文件（有.json扩展名或无扩展名）"""
    if filename.lower().endswith(".json"):
        return True
    if "." not in filename:
        return True
    return False


def main():
    parser = argparse.ArgumentParser(
        description="将AI Studio导出的JSON聊天记录转换为Markdown格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--source", "-s", help="源文件夹路径（包含JSON文件）")
    parser.add_argument(
        "--output",
        "-o",
        help="输出文件夹路径（默认：PATH_DOWNLOADS/AI_Studio_Chat）",
    )
    parser.add_argument(
        "--include-thoughts",
        action="store_true",
        help="包含AI思考过程（默认：不包含）",
    )

    args = parser.parse_args()

    SRC_FOLDER = get_param_value(args, "source", prompt_text="源文件夹路径")

    if not os.path.exists(SRC_FOLDER):
        print(f"错误：源路径不存在: {SRC_FOLDER}")
        sys.exit(1)

    default_output = os.path.join(PATH_DOWNLOADS, "AI_Studio_Chat")
    OUTPUT_FOLDER = get_param_value(args, "output", script_default=default_output)

    include_thoughts = bool(
        get_param_value(args, "include_thoughts", script_default=False)
    )

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    processed_count = 0
    success_count = 0

    for root, dirs, files in os.walk(SRC_FOLDER):
        for filename in files:
            if filename.startswith(".") or not is_json_file(filename):
                continue

            json_file_path = os.path.join(root, filename)
            processed_count += 1

            if process_single_file(json_file_path, OUTPUT_FOLDER, include_thoughts):
                success_count += 1

    print(
        f"\n转换完成！共处理 {processed_count} 个JSON文件，成功转换 {success_count} 个文件"
    )
    if success_count > 0:
        print(f"输出目录: {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()
