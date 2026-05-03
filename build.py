# -*- coding: utf-8 -*-
"""Build script for Multi-Game Redeem Code Collector v3.0"""
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

# Also clean parent dist since PyInstaller outputs there with --distpath ..
parent_dist = os.path.join(os.path.dirname(base_dir), "dist")
# Don't delete parent dist, just remove the target exe
target_exe = os.path.join(parent_dist, app_name + ".exe")
if os.path.exists(target_exe):
    os.remove(target_exe)

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
    f"--distpath={parent_dist}",
    f"--workpath={os.path.join(base_dir, 'build')}",
    f"--specpath={base_dir}",
    f"--add-data={data_file}{os.pathsep}.",
    "--hidden-import=tkinter",
    "--hidden-import=json",
    "--hidden-import=threading",
    "--exclude-module=matplotlib",
    "--exclude-module=numpy",
    "--exclude-module=pandas",
    "--collect-all=tkinter",
]

print(f"Building {app_name} v3.0 (Multi-Game)...")
print(f"Base dir: {base_dir}")
print(f"Python: {sys.executable} ({sys.version})")

PyInstaller.__main__.run(args)

# Check for output
if os.path.exists(target_exe):
    sz_mb = os.path.getsize(target_exe) / (1024 * 1024)
    print(f"\n✅ Build complete!")
    print(f"   Output: {target_exe} ({sz_mb:.1f} MB)")
else:
    print("ERROR: Build failed - exe not found")
