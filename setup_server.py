"""
Setup script for compiling PhantomStrike Server using cx_Freeze
"""

from cx_Freeze import setup, Executable
import sys

# Dependencies are automatically detected, but it might be fine tuned.
build_exe_options = {
    "packages": ["socket", "threading", "logging", "configparser", "os", "signal", "sys", "datetime"],
    "excludes": ["tkinter", "unittest", "pydoc", "doctest", "argparse"],
    "include_files": ["server_config.ini"]
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Console"

setup(
    name="PhantomStrike-Server",
    version="1.0.0",
    description="PhantomStrike Server Application",
    options={"build_exe": build_exe_options},
    executables=[Executable("Server.py", base=base, target_name="PhantomStrike-Server.exe")]
)
