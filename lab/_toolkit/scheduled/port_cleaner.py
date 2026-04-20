"""
File: port_cleaner.py
Project: routine
Created: 2026-04-16 21:00:00
Author: Victor Cheng
Email: hi@victor42.work
Description: 沙盒工作目录文件归拢与过期清理，基于 Port Thinking
"""

import sys
import time
import shutil
import argparse
from pathlib import Path

DEFAULT_TTL_DAYS = 7


def resolve_port(workdir: Path, port: str) -> Path:
    """Resolve port path — absolute if starts with /, otherwise relative to workdir."""
    if Path(port).is_absolute():
        return Path(port)
    return workdir / port


def collect_from_root(workdir: Path, exclude_dirs: set, exclude_files: set) -> list[Path]:
    """Find loose files in workdir root (skip excluded dirs/files)."""
    targets = []
    for item in workdir.iterdir():
        if item.is_file() and item.name not in exclude_files:
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


def move_to_port(filepath: Path, port: Path, dry_run: bool = False) -> str:
    """Move a file to port/, handling name conflicts by appending counter."""
    dest = port / filepath.name
    if dest.exists():
        stem = filepath.stem
        suffix = filepath.suffix
        counter = 1
        while dest.exists():
            dest = port / f"{stem}_{counter}{suffix}"
            counter += 1

    action = "Would move" if dry_run else "Moving"
    if not dry_run:
        shutil.move(str(filepath), str(dest))
    return f"  {action}: {filepath.name} -> {dest.name}"


def purge_old_files(port: Path, ttl_days: int, dry_run: bool = False) -> list[str]:
    """Delete files in port/ older than TTL (based on st_mtime)."""
    now = time.time()
    ttl_seconds = ttl_days * 24 * 3600
    purged = []

    if not port.is_dir():
        return purged

    for item in port.iterdir():
        if not item.is_file():
            continue
        age = now - item.stat().st_mtime
        if age > ttl_seconds:
            action = "Would purge" if dry_run else "Purged"
            size_kb = item.stat().st_size / 1024
            if not dry_run:
                item.unlink()
            purged.append(f"  {action}: {item.name} ({size_kb:.0f}KB, {age/86400:.1f} days old)")
    return purged


def main():
    parser = argparse.ArgumentParser(
        description="Port Cleaner — consolidate scattered files & purge by TTL"
    )

    # Required parameters
    required = parser.add_argument_group("required arguments")
    required.add_argument("--workdir", type=str, required=True,
                          help="Working directory to clean")
    required.add_argument("--port", type=str, required=True,
                          help="Port (consolidation) directory; "
                               "absolute path or relative to workdir")
    required.add_argument("--sources", nargs='+', required=True,
                          help="Source directories to scan, relative to workdir")
    required.add_argument("--exclude-dirs", nargs='+', required=True,
                          help="Directories to skip in root scan, relative to workdir")
    required.add_argument("--exclude-files", nargs='+', required=True,
                          help="Files to skip by exact name")

    # Optional parameters
    parser.add_argument("--ttl", type=int, default=DEFAULT_TTL_DAYS,
                        help="File age threshold in days (default: %(default)s)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview without making changes")

    args = parser.parse_args()

    workdir = Path(args.workdir)
    port = resolve_port(workdir, args.port)
    exclude_dirs = set(args.exclude_dirs)
    exclude_files = set(args.exclude_files)

    if not workdir.exists():
        print(f"Error: Working directory {workdir} does not exist.")
        sys.exit(1)

    port.mkdir(parents=True, exist_ok=True)

    print(f"=== Port Cleaner ({'DRY RUN' if args.dry_run else 'LIVE'}) ===")
    print(f"Workdir: {workdir}")
    print(f"Port:    {port}")
    print(f"Sources: {', '.join(args.sources)}")
    print(f"TTL:     {args.ttl} days")
    print()

    # Phase 1: Consolidate scattered files
    print("--- Phase 1: Consolidate scattered files ---")
    scattered = collect_from_root(workdir, exclude_dirs, exclude_files)
    scattered += collect_from_sources(workdir, args.sources, exclude_files)
    if scattered:
        for f in sorted(scattered):
            print(move_to_port(f, port, args.dry_run))
        print(f"  Total: {len(scattered)} files consolidated")
    else:
        print("  No scattered files found.")

    print()

    # Phase 2: Purge old files
    print("--- Phase 2: Purge files older than TTL ---")
    purged = purge_old_files(port, args.ttl, args.dry_run)
    if purged:
        for line in purged:
            print(line)
        print(f"  Total: {len(purged)} files purged")
    else:
        print("  No files exceeded TTL.")

    # Summary
    remaining = sum(1 for f in port.iterdir() if f.is_file())
    print(f"\n  Port status: {remaining} files in {port}")
    print("=== Done ===")


if __name__ == "__main__":
    main()
