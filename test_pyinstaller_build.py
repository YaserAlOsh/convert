import os
import subprocess
import sys
import shutil

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode(), error.decode(), process.returncode

def test_pyinstaller_build():
    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')

    # Run PyInstaller
    print("Building with PyInstaller...")
    output, error, return_code = run_command("pyinstaller gui.spec")
    
    if return_code != 0:
        print("PyInstaller build failed:")
        print(error)
        return False

    # Find the executable
    if sys.platform.startswith('win'):
        exe_path = 'dist/od_convert/Object Detection Converter.exe'
    elif sys.platform.startswith('darwin'):
        exe_path = 'dist/od_convert/Object Detection Converter.app/Contents/MacOS/Object Detection Converter'
    else:
        exe_path = 'dist/od_convert/Object Detection Converter'

    if not os.path.exists(exe_path):
        print(f"Executable not found at expected path: {exe_path}")
        return False

    # Test running the executable
    print("Testing the executable...")
    output, error, return_code = run_command(exe_path)
    
    if return_code != 0:
        print("Executable test failed:")
        print(error)
        return False

    print("PyInstaller build and test successful!")
    return True

if __name__ == "__main__":
    success = test_pyinstaller_build()
    sys.exit(0 if success else 1) 