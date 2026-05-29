Created At: 2026-05-26T16:21:14Z
Completed At: 2026-05-26T16:21:14Z
File Path: `file:///c:/Users/Accesorizate1/Downloads/Eyemax/.venv/Lib/site-packages/flet_desktop/__init__.py`
Total Lines: 462
Total Bytes: 15484
Showing lines 1 to 462
The following code has been modified to include a line number before every line, in the format: <line_number>: <original_line>. Please note that any changes targeting the original code should remove the line number, colon, and leading space.
1: import asyncio
2: import ctypes
3: import ctypes.util
4: import logging
5: import os
6: import shutil
7: import signal
8: import stat
9: import subprocess
10: import sys
11: import tarfile
12: import tempfile
13: import urllib.request
14: import zipfile
15: from pathlib import Path
16: 
17: import flet_desktop
18: import flet_desktop.version
19: from flet.utils import (
20:     get_arch,
21:     is_linux,
22:     is_macos,
23:     is_windows,
24:     random_string,
25:     safe_tar_extractall,
26:     safe_zip_extractall,
27: )
28: 
29: logger = logging.getLogger(flet_desktop.__name__)
30: 
31: # Supported Linux build targets ordered by glibc version.
32: # Each entry maps a minimum glibc (major, minor) to a distro_id used in
33: # release artifact filenames.
34: _GLIBC_DISTRO_TABLE = [
35:     ((2, 28), "debian10"),
36:     ((2, 31), "ubuntu20.04"),
37:     ((2, 35), "ubuntu22.04"),
38:     ((2, 36), "debian12"),
39:     ((2, 39), "ubuntu24.04"),
40: ]
41: 
42: 
43: def get_package_bin_dir():
44:     """
45:     Return the directory that contains bundled desktop runtime artifacts.
46: 
47:     The directory may contain platform-specific executables or compressed
48:     archives used to provision the desktop client at runtime.  When the
49:     package is installed without bundled binaries the directory will be
50:     empty and the download path is used instead.
51:     """
52: 
53:     return str(Path(__file__).parent.joinpath("app"))
54: 
55: 
56: def __get_desktop_flavor():
57:     """
58:     Return the desktop client flavor to use: `
<truncated 14152 bytes>
16: 
417:         logger.info(f"page_url: {page_url}")
418:         logger.info(f"pid_file: {pid_file}")
419:         args = ["open", str(app_path), "-n", "-W", "--args", page_url, pid_file]
420: 
421:     elif is_linux():
422:         app_path = None
423:         # 1. Try loading Flet client built with the latest run of `flet build`
424:         build_linux = os.path.join(os.getcwd(), "build", "linux")
425:         if os.path.exists(build_linux):
426:             for f in os.listdir(build_linux):
427:                 ef = os.path.join(build_linux, f)
428:                 if os.path.isfile(ef) and stat.S_IXUSR & os.stat(ef)[stat.ST_MODE]:
429:                     app_path = ef
430: 
431:         # 2. Check FLET_VIEW_PATH (developer mode)
432:         if not app_path:
433:             flet_view_path = os.environ.get("FLET_VIEW_PATH")
434:             if flet_view_path:
435:                 exe_path = str(Path(flet_view_path).joinpath("flet"))
436:                 if os.path.isfile(exe_path):
437:                     logger.info(
438:                         f"Flet View is set via FLET_VIEW_PATH: {flet_view_path}"
439:                     )
440:                     app_path = exe_path
441:                 else:
442:                     logger.warning(
443:                         f"FLET_VIEW_PATH set to {flet_view_path} "
444:                         f"but flet executable not found there"
445:                     )
446:             if not app_path:
447:                 # 3. Use cached or downloaded client
448:                 cache_dir = ensure_client_cached()
449:                 app_path = str(cache_dir.joinpath("flet", "flet"))
450: 
451:         args = [str(app_path), page_url, pid_file]
452: 
453:     flet_env = {**os.environ}
454: 
455:     if assets_dir:
456:         args.append(assets_dir)
457: 
458:     if hidden:
459:         flet_env["FLET_HIDE_WINDOW_ON_START"] = "true"
460: 
461:     return args, flet_env, pid_file
462: 
The above content shows the entire, complete file contents of the requested file.
