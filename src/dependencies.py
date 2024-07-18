import platform
import subprocess
import sys
import importlib

# This method installs the missing packages for the plugin without further user's action
def install_package(package_name):
    if importlib.util.find_spec(package_name) is None:
        try:
            importlib.import_module(package_name)
        except ImportError:
            if platform.system() == 'Windows':
                subprocess.call([sys.exec_prefix + '/python', "-m", 'pip', 'install', package_name])
            else:
                subprocess.call(['python3', '-m', 'pip', 'install', package_name]) 