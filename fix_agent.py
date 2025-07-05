# fix_agent.py
import os
import subprocess

def run_black():
    print("Running black for auto-fix...")
    subprocess.run(['black', '.'])

if __name__ == "__main__":
    run_black()
