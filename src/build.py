import subprocess
import os
import argparse

# Parse the command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--platform", help="the platform to build for", choices=["windows", "macos"], required=True)
args = parser.parse_args()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# Set the paths to the icon files
if args.platform == "windows":
    icon_path = os.path.join(script_dir, 'icon.ico')
else:
    icon_path = os.path.join(script_dir, 'icon.icns')

# Set the path to the main script
main_script_path = os.path.join(script_dir, 'candlecleaner.py')

# Set the path to the base repo directory
work_dir = os.path.dirname(script_dir).removesuffix("src")

work_dir = os.path.join(work_dir, 'build/')

# Build the application using PyInstaller
if args.platform == "windows":
    command = f'pyinstaller --onefile --add-data "{icon_path};." --windowed --name candlecleaner --icon "{icon_path}" --distpath "{work_dir}" --workpath "{work_dir}" --specpath {work_dir} {main_script_path}'
else:
    command = f'pyinstaller --onefile --add-data "{icon_path}:." --windowed --name candlecleaner --icon "{icon_path}" --distpath "{work_dir}" --workpath "{work_dir}" --specpath {work_dir} {main_script_path}'
print(command)
subprocess.run(command, shell=True)
