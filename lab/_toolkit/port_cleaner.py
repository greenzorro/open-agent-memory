"""
File: port_cleaner.py
Project: routine
Created: 2026-04-16 21:00:00
Author: Victor Cheng
Email: hi@victor42.work
Description: 工作目录文件归拢与过期清理，基于港口思维（https://victor42.eth.limo/post/3627）
"""

import sys
import time
import shutil
import argparse
from datetime import datetime
from pathlib import Path
from utils.basic import get_param_value

DEFAULT_TTL_DAYS = 7


def _ts():
    """格式化时间戳"""
    return datetime.now().strftime("%H:%M:%S")


def resolve_port(workdir: Path, port: str) -> Path:
    """Resolve port path — absolute if starts with /, otherwise relative to workdir."""
    if Path(port).is_absolute():
        return Path(port)
    return workdir / port


def collect_from_root(workdir: Path, exclude_dirs: set, exclude_files: set) -> list[Path]:
    """Find loose files and non-excluded directories in workdir root."""
    targets = []
    for item in workdir.iterdir():
        if item.is_file() and item.name not in exclude_files:
            targets.append(item)
        elif item.is_dir() and item.name not in exclude_dirs:
            targets.append(item)
    return targets


def collect_from_sources(workdir: Path, sources: list[str], exclude_files: set) -> list[Path]:
    """Recursively collect files from specified source directories."""
    targets = []
    for src in sources:
        src_dir = workdir / src
        if not src_dir.is_dir():
            continue
        for f in src_dir.rglob("*"):
            if f.is_file() and f.name not in exclude_files:
                targets.append(f)
    return targets


def move_to_port(filepath: Path, port: Path, dry_run: bool = False):
    """Move a file or directory to port/, handling name conflicts by appending counter."""
    dest = port / filepath.name
    if dest.exists():
        stem = filepath.stem if filepath.is_file() else filepath.name
        suffix = filepath.suffix if filepath.is_file() else ""
        counter = 1
        while dest.exists():
            dest = port / f"{stem}_{counter}{suffix}"
            counter += 1

    if not dry_run:
        shutil.move(str(filepath), str(dest))

    # 日志输出
    action = "Would move" if dry_run else "Moved"
    prefix = "Dir" if filepath.is_dir() else "File"
    print(f"[{_ts()}] {prefix}[{filepath.name}] {action}: {dest.name}")


def purge_old_files(port: Path, ttl_days: int, dry_run: bool = False):
    """Delete files and directories in port/ older than TTL (based on st_mtime)."""
    now = time.time()
    ttl_seconds = ttl_days * 24 * 3600
    purged_count = 0

    if not port.is_dir():
        return purged_count

    for item in port.iterdir():
        age = now - item.stat().st_mtime
        if age > ttl_seconds:
            action = "Would purge" if dry_run else "Purged"
            if item.is_file():
                size_kb = item.stat().st_size / 1024
                if not dry_run:
                    item.unlink()
                print(f"[{_ts()}] File[{item.name}] {action}: {size_kb:.0f}KB, {age/86400:.1f} days old")
            elif item.is_dir():
                if not dry_run:
                    shutil.rmtree(str(item))
                print(f"[{_ts()}] Dir[{item.name}] {action}: {age/86400:.1f} days old")
            purged_count += 1
    return purged_count


def main():
    """主函数：执行港口清理操作"""
    parser = argparse.ArgumentParser(
        description="工作目录文件归拢与过期清理",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 参数定义
    parser.add_argument("--source", "-s", help="工作目录路径")
    parser.add_argument("--port", "-p", help="港口目录名称或路径")
    parser.add_argument("--scan", nargs='+', help="要扫描的源目录")
    parser.add_argument("--exclude-dirs", nargs='+', help="根目录扫描时跳过的目录")
    parser.add_argument("--exclude-files", nargs='+', help="跳过的文件名")
    parser.add_argument("--ttl", type=int, help="文件过期天数（默认：7）")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不实际执行")

    args = parser.parse_args()

    # 判断是否交互式模式（无命令行参数）
    is_interactive = all([
        args.source is None,
        args.port is None,
        args.scan is None,
        args.exclude_dirs is None,
        args.exclude_files is None,
        args.ttl is None,
        not args.dry_run
    ])

    if is_interactive:
        print("=" * 60)
        print("Port Cleaner — 工作目录文件归拢与过期清理")
        print("=" * 60)
        print()
        print("基于港口思维：将散落的文件归拢到港口目录，并清理过期文件。")
        print()
        print("参数说明：")
        print("  • 工作目录：要清理的目标目录（必填）")
        print("  • 港口目录：归拢文件的存放位置（必填，相对或绝对路径）")
        print("  • 移出目录：要扫描的子目录，文件会被移到港口（可直接回车跳过）")
        print("  • 跳过目录：根目录扫描时忽略的目录（可直接回车跳过）")
        print("  • 跳过文件：扫描时忽略的文件名（可直接回车跳过）")
        print("  • 过期天数：港口中超过此天数的文件将被删除（默认7天）")
        print()
        print("-" * 60)
        print()

    # 使用 get_param_value 获取参数（支持交互式模式）
    workdir = Path(get_param_value(
        args, 'source',
        prompt_text="请输入工作目录路径"
    ))

    port_name = get_param_value(
        args, 'port',
        prompt_text="请输入港口目录名称或路径"
    )

    # 交互式模式提示输入，命令行模式使用默认空列表
    if is_interactive:
        sources_input = get_param_value(
            args, 'scan',
            prompt_text="请输入移出目录（多个用空格分隔）"
        )
        sources = sources_input.split() if isinstance(sources_input, str) else sources_input

        exclude_dirs_input = get_param_value(
            args, 'exclude_dirs',
            prompt_text="请输入根目录扫描时要跳过的目录（多个用空格分隔）"
        )
        exclude_dirs = exclude_dirs_input.split() if isinstance(exclude_dirs_input, str) else exclude_dirs_input

        exclude_files_input = get_param_value(
            args, 'exclude_files',
            prompt_text="请输入要跳过的文件名（多个用空格分隔）"
        )
        exclude_files = exclude_files_input.split() if isinstance(exclude_files_input, str) else exclude_files_input
    else:
        sources = get_param_value(args, 'scan', script_default=[])
        exclude_dirs = get_param_value(args, 'exclude_dirs', script_default=[])
        exclude_files = get_param_value(args, 'exclude_files', script_default=[])

    ttl_days = get_param_value(
        args, 'ttl',
        script_default=DEFAULT_TTL_DAYS
    )

    dry_run = args.dry_run

    # 解析路径
    port = resolve_port(workdir, port_name)
    exclude_dirs = set(exclude_dirs)
    exclude_files = set(exclude_files)

    # 自动排除 port 目录和 source 目录
    if port.is_relative_to(workdir):
        exclude_dirs.add(port.relative_to(workdir).as_posix())
    for src in sources:
        exclude_dirs.add(src)

    if not workdir.exists():
        print(f"Error: Working directory {workdir} does not exist.")
        sys.exit(1)

    port.mkdir(parents=True, exist_ok=True)

    # 显示配置信息
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"[{_ts()}] Port Cleaner {mode}")
    print(f"[{_ts()}] Workdir: {workdir}")
    print(f"[{_ts()}] Port:    {port}")
    print(f"[{_ts()}] Sources: {', '.join(sources)}")
    print(f"[{_ts()}] TTL:     {ttl_days} days")
    print()

    # Phase 1: Consolidate scattered items
    print(f"[{_ts()}] --- Phase 1: Consolidate scattered items ---")
    scattered = collect_from_root(workdir, exclude_dirs, exclude_files)
    scattered += collect_from_sources(workdir, sources, exclude_files)
    if scattered:
        for f in sorted(scattered):
            move_to_port(f, port, dry_run)
        print(f"[{_ts()}] Total: {len(scattered)} items consolidated")
    else:
        print(f"[{_ts()}] No scattered items found")

    print()

    # Phase 2: Purge expired items
    print(f"[{_ts()}] --- Phase 2: Purge expired items ---")
    purged_count = purge_old_files(port, ttl_days, dry_run)
    if purged_count:
        print(f"[{_ts()}] Total: {purged_count} items purged")
    else:
        print(f"[{_ts()}] No items exceeded TTL")

    # Summary
    remaining = sum(1 for _ in port.iterdir())
    print(f"\n[{_ts()}] Port status: {remaining} items in {port}")
    print(f"[{_ts()}] Done")


if __name__ == "__main__":
    main()