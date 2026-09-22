"""
File: api_email.py
Project: routine
Created: 2026-09-22
Author: Victor Cheng
Email: hi@victor42.work
Description: 邮件发送工具。经 Resend HTTPS API 发送纯文本与附件，供定时报告等日常投递使用。
"""

import argparse
import base64
import json
import sys
from pathlib import Path

import requests


RESEND_EMAILS_URL = "https://api.resend.com/emails"
TEXT_TIMEOUT = 30
ATTACHMENT_TIMEOUT = 120
MAX_SUBJECT_LENGTH = 120
# Resend 单封含附件上限 40MB；原始文件留出正文与 base64 膨胀余量。
MAX_ATTACHMENT_BYTES = 30 * 1024 * 1024

keys_file_path = Path(__file__).parent / "keys.json"
try:
    with open(keys_file_path, "r", encoding="utf-8") as f:
        keys = json.load(f)
        DEFAULT_API_KEY = keys.get("RESEND_API_KEY")
        DEFAULT_EMAIL_FROM = keys.get("EMAIL_FROM")
        DEFAULT_EMAIL_TO = keys.get("EMAIL_TO")
except Exception as e:
    print(f"Warning: Failed to load keys from {keys_file_path}: {e}")
    DEFAULT_API_KEY = None
    DEFAULT_EMAIL_FROM = None
    DEFAULT_EMAIL_TO = None


def _normalize_recipients(to):
    if to is None:
        to = DEFAULT_EMAIL_TO
    if isinstance(to, str):
        recipients = [part.strip() for part in to.split(",") if part.strip()]
    elif isinstance(to, (list, tuple)):
        recipients = [str(part).strip() for part in to if str(part).strip()]
    else:
        recipients = []
    return recipients


def _resolve_credentials(api_key=None, from_addr=None, to=None):
    key = api_key or DEFAULT_API_KEY
    sender = (from_addr or DEFAULT_EMAIL_FROM or "").strip()
    recipients = _normalize_recipients(to)
    if not key or not sender or not recipients:
        print(
            "Error: API key, from address, and recipient must be provided "
            "either via arguments or keys.json "
            "(RESEND_API_KEY, EMAIL_FROM, EMAIL_TO)."
        )
        return None, None, None
    return key, sender, recipients


def subject_from_text(text, max_length=MAX_SUBJECT_LENGTH):
    """用第一行非空文本做主题；过长则截断。没有可用行时返回 Report。"""
    if max_length <= 1:
        raise ValueError("max_length 必须大于 1")
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if len(line) <= max_length:
            return line
        return line[: max_length - 1] + "…"
    return "Report"


def _resolve_subject(subject, text):
    if subject and str(subject).strip():
        return str(subject).strip()
    return subject_from_text(text)


def send_email(api_key, from_addr, to, subject, text, attachments=None, timeout=TEXT_TIMEOUT):
    """
    POST 一封邮件到 Resend。

    :param to: 收件人字符串、逗号分隔字符串，或字符串列表
    :return: (True, response_json) 或 (False, error)
    """
    recipients = _normalize_recipients(to)
    if not api_key or not from_addr or not recipients:
        return False, "Missing API key, from address, or recipient"
    if not subject or not str(subject).strip():
        return False, "Missing subject"
    if text is None or not str(text).strip():
        return False, "Missing text body"

    payload = {
        "from": from_addr,
        "to": recipients,
        "subject": str(subject).strip(),
        "text": text,
    }
    if attachments:
        payload["attachments"] = attachments

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(
            RESEND_EMAILS_URL,
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        detail = str(e)
        response = getattr(e, "response", None)
        body = getattr(response, "text", "") if response is not None else ""
        if body:
            detail = body
        return False, detail


def send_email_message(message, subject=None, to=None, from_addr=None, api_key=None):
    """
    发送一封纯文本邮件。主题缺省时取正文第一行非空文本。

    :return: True on success, False otherwise
    """
    key, sender, recipients = _resolve_credentials(api_key, from_addr, to)
    if not key:
        return False
    if message is None or not str(message).strip():
        print("Error: Message is empty.")
        return False

    resolved_subject = _resolve_subject(subject, message)
    print(f"Sending email ({len(recipients)} recipient(s)): {resolved_subject}")
    success, result = send_email(key, sender, recipients, resolved_subject, message)
    if success:
        print("Email sent successfully.")
        return True
    print(f"Failed to send email: {result}")
    return False


def send_email_file(file_path, subject=None, body=None, to=None, from_addr=None, api_key=None):
    """
    把本地文件作为附件发送。正文缺省时写一行附件说明。空文件拒绝；原始文件不超过 30MB。

    :return: True on success, False otherwise
    """
    key, sender, recipients = _resolve_credentials(api_key, from_addr, to)
    if not key:
        return False

    path = Path(file_path)
    if not path.is_file():
        print(f"Error: File {file_path} not found.")
        return False

    size = path.stat().st_size
    if size <= 0:
        print(f"Error: File {file_path} is empty.")
        return False
    if size > MAX_ATTACHMENT_BYTES:
        print(
            f"Error: File exceeds attachment limit "
            f"({size} bytes > {MAX_ATTACHMENT_BYTES} bytes)."
        )
        return False

    text = body if body and str(body).strip() else f"附件：{path.name}"
    resolved_subject = _resolve_subject(subject, text if body else path.name)
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    attachments = [{"filename": path.name, "content": encoded}]

    print(f"Sending {path.name} as attachment ({size} bytes): {resolved_subject}")
    success, result = send_email(
        key,
        sender,
        recipients,
        resolved_subject,
        text,
        attachments=attachments,
        timeout=ATTACHMENT_TIMEOUT,
    )
    if success:
        print("Email sent successfully.")
        return True
    print(f"Failed to send email: {result}")
    return False


def main():
    parser = argparse.ArgumentParser(
        description="Send plain text, or a file attachment, by email via Resend."
    )
    parser.add_argument(
        "file",
        help="Path to a text file whose content will be sent as the email body",
        nargs="?",
    )
    parser.add_argument("--text", help="Direct text to send")
    parser.add_argument("--subject", help="Email subject; defaults to the first non-empty line")
    parser.add_argument(
        "--attach",
        metavar="PATH",
        help="Send a local file as an attachment instead of a text body",
    )
    parser.add_argument("--body", help="Body text for --attach")
    args = parser.parse_args()

    if args.attach:
        if args.text or args.file:
            print("Error: --text and the file argument do not apply with --attach. Use --body.")
            sys.exit(1)
        ok = send_email_file(args.attach, subject=args.subject, body=args.body)
        sys.exit(0 if ok else 1)

    if args.body:
        print("Error: --body only applies with --attach.")
        sys.exit(1)

    content = ""
    if args.text:
        content = args.text
    elif args.file:
        if not Path(args.file).is_file():
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

    ok = send_email_message(content, subject=args.subject)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
