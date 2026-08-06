import os
import shutil
import subprocess
import sys
import time
import ctypes
from pathlib import Path


UPDATE_FILES = (
    "main.py",
    "updater.py",
    "README.md",
    "start.bat",
    "启动写信翻译.bat",
    "启动写信翻译.vbs",
)


def wait_for_process(pid, timeout_ms=15000):
    if os.name == "nt":
        synchronize = 0x00100000
        handle = ctypes.windll.kernel32.OpenProcess(synchronize, False, pid)
        if handle:
            ctypes.windll.kernel32.WaitForSingleObject(handle, timeout_ms)
            ctypes.windll.kernel32.CloseHandle(handle)
        return
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        try:
            os.kill(pid, 0)
        except OSError:
            return
        time.sleep(0.1)


def main():
    if len(sys.argv) != 4:
        return 2
    pid = int(sys.argv[1])
    source = Path(sys.argv[2]).resolve()
    destination = Path(sys.argv[3]).resolve()
    wait_for_process(pid)
    for name in UPDATE_FILES:
        source_file = source / name
        if source_file.is_file():
            shutil.copy2(source_file, destination / name)
    pythonw = Path(sys.executable).with_name("pythonw.exe")
    executable = pythonw if pythonw.exists() else Path(sys.executable)
    subprocess.Popen([str(executable), str(destination / "main.py")],
                     cwd=destination,
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
