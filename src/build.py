import subprocess
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--platform", help="the platform to build for", choices=["windows", "macos"], required=True)
args = parser.parse_args()
script_dir = os.path.dirname(os.path.realpath(__file__))
icon_path = os.path.join(script_dir, 'icon.ico')
main_script_path = os.path.join(script_dir, 'candlecleaner.py')
work_dir = os.path.dirname(script_dir)
build_dir = os.path.join(work_dir, 'build/')
os.makedirs(build_dir, exist_ok=True)
dist_dir = os.path.join(work_dir, 'dist/')
os.makedirs(dist_dir, exist_ok=True)

# Build the application using PyInstaller
if args.platform == "windows":
    command = f'pyinstaller --onefile --add-data "{icon_path};." --windowed --name candlecleaner --icon "{icon_path}" --distpath "{dist_dir}" --workpath "{build_dir}" --specpath "{build_dir}" {main_script_path}'
else:
    command = f'pyinstaller --onefile --add-data "{icon_path}:." --windowed --name candlecleaner --icon "{icon_path}" --distpath "{dist_dir}" --workpath "{build_dir}" --specpath "{build_dir}" {main_script_path}'
    
print(command)
subprocess.run(command, shell=True)
