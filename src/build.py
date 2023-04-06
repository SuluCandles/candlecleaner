import subprocess
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.realpath(__file__))

# Set the paths to the icon files
#mac_icon_path = os.path.join(script_dir, 'resources', 'icon.icns')
win_icon_path = os.path.join(script_dir, 'icon.ico')

# Set the path to the main script
main_script_path = os.path.join(script_dir, 'candlecleaner.py')

# Set the path to the base repo directory
work_dir = os.path.dirname(script_dir).removesuffix("src")

work_dir = os.path.join(work_dir, 'build/')

# Build the application using PyInstaller
command = f'pyinstaller --onefile --add-data "{win_icon_path};." --windowed --name candlecleaner --icon "{win_icon_path}" --distpath "{work_dir}" --workpath "{work_dir}" --specpath {work_dir} {main_script_path}'
print(command)
subprocess.run(command, shell=True)