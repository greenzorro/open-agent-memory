"""
File: api_telegram.py
Project: routine
Created: 2025-02-03
Author: Routine AI
Description: Telegram 消息发送工具，支持长文本自动分块和Markdown格式
"""

import requests
import sys
import os
import argparse
import json
from pathlib import Path

# Load keys from keys.json
keys_file_path = Path(__file__).parent / "keys.json"
try:
    with open(keys_file_path, 'r') as f:
        keys = json.load(f)
        DEFAULT_BOT_TOKEN = keys.get('TELEGRAM_BOT_TOKEN')
        DEFAULT_CHAT_ID = keys.get('TELEGRAM_CHAT_ID')
except Exception as e:
    print(f"Warning: Failed to load keys from {keys_file_path}: {e}")
    DEFAULT_BOT_TOKEN = None
    DEFAULT_CHAT_ID = None

def send_message(token, chat_id, text, parse_mode="Markdown"):
    """
    Sends a message to the Telegram chat.

    :param token: Bot API token
    :param chat_id: Target chat ID
    :param text: Message content
    :param parse_mode: 'Markdown' (default) or None for plain text
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)

def send_telegram_message(message, bot_token=None, chat_id=None):
    """
    Unified function to send message (supports chunking)

    :param message: The message string to send
    :param bot_token: Optional override for bot token
    :param chat_id: Optional override for chat ID
    """
    token = bot_token or DEFAULT_BOT_TOKEN
    chat = chat_id or DEFAULT_CHAT_ID

    if not token or not chat:
        print("Error: Bot token and Chat ID must be provided either via arguments or keys.json.")
        return

    # Telegram limit is 4096 chars.
    MAX_LENGTH = 4090

    if len(message) <= MAX_LENGTH:
        messages = [message]
    else:
        messages = []
        current_chunk = ""
        for line in message.splitlines(keepends=True):
            if len(current_chunk) + len(line) > MAX_LENGTH:
                messages.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += line
        if current_chunk:
            messages.append(current_chunk)

    print(f"Sending content in {len(messages)} chunk(s)...")

    for i, msg in enumerate(messages):
        success, result = send_message(token, chat, msg)
        if success:
            print(f"Chunk {i+1}/{len(messages)} sent successfully.")
        else:
            print(f"Failed to send chunk {i+1}: {result}")
            # Fallback to plain text
            print("Retrying as plain text...")
            success_plain, result_plain = send_message(token, chat, msg, parse_mode=None)
            if success_plain:
                 print("Sent as plain text.")
            else:
                 print(f"Failed again: {result_plain}")

def main():
    parser = argparse.ArgumentParser(description="Send a text file content to Telegram.")
    parser.add_argument("file", help="Path to the file to send", nargs='?')
    parser.add_argument("--text", help="Direct text to send")
    args = parser.parse_args()

    # Priority: Direct text > File
    content = ""
    if args.text:
        content = args.text
    elif args.file:
        if not os.path.exists(args.file):
            print(f"Error: File {args.file} not found.")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        # Try reading from stdin if no args provided (support pipe)
        if not sys.stdin.isatty():
             content = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(1)

    send_telegram_message(content)

if __name__ == "__main__":
    main()
