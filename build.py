# -*- coding: utf-8 -*-
"""Build script for Yihuan Redeem Code Collector"""
import PyInstaller.__main__
import os
import sys
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))
app_script = os.path.join(base_dir, "app.py")
data_file = os.path.join(base_dir, "codes_data.json")

# Use English name for build to avoid path encoding issues
app_name = "YihuanRedeemCollector"

if not os.path.exists(data_file):
    print("ERROR: codes_data.json not found!")
    sys.exit(1)

# Clean previous builds
for d in ["build", "dist"]:
    p = os.path.join(base_dir, d)
    if os.path.exists(p):
        shutil.rmtree(p, ignore_errors=True)

spec_file = os.path.join(base_dir, app_name + ".spec")
if os.path.exists(spec_file):
    os.remove(spec_file)

args = [
    app_script,
    f"--name={app_name}",
    "--onefile",
    "--windowed",
    "--clean",
    "--noconfirm",
    f"--add-data={data_file}{os.pathsep}.",
    "--hidden-import=tkinter",
    "--hidden-import=requests",
    "--hidden-import=bs4",
    "--hidden-import=json",
    "--hidden-import=threading",
    "--exclude-module=matplotlib",
    "--exclude-module=numpy",
    "--exclude-module=pandas",
    "--collect-all=tkinter",
]

print(f"Building {app_name}...")
print(f"Base dir: {base_dir}")
print(f"Python: {sys.executable} ({sys.version})")

PyInstaller.__main__.run(args)

# Rename output to Chinese name
src = os.path.join(base_dir, "dist", app_name + ".exe")
dst = os.path.join(base_dir, "dist", "异环兑换码搜集器.exe")
dst2 = os.path.join(base_dir, "异环兑换码搜集器.exe")
if os.path.exists(src):
    if os.path.exists(dst):
        os.remove(dst)
    os.rename(src, dst)
    # Also copy to project root for convenience
    shutil.copy2(dst, dst2)
    print(f"\n✅ Build complete!")
    print(f"   Output: {dst}")
    print(f"   Copy in project root: {dst2}")
else:
    print("ERROR: Build failed - exe not found")
