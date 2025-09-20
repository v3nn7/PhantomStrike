"""
Setup script for compiling PhantomStrike Client using cx_Freeze
"""

from cx_Freeze import setup, Executable
import sys
import os

# Dependencies are automatically detected, but it might be fine tuned.
build_exe_options = {
    "packages": ["socket", "os", "sys", "logging", "configparser", "platform", "time", "datetime"],
    "excludes": ["tkinter", "unittest", "pydoc", "doctest", "argparse"],
    "include_files": ["client_config.ini", "core/", "functions/"]
}

# GUI applications require a different base on Windows
base = None
if sys.platform == "win32":
    base = "Console"

# Change to client directory for proper path resolution
os.chdir(os.path.dirname(os.path.abspath(__file__)))

setup(
    name="PhantomStrike-Client",
    version="1.0.0",
    description="PhantomStrike Client Application",
    options={"build_exe": build_exe_options},
    executables=[Executable("core/client_main.py", base=base, target_name="PhantomStrike-Client.exe")]
)
