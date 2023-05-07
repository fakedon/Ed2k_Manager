import os

app_name = 'Ed2k_Manager'
build_command = "pyinstaller -w --clean --noconfirm "
# build_command += "--disable-console --onefile --macos-create-app-bundle "
# build_command += "--macos-app-icon=app/resource/images/link.png "
# build_command += f" --macos-app-name={app_name}  "
build_command += "entry.py"
# ========

print(build_command)
os.system(build_command)

# FATAL: Failed to download 'https://nuitka.net/ccache/v4.2.1/ccache-4.2.1.zip'
# due to '<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1131)>'. 
# Contents should manually be copied to '/Users/wanning/Library/Caches/Nuitka/downloads/ccache/v4.2.1/ccache-4.2.1.zip'.
