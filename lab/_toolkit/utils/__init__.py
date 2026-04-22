"""
File: __init__.py
Project: routine
Created: 2024-11-05 10:34:36
Author: Victor Cheng
Email: hi@victor42.work
Description:
"""

import importlib
import warnings

_submodules = [
    'path',
    'basic',
    'image',
    'video',
    'spreadsheet',
    'ocr',
    'api_telegram',
    'api_ai',
]

_skipped = []

for _mod_name in _submodules:
    try:
        _mod = importlib.import_module(f'.{_mod_name}', __name__)
    except Exception:
        _skipped.append(_mod_name)
        continue
    for _name in getattr(_mod, '__all__', [n for n in vars(_mod) if not n.startswith('_')]):
        globals()[_name] = getattr(_mod, _name)

if _skipped:
    warnings.warn(
        f"utils: skipped modules with missing dependencies: {', '.join(_skipped)}",
        stacklevel=2,
    )


def __getattr__(name):
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
