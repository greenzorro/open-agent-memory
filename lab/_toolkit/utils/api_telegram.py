"""
File: api_telegram.py
Project: routine
Created: 2025-02-03
Author: Victor Cheng
Email: hi@victor42.work
Description: Telegram 消息发送工具，支持长文本自动分块、Markdown格式，以及图片/文件上传
"""

import requests
import sys
import os
import argparse
import json
import mimetypes
from pathlib import Path

MAX_MESSAGE_LENGTH = 4090
MAX_CAPTION_LENGTH = 1024
MAX_PHOTO_BYTES = 10 * 1024 * 1024
MAX_DOCUMENT_BYTES = 50 * 1024 * 1024
UPLOAD_TIMEOUT = 120

# sendPhoto 适合的静态图；过大或失败时回退到 sendDocument
PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

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


def _resolve_credentials(bot_token=None, chat_id=None):
    token = bot_token or DEFAULT_BOT_TOKEN
    chat = chat_id or DEFAULT_CHAT_ID
    if not token or not chat:
        print("Error: Bot token and Chat ID must be provided either via arguments or keys.json.")
        return None, None
    return token, chat


def is_photo_file(path):
    """判断路径是否适合走 sendPhoto（按扩展名）。"""
    return Path(path).suffix.lower() in PHOTO_EXTENSIONS


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
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)


def _post_multipart(url, data, file_field, file_path, timeout=UPLOAD_TIMEOUT):
    """上传本地文件；成功返回 (True, json)，失败返回 (False, error)。"""
    filename = os.path.basename(file_path)
    mime_type, _ = mimetypes.guess_type(filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    try:
        with open(file_path, "rb") as f:
            files = {file_field: (filename, f, mime_type)}
            response = requests.post(url, data=data, files=files, timeout=timeout)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)


def send_photo(token, chat_id, file_path, caption=None, parse_mode="Markdown"):
    """通过 sendPhoto 上传图片。"""
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
        if parse_mode:
            data["parse_mode"] = parse_mode
    return _post_multipart(url, data, "photo", file_path)


def send_document(token, chat_id, file_path, caption=None, parse_mode="Markdown"):
    """通过 sendDocument 上传任意文件。"""
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    data = {"chat_id": chat_id}
    if caption:
        data["caption"] = caption
        if parse_mode:
            data["parse_mode"] = parse_mode
    return _post_multipart(url, data, "document", file_path)


def split_message(message, max_length=MAX_MESSAGE_LENGTH):
    """按 Telegram 长度限制分块，并尽量在换行处切分。"""
    if max_length <= 0:
        raise ValueError("max_length 必须大于 0")
    if len(message) <= max_length:
        return [message]

    chunks = []
    remaining = message
    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        split_at = remaining.rfind("\n", 0, max_length + 1)
        if split_at <= 0:
            split_at = max_length
        else:
            split_at += 1

        chunks.append(remaining[:split_at])
        remaining = remaining[split_at:]

    return chunks


def send_telegram_message(message, bot_token=None, chat_id=None):
    """
    Unified function to send message (supports chunking)

    :param message: The message string to send
    :param bot_token: Optional override for bot token
    :param chat_id: Optional override for chat ID
    :return: True if all chunks sent successfully, else False
    """
    token, chat = _resolve_credentials(bot_token, chat_id)
    if not token:
        return False

    messages = split_message(message)

    print(f"Sending content in {len(messages)} chunk(s)...")

    all_ok = True
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
                all_ok = False
    return all_ok


def _send_media_with_caption_fallback(send_fn, token, chat, file_path, caption):
    """先 Markdown caption，失败则纯文本 caption，再失败则无 caption。"""
    if caption:
        success, result = send_fn(token, chat, file_path, caption=caption, parse_mode="Markdown")
        if success:
            return True, result
        print(f"Markdown caption failed: {result}")
        print("Retrying with plain caption...")
        success, result = send_fn(token, chat, file_path, caption=caption, parse_mode=None)
        if success:
            return True, result
        print(f"Plain caption failed: {result}")
        print("Retrying without caption...")

    return send_fn(token, chat, file_path, caption=None, parse_mode=None)


def send_telegram_file(file_path, caption=None, as_photo=None, bot_token=None, chat_id=None):
    """
    上传本地文件到 Telegram。

    :param file_path: 本地文件路径
    :param caption: 可选说明文字；超过 1024 字符时改为文件发送后另发文本
    :param as_photo: True 强制 sendPhoto，False 强制 sendDocument，None 按扩展名自动选择
    :param bot_token: 可选覆盖 bot token
    :param chat_id: 可选覆盖 chat id
    :return: True on success, False otherwise
    """
    token, chat = _resolve_credentials(bot_token, chat_id)
    if not token:
        return False

    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File {file_path} not found.")
        return False

    size = path.stat().st_size
    if size <= 0:
        print(f"Error: File {file_path} is empty.")
        return False
    if size > MAX_DOCUMENT_BYTES:
        print(
            f"Error: File exceeds Bot API upload limit "
            f"({size} bytes > {MAX_DOCUMENT_BYTES} bytes)."
        )
        return False

    use_photo = is_photo_file(path) if as_photo is None else bool(as_photo)
    if use_photo and size > MAX_PHOTO_BYTES:
        print(
            f"Photo exceeds sendPhoto limit ({size} bytes > {MAX_PHOTO_BYTES} bytes); "
            "sending as document instead."
        )
        use_photo = False

    overflow_caption = None
    media_caption = caption
    if caption and len(caption) > MAX_CAPTION_LENGTH:
        print(
            f"Caption exceeds {MAX_CAPTION_LENGTH} chars; "
            "sending file first, then caption as text."
        )
        overflow_caption = caption
        media_caption = None

    send_fn = send_photo if use_photo else send_document
    kind = "photo" if use_photo else "document"
    print(f"Sending {path.name} as {kind} ({size} bytes)...")

    success, result = _send_media_with_caption_fallback(
        send_fn, token, chat, str(path), media_caption
    )
    if not success:
        if use_photo:
            print(f"sendPhoto failed: {result}")
            print("Falling back to sendDocument...")
            success, result = _send_media_with_caption_fallback(
                send_document, token, chat, str(path), media_caption
            )
        if not success:
            print(f"Failed to send file: {result}")
            return False

    print("File sent successfully.")

    if overflow_caption:
        return send_telegram_message(overflow_caption, bot_token=token, chat_id=chat)
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Send text, or upload a photo/document, to Telegram."
    )
    parser.add_argument(
        "file",
        help="Path to a text file whose content will be sent as messages",
        nargs="?",
    )
    parser.add_argument("--text", help="Direct text to send")
    parser.add_argument(
        "--attach",
        metavar="PATH",
        help="Upload a local file (photo or document) instead of sending text",
    )
    parser.add_argument("--caption", help="Caption for --attach (max 1024 chars inline)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--as-photo",
        action="store_true",
        help="Force sendPhoto for --attach",
    )
    mode.add_argument(
        "--as-document",
        action="store_true",
        help="Force sendDocument for --attach",
    )
    args = parser.parse_args()

    if args.attach:
        as_photo = True if args.as_photo else (False if args.as_document else None)
        ok = send_telegram_file(args.attach, caption=args.caption, as_photo=as_photo)
        sys.exit(0 if ok else 1)

    if args.caption or args.as_photo or args.as_document:
        print("Error: --caption/--as-photo/--as-document only apply with --attach.")
        sys.exit(1)

    # Priority: Direct text > File content > stdin
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
        if not sys.stdin.isatty():
            content = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(1)

    ok = send_telegram_message(content)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
