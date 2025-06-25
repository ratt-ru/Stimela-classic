import os
import sys
import subprocess

def main():
    script_path = os.path.join(os.path.dirname(__file__), 'cargo/cab/stimela_runscript')
    os.chmod(script_path, 0o755)  # ensure it's executable
    sys.exit(subprocess.call(["bash", script_path] + sys.argv[1:]))
