#
# Copyright (C) 2021-2022 by TeamYukki@Github, < https://github.com/TeamYukki >.
#
# This file is part of < https://github.com/TeamYukki/YukkiMusicBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/TeamYukki/YukkiMusicBot/blob/master/LICENSE >
#
# All rights reserved.
#

import glob
from os.path import dirname, isfile
from typing import List
from pathlib import Path

def __list_all_modules() -> List[str]:
    """
    Return module names (dotted) for all python files one directory deep under this file's folder.

    Behavior:
     - scans work_dir/*/*.py (one level down) to match original behavior
     - skips __init__.py
     - returns dotted module names like "subpkg.module" (no leading dot)
     - works on Windows and Linux
    """
    work_dir = Path(__file__).resolve().parent

    # change to work_dir.rglob("*.py") if you want recursive scanning at any depth
    py_paths = work_dir.glob("*/*.py")

    modules: List[str] = []
    for p in py_paths:
        if not p.is_file():
            continue
        if p.name == "__init__.py":
            continue

        # relative path to work_dir, remove suffix, convert path parts to dotted module name
        rel = p.relative_to(work_dir).with_suffix("")  # e.g. Path("subpkg/module")
        module_name = ".".join(rel.parts)              # -> "subpkg.module"
        modules.append(module_name)

    return modules

ALL_MODULES = sorted(__list_all_modules())
__all__ = ALL_MODULES + ["ALL_MODULES"]

'''def __list_all_modules():
    work_dir = dirname(__file__)
    mod_paths = glob.glob(work_dir + "/*/*.py")

    all_modules = [
        (((f.replace(work_dir, "")).replace("/", "."))[:-3])
        for f in mod_paths
        if isfile(f)
        and f.endswith(".py")
        and not f.endswith("__init__.py")
    ]

    return all_modules


ALL_MODULES = sorted(__list_all_modules())
__all__ = ALL_MODULES + ["ALL_MODULES"]'''
