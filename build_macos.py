import os

app_name = 'Ed2k_Manager'
build_command = "nuitka3 --standalone  --enable-plugin=pyqt5 --show-memory --show-progress "
build_command += "--disable-console "
build_command += "--macos-app-icon==app/resource/images/link.png "
build_command += f" --macos-app-name=={app_name}  "
build_command += "entry.py"
# ========

print(build_command)
os.system(build_command)
