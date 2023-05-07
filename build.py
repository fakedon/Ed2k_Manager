import os

app_name = 'Ed2k_Manager'
build_command = "nuitka --standalone --mingw64 --enable-plugin=pyqt5 --show-memory --show-progress "
build_command += "--windows-disable-console "
build_command += "--windows-icon-from-ico=app/resource/images/link.png "
build_command += f"--output-filename={app_name}.exe  "
build_command += "entry.py"
# ========

print(build_command)
os.system(build_command)
