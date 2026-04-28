"""保证 ``src`` 目录在测试导入路径上。"""
from __future__ import annotations

import os
import sys

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.normpath(os.path.join(_THIS_DIR, os.pardir, "src"))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
